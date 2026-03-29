# Adding Error Handling with Crash Reporting to a Network Call

The original function has three silent failure patterns:

1. **URLSession does not throw for HTTP errors** -- a 500 response returns `(Data, URLResponse)` without throwing, so the caller silently receives garbage data or a decode failure with no context about the actual HTTP status.
2. **No logging** -- if this function throws (transport error or decode error), the caller may catch it with `try?` or a bare `catch`, and the error vanishes.
3. **No crash reporting** -- even if someone logs the error locally, no remote service is notified, so production failures are invisible.

## Step 1: Define the ErrorReporter Protocol

Never call Sentry/Crashlytics APIs directly throughout your codebase. Use a protocol-based abstraction:

```swift
protocol ErrorReporter: Sendable {
    func recordNonFatal(_ error: Error, context: [String: Any])
    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?)
    func setUserID(_ userID: String?)
    func setCustomKey(_ key: String, value: Any)
    func log(_ message: String)
}

enum BreadcrumbLevel: String, Sendable {
    case debug, info, warning, error, fatal
}
```

Provide a concrete implementation wrapping your chosen SDK (Sentry, Crashlytics, or a composite). See below for a Sentry example:

```swift
import SentrySwift

final class SentryErrorReporter: ErrorReporter {
    func recordNonFatal(_ error: Error, context: [String: Any]) {
        SentrySDK.capture(error: error) { scope in
            for (key, value) in context {
                scope.setExtra(value: value, key: key)
            }
        }
    }

    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?) {
        let crumb = Breadcrumb(level: sentryLevel(level), category: category)
        crumb.message = message
        crumb.data = data
        SentrySDK.addBreadcrumb(crumb)
    }

    func setUserID(_ userID: String?) {
        SentrySDK.configureScope { scope in
            scope.setUser(userID.map { User(userId: $0) })
        }
    }

    func setCustomKey(_ key: String, value: Any) {
        SentrySDK.configureScope { scope in
            scope.setExtra(value: value, key: key)
        }
    }

    func log(_ message: String) {
        SentrySDK.addBreadcrumb(Breadcrumb(level: .info, category: "log"))
    }

    private func sentryLevel(_ level: BreadcrumbLevel) -> SentryLevel {
        switch level {
        case .debug:   return .debug
        case .info:    return .info
        case .warning: return .warning
        case .error:   return .error
        case .fatal:   return .fatal
        }
    }
}
```

Make the shared instance available:

```swift
extension ErrorReporter where Self == SentryErrorReporter {
    static var shared: ErrorReporter { SentryErrorReporter() }
}
// Or use a simple singleton pattern:
enum ErrorReporterProvider {
    static let shared: ErrorReporter = SentryErrorReporter()
}
```

## Step 2: Set Up the Logger

Use `os.Logger` with a subsystem and category -- never `print()`:

```swift
import os

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.app"

    static let networking = Logger(subsystem: subsystem, category: "networking")
}
```

## Step 3: Define a Typed Network Error

```swift
enum NetworkError: LocalizedError {
    case invalidResponse
    case httpError(statusCode: Int, data: Data)
    case decodingFailed(underlying: DecodingError, data: Data)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "Response was not a valid HTTP response."
        case .httpError(let statusCode, _):
            return "HTTP error \(statusCode)."
        case .decodingFailed(let underlying, _):
            return "Decoding failed: \(underlying.localizedDescription)"
        }
    }
}
```

## Step 4: Rewrite the Function with Full Observability

```swift
func fetchProducts() async throws -> [Product] {
    // Breadcrumb before the risky operation -- answers "what was the user doing?"
    ErrorReporterProvider.shared.addBreadcrumb(
        message: "Fetching products",
        category: "networking",
        level: .info,
        data: ["url": productsURL.absoluteString]
    )

    let data: Data
    let response: URLResponse

    do {
        (data, response) = try await URLSession.shared.data(from: productsURL)
    } catch {
        // Transport-level failure: no network, DNS failure, timeout, etc.
        Logger.networking.error(
            "Product fetch transport error: \(error.localizedDescription, privacy: .public)"
        )
        ErrorReporterProvider.shared.recordNonFatal(error, context: [
            "operation": "fetchProducts",
            "url": productsURL.absoluteString,
            "phase": "transport"
        ])
        throw error
    }

    // URLSession does NOT throw for HTTP errors -- a 500 returns successfully.
    // You must validate the status code explicitly.
    guard let httpResponse = response as? HTTPURLResponse else {
        let error = NetworkError.invalidResponse
        Logger.networking.error("Invalid response type for product fetch")
        ErrorReporterProvider.shared.recordNonFatal(error, context: [
            "operation": "fetchProducts",
            "url": productsURL.absoluteString
        ])
        throw error
    }

    guard (200...299).contains(httpResponse.statusCode) else {
        let error = NetworkError.httpError(statusCode: httpResponse.statusCode, data: data)
        Logger.networking.error(
            "Product fetch HTTP \(httpResponse.statusCode, privacy: .public) for \(productsURL.path, privacy: .public)"
        )
        ErrorReporterProvider.shared.recordNonFatal(error, context: [
            "operation": "fetchProducts",
            "url": productsURL.absoluteString,
            "statusCode": httpResponse.statusCode,
            "phase": "http_status"
        ])
        throw error
    }

    // Decode with error context preserved
    do {
        return try JSONDecoder().decode([Product].self, from: data)
    } catch let decodingError as DecodingError {
        Logger.networking.error(
            "Product decode failed: \(decodingError.localizedDescription, privacy: .public)"
        )
        ErrorReporterProvider.shared.recordNonFatal(decodingError, context: [
            "operation": "fetchProducts",
            "url": productsURL.absoluteString,
            "phase": "decoding",
            "dataSize": data.count,
            "responseSnippet": String(data: data.prefix(512), encoding: .utf8) ?? "<binary>"
        ])
        throw NetworkError.decodingFailed(underlying: decodingError, data: data)
    }
}
```

## What Changed and Why

### 1. HTTP status code validation

The original code ignored the `response` entirely. URLSession only throws for transport-level failures (no network, DNS, timeout). An HTTP 401, 403, 404, or 500 all return `(Data, URLResponse)` successfully. Without the `guard` on `httpResponse.statusCode`, the function would attempt to decode an error body as `[Product]`, producing a confusing `DecodingError` instead of a clear HTTP error.

### 2. Breadcrumb before the operation

`addBreadcrumb` records a timestamped event that is buffered locally and attached to the next error or crash report. If this function or anything after it fails, the crash report will show "Fetching products" in the breadcrumb trail, answering "what was the user doing before this broke?"

### 3. `os.Logger` with privacy annotations

Every error is logged through `Logger.networking.error()` using `privacy: .public` only for non-sensitive data (status codes, URL paths). This replaces `print()` which is invisible on production devices. Logger output is integrated with the unified logging system, persisted at `.error` level, and searchable with Console.app or `log stream`.

### 4. `ErrorReporter.recordNonFatal()` with structured context

Every error is reported to the remote crash SDK with structured context (operation name, URL, phase, status code, data size). Non-fatal errors affect 10-30% of sessions silently -- far more than crashes. This is the primary tool for detecting production issues.

### 5. Separate catch blocks for transport vs. decoding

The original single `try` chain made it impossible to distinguish "network is down" from "server returned unexpected JSON". The rewritten version catches transport errors and decoding errors separately, with different context metadata for each.

### 6. Typed `NetworkError` enum

Instead of re-throwing raw system errors, the function wraps failures in domain-specific types. This lets callers pattern-match on the error kind (e.g., show "no network" vs. "server error" vs. "update the app" for different cases).

## Calling This Function Safely

When calling from a SwiftUI `.task` modifier, always distinguish `CancellationError` from real errors:

```swift
.task {
    do {
        products = try await fetchProducts()
    } catch is CancellationError {
        // View disappeared -- expected lifecycle, do not report
    } catch {
        loadError = error
        // fetchProducts already reported to ErrorReporter,
        // so no need to call recordNonFatal again here.
        // Just update UI state.
    }
}
```

When calling from an unstructured `Task {}`, always wrap in `do/catch` -- `Task.init` is `@discardableResult` and silently discards thrown errors:

```swift
func loadData() {
    Task {
        do {
            products = try await fetchProducts()
        } catch is CancellationError {
            // Normal cancellation
        } catch {
            loadError = error
        }
    }
}
```
