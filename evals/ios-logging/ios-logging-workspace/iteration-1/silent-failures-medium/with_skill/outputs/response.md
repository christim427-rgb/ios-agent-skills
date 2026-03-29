# Diagnosis: Combine Pipeline Dies After First API Error

## The Problem

Your pipeline stops responding after the first API error because of where `.replaceError(with: [])` is placed. When `APIService.search(query)` returns a failure, that error propagates up to the outer pipeline level. `.replaceError(with: [])` handles it by changing the publisher's `Failure` type to `Never` -- but in doing so, it **terminates the entire pipeline**. The Combine contract states that once a publisher emits a `.failure` completion, it is finished permanently. No further values from `$searchQuery` will ever be processed.

This is why the search works exactly once (or works fine until the first network error) and then goes completely dead.

## The Fix: Move Error Handling Inside `flatMap`

Error recovery must happen **inside the `flatMap` closure**, so that each individual API call handles its own errors without killing the outer subscription to `$searchQuery`.

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .flatMap { query in
        APIService.search(query)
            .retry(2)
            .catch { error -> Just<[Result]> in
                Logger.networking.error(
                    "Search failed for query: \(error.localizedDescription, privacy: .public)"
                )
                ErrorReporter.shared.recordNonFatal(error, context: ["query": query])
                return Just([])
            }
    }
    .receive(on: DispatchQueue.main)
    .assign(to: &$results)
```

## Why This Works

- Each call to `APIService.search(query)` is now individually wrapped with `.catch`. If that single request fails, `.catch` converts the failure into `Just([])` (an empty array), which completes normally.
- The outer pipeline (driven by `$searchQuery`) never sees a failure. It remains alive and continues to react to new search queries.
- `.retry(2)` gives transient network errors a chance to recover before falling through to the catch.
- The error is logged with `os.Logger` and reported to a crash/analytics SDK so you have production visibility into search failures, rather than silently swallowing them.

## Key Principle

In Combine, a failure completion is terminal -- the publisher is done forever. When you have a long-lived pipeline (like one driven by a `@Published` property), you must never let errors reach the outer pipeline. Always contain errors inside `flatMap` (or `map`/`tryMap` paired with inner `.catch`) so the outer subscription stays alive.
