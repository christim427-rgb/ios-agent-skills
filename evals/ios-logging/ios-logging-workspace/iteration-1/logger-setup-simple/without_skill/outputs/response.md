# Replacing print() with Proper Logging in iOS

## Why print() Is Problematic

Using `print()` throughout your iOS app has several drawbacks:

- **No log levels** -- everything is treated equally, making it hard to filter noise from critical issues.
- **No metadata** -- no timestamps, source file info, or category tagging.
- **Stripped in Release builds only if you do it manually** -- `print()` still executes in production, which can impact performance and leak information.
- **Not visible in Console.app** -- you cannot use Apple's Console app to inspect logs from a device or simulator when using `print()`.
- **No integration with system diagnostics** -- crash reports and sysdiagnose bundles do not capture `print()` output.

## What to Use Instead

### 1. os.Logger (iOS 14+ / macOS 11+) -- Recommended

Apple's unified logging system via the `os` framework is the gold standard for iOS logging. Use the `Logger` struct:

```swift
import os

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.example.myapp"

    static let networking = Logger(subsystem: subsystem, category: "networking")
    static let ui = Logger(subsystem: subsystem, category: "ui")
    static let dataStore = Logger(subsystem: subsystem, category: "dataStore")
}
```

Usage:

```swift
Logger.networking.debug("Starting request to \(url)")
Logger.networking.info("Response received: \(statusCode)")
Logger.networking.error("Request failed: \(error.localizedDescription)")
```

**Key advantages of Logger:**

- **Log levels**: `.debug`, `.info`, `.notice`, `.error`, `.fault`, `.critical` -- lets you filter by severity.
- **Privacy by default**: String interpolation is redacted in release builds unless you opt in with `\(value, privacy: .public)`. This prevents accidentally logging sensitive user data.
- **High performance**: The system uses a lazy formatting approach -- messages are not fully rendered unless someone is actually reading the logs.
- **Visible in Console.app**: You can filter by subsystem and category in real time on a connected device.
- **Persisted based on level**: Debug messages are ephemeral (memory only), while error and fault messages are persisted to disk and included in sysdiagnose.
- **Structured categories**: Subsystem + category gives you fine-grained filtering.

### 2. os_log (iOS 10+) -- Legacy Unified Logging

If you need to support iOS versions earlier than 14, use `os_log` directly:

```swift
import os.log

let networkLog = OSLog(subsystem: "com.example.myapp", category: "networking")

os_log("Request started for %{public}@", log: networkLog, type: .info, url.absoluteString)
os_log("Request failed: %{public}@", log: networkLog, type: .error, error.localizedDescription)
```

This uses printf-style formatting rather than Swift string interpolation. The `Logger` struct (option 1) is the modern Swift-friendly wrapper around this.

### 3. OSSignposter (iOS 16+) -- For Performance Instrumentation

If your logging is specifically about measuring performance, use `OSSignposter` to create signpost intervals that appear in Instruments:

```swift
import os

let signposter = OSSignposter(logger: Logger.networking)

func fetchData() async throws -> Data {
    let signpostID = signposter.makeSignpostID()
    let state = signposter.beginInterval("fetchData", id: signpostID)
    defer { signposter.endInterval("fetchData", state) }

    // ... perform work
}
```

## Recommended Setup Pattern

Here is a practical pattern for organizing logging in your app:

```swift
import os

enum Log {
    static let subsystem = Bundle.main.bundleIdentifier ?? "com.example.app"

    static let general = Logger(subsystem: subsystem, category: "general")
    static let network = Logger(subsystem: subsystem, category: "network")
    static let storage = Logger(subsystem: subsystem, category: "storage")
    static let auth = Logger(subsystem: subsystem, category: "auth")
    static let ui = Logger(subsystem: subsystem, category: "ui")
}
```

Then throughout your code:

```swift
// Debug-level (not persisted, only visible when actively streaming logs)
Log.network.debug("Headers: \(headers, privacy: .private)")

// Info-level (persisted only during log collect)
Log.network.info("GET \(url, privacy: .public) started")

// Error-level (persisted to disk)
Log.network.error("Request failed: \(error, privacy: .public)")

// Fault-level (persisted, indicates a bug in your code)
Log.storage.fault("Core Data save failed unexpectedly: \(error)")
```

## Log Level Guide

| Level | Use Case | Persistence |
|-------|----------|-------------|
| `.debug` | Detailed development info, verbose output | Memory only, not persisted |
| `.info` | Helpful runtime info, flow tracking | Persisted only during log collection |
| `.notice` | Default level, notable events | Persisted up to a storage limit |
| `.error` | Errors that are recoverable | Persisted to disk |
| `.fault` | Bugs, programming errors, unrecoverable issues | Persisted to disk |

## Migration Strategy

1. **Create your Logger extensions** with appropriate categories for your app's modules.
2. **Replace print() calls one module at a time**, choosing the correct log level for each message.
3. **Use privacy modifiers** -- mark user-facing or sensitive data as `.private` (the default), and only use `.public` for data that is safe to appear in logs on any device.
4. **Remove any custom logging wrappers** that reinvent what the unified logging system already provides.
5. **Test with Console.app** -- connect your device, filter by your app's subsystem, and verify logs appear at the correct levels.

## Common Mistakes to Avoid

- **Do not use `NSLog`** -- it is slower than unified logging, always persists, and uses the legacy ASL system. It also logs to stderr, which has performance overhead.
- **Do not wrap Logger in a custom class that uses string concatenation** -- this defeats the lazy evaluation optimization. Let the system handle string interpolation natively.
- **Do not log sensitive data as `.public`** -- passwords, tokens, PII, and similar data should remain private (redacted) in production logs.
- **Do not use `.fault` for expected errors** -- reserve it for conditions that indicate a bug in your code. Use `.error` for expected failure paths like network timeouts.
