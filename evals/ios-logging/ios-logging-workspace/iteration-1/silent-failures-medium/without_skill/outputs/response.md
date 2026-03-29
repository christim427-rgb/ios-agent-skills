# Combine Search Pipeline Stops After First Error

## The Problem

The pipeline works once but then stops responding to subsequent changes in `searchQuery`. The root cause is the placement of `.replaceError(with: [])` — it is applied to the **outer** publisher chain rather than to each **inner** publisher created inside `flatMap`.

## Why It Breaks

In Combine, when a publisher emits a `.failure`, the entire subscription terminates. The operator `.replaceError(with:)` converts the failure into a final value and then sends `.finished`, which **completes the stream**. Once completed, the pipeline is dead — no further values from `$searchQuery` will be processed.

Here is the problematic code:

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .flatMap { query in
        APIService.search(query)
    }
    .replaceError(with: [])   // <-- Kills the entire pipeline on first error
    .assign(to: &$results)
```

The sequence of events:

1. User types a query, `$searchQuery` emits a value.
2. `.debounce` waits 0.3 seconds, then forwards it.
3. `.flatMap` subscribes to `APIService.search(query)`.
4. If the API call fails, the error propagates to `.replaceError(with: [])`.
5. `.replaceError` emits `[]` and then sends `.finished`.
6. The entire chain completes. Future changes to `$searchQuery` are ignored.

## The Fix

Move `.replaceError(with: [])` **inside** the `flatMap` closure so that each individual API call handles its own errors without killing the outer pipeline:

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .flatMap { query in
        APIService.search(query)
            .replaceError(with: [])   // <-- Error handled per-request
    }
    .assign(to: &$results)
```

Now each inner publisher independently handles its errors. The outer pipeline never sees a failure, so it stays alive indefinitely and continues to react to new values from `$searchQuery`.

## Alternative: Using `catch` for Logging

If you want visibility into failures, use `catch` instead of `replaceError` so you can log the error:

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .flatMap { query in
        APIService.search(query)
            .catch { error -> Just<[SearchResult]> in
                print("Search failed: \(error)")
                return Just([])
            }
    }
    .assign(to: &$results)
```

## Alternative: Surfacing Errors to the UI

If you want the UI to display error states rather than silently returning empty results, encode the result as a `Result` type:

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .flatMap { query in
        APIService.search(query)
            .map { Result<[SearchResult], Error>.success($0) }
            .catch { Just(.failure($0)) }
    }
    .assign(to: &$searchResult)  // where searchResult is @Published var of Result type
```

## General Rule

In any long-lived Combine pipeline — UI bindings, real-time streams, user input processing — **never let errors propagate to the outer subscription**. Always contain errors within the `flatMap` (or `switchToLatest`) scope so the outer stream survives.

The same principle applies to `switchToLatest`:

```swift
$searchQuery
    .debounce(for: .seconds(0.3), scheduler: DispatchQueue.main)
    .map { query in
        APIService.search(query)
            .replaceError(with: [])  // Handle error inside map, before switchToLatest
    }
    .switchToLatest()
    .assign(to: &$results)
```

## Key Takeaway

Combine's error model is terminal: once a failure reaches a subscriber, the subscription is cancelled. Operators like `replaceError` and `catch` convert the failure into a value + completion, but the completion still ends the stream. The fix is always to handle errors at the innermost scope possible — inside `flatMap`, `map` + `switchToLatest`, or similar operators — so the outer pipeline remains active.
