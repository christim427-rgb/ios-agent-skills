# Error Handling Analysis

This code has two compounding silent failure patterns that will make production debugging nearly impossible.

## Problem 1: `try?` erases all diagnostic information

```swift
let profile = try? await api.fetchProfile(userId: currentUser.id)
```

`try?` converts any thrown error into `nil`, destroying the error type, message, and stack context entirely. If this call fails due to a 401 unauthorized response, a network timeout, a DNS failure, or a server 500, the result is the same: `self.profile` is set to `nil`. You will never know *why* it failed. This is the single most dangerous convenience in Swift for production observability.

`try?` is only acceptable for genuinely irrelevant best-effort operations (temp file cleanup, optional cache reads, cosmetic prefetches). Fetching a user profile is a user-facing operation where failure absolutely matters -- it must use `do/catch`.

## Problem 2: `Task {}` swallows errors silently

`Task.init` is `@discardableResult`, so the compiler never warns when you ignore the returned `Task<Void, Error>`. Even if `try?` were replaced with `try`, any thrown error inside a bare `Task {}` without a `do/catch` would be silently discarded -- no crash, no log, nothing. The two patterns together form a double layer of silence.

## Problem 3: No observability at all

There is no logging (`os.Logger`), no crash reporting (`ErrorReporter`), and no user-facing error state. When this fails in production across thousands of devices, you cannot attach a debugger. Without remote logging, a 15-minute investigation becomes a 3-day mystery.

## Corrected Version

```swift
func loadUserProfile() {
    Task {
        do {
            let profile = try await api.fetchProfile(userId: currentUser.id)
            self.profile = profile
        } catch is CancellationError {
            // Task was cancelled (e.g., view disappeared) -- normal lifecycle, not a failure
        } catch {
            Logger.networking.error(
                "Failed to load profile for user \(currentUser.id, privacy: .private): \(error.localizedDescription, privacy: .public)"
            )
            ErrorReporter.shared.recordNonFatal(error, context: [
                "operation": "loadUserProfile",
                "userId": currentUser.id
            ])
            self.loadError = error // Surface error state to the UI
        }
    }
}
```

### What changed and why

1. **`try?` replaced with `do/catch`** -- errors are now caught with their full type, message, and context preserved.
2. **`CancellationError` handled separately** -- if this runs inside a SwiftUI `.task` modifier, the view disappearing will throw `CancellationError`. That is normal lifecycle behavior, not a failure. Reporting it as an error creates noise in your crash dashboard.
3. **`Logger.networking.error()`** -- logs the failure to the unified logging system with privacy annotations (`privacy: .private` on the user ID to avoid PII in logs, `privacy: .public` on the error description so it is readable in production log archives).
4. **`ErrorReporter.shared.recordNonFatal()`** -- reports the error to your crash reporting SDK (Sentry, Crashlytics, etc.) so it appears in your remote dashboard and can be investigated without a debugger.
5. **`self.loadError = error`** -- exposes the error to the UI layer so the user sees a meaningful failure state instead of a blank or perpetually loading screen.

### The rule

Every `Task {}` containing `try` must have an explicit `do/catch` with observability inside it. Every caught error must be logged with `os.Logger` AND reported to a remote crash/analytics service. No `try?` on network, persistence, auth, or user-facing operations.
