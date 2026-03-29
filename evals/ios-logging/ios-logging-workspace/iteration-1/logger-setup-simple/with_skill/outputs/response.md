# Replace print() with os.Logger

You should replace `print()` with Apple's `os.Logger` API (available since iOS 14). Here is why and how.

## Why print() Is Wrong for Production

`print()` has three critical problems in a shipping app:

1. **No log levels.** Every message is the same priority. You cannot filter noise from real errors, and you cannot search for just errors in Console.app or a log archive.
2. **No privacy controls.** `print()` dumps raw strings, including user emails, tokens, or PII, directly into the log stream. Apple's logging system redacts dynamic values by default, which is essential for GDPR/CCPA compliance.
3. **No persistence or structure.** `print()` output goes to stdout and vanishes. `os.Logger` messages are persisted at configurable levels, tagged with subsystem and category, and can be collected in sysdiagnose bundles or streamed from Xcode's structured console.

Additionally, `os.Logger` debug-level messages are effectively free in production -- the compiler optimizes away message creation when nobody is streaming. You can leave verbose debug logging in place without any performance cost.

## Step 1: Create Logger Extensions

Define static loggers per domain area so every call site has a clear, filterable category:

```swift
import os

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier!

    static let networking = Logger(subsystem: subsystem, category: "Networking")
    static let auth       = Logger(subsystem: subsystem, category: "Authentication")
    static let database   = Logger(subsystem: subsystem, category: "Database")
    static let ui         = Logger(subsystem: subsystem, category: "UI")
    static let payments   = Logger(subsystem: subsystem, category: "Payments")
    static let lifecycle  = Logger(subsystem: subsystem, category: "Lifecycle")
}
```

Add or remove categories to match your app's domain areas.

## Step 2: Choose the Right Log Level

| Level | Persisted? | Use for |
|-------|-----------|---------|
| `.debug` | No (memory only, discarded if not streaming) | Development tracing, hot-path diagnostics |
| `.info` | Memory only (captured when faults occur) | Helpful but non-critical context |
| `.notice` | Yes (persisted to disk) | Important operational information |
| `.error` | Always persisted | Recoverable error conditions |
| `.fault` | Always persisted + process chain info | Bugs, unrecoverable system failures |

## Step 3: Always Add Privacy Annotations

This is the most important feature. Dynamic strings are redacted by default in production logs -- they show as `<private>` unless you explicitly mark them. Numeric types are public by default.

```swift
// BAD -- no privacy annotation, useless in production
Logger.networking.error("Request to \(url) failed for user \(userId)")
// Production output: "Request to <private> failed for user <private>"

// GOOD -- explicit privacy annotations
Logger.networking.error("Request to \(url.absoluteString, privacy: .public) failed for user \(userId, privacy: .private(mask: .hash))")
// Production output: "Request to /api/users failed for user <mask.hash: 'uZiZmp5vMXG4evDH=='>"
```

Use this decision guide:

- **`.public`** -- URL paths, error descriptions, status codes, operation names. Safe for anyone with log access.
- **`.private`** -- User IDs, emails, names. Redacted in production.
- **`.private(mask: .hash)`** -- Same as private, but produces a consistent hash so you can correlate events for the same user across log entries without exposing the actual value.
- **`.sensitive`** -- Passwords, tokens, API keys. Always redacted, even during development. (Better yet, do not log secrets at all.)
- **No annotation on strings** -- Defaults to `<private>` in production. Always specify explicitly.

## Step 4: Replace print() Calls

Here is how common `print()` patterns map to Logger:

| Before | After |
|--------|-------|
| `print("Loading data...")` | `Logger.networking.debug("Loading data...")` |
| `print("Error: \(error)")` | `Logger.networking.error("Failed: \(error.localizedDescription, privacy: .public)")` |
| `print("User: \(user.email)")` | `Logger.auth.info("User: \(user.email, privacy: .private(mask: .hash))")` |
| `print("Response: \(data)")` | `Logger.networking.debug("Response size: \(data.count, privacy: .public) bytes")` |
| `debugPrint(object)` | `Logger.ui.debug("State: \(String(describing: object), privacy: .private)")` |

## Step 5: Pair with a Crash Reporting SDK

Logger alone only writes to the device's local log store. For production observability, pair it with a remote error reporting service. In every `catch` block, do both:

```swift
catch {
    // 1. Structured local log
    Logger.networking.error("Request failed: \(error.localizedDescription, privacy: .public)")

    // 2. Report to remote crash SDK (Sentry, Crashlytics, etc.)
    ErrorReporter.shared.recordNonFatal(error, context: ["operation": "fetchUserProfile"])
}
```

This ensures errors are visible both locally (for live debugging in Console.app or Xcode) and remotely (for monitoring across your user base).

## Summary

- Use `os.Logger` with subsystem/category extensions for structured, filterable logs.
- Always specify privacy annotations on dynamic values.
- Choose the right log level so errors are persisted and debug messages are free.
- Pair Logger with a remote crash reporting SDK so production errors are never invisible.
- Reserve `print()` for unit tests, playgrounds, and throwaway scripts only.
