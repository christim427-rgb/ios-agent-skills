# Adding Error Handling with Crash Reporting to a Network Call

## Enhanced Implementation

```swift
import Foundation
import os.log

// MARK: - Custom Error Types

enum NetworkError: Error, LocalizedError {
    case invalidResponse(statusCode: Int)
    case noData
    case decodingFailed(underlyingError: Error)
    case requestFailed(underlyingError: Error)
    case invalidURL

    var errorDescription: String? {
        switch self {
        case .invalidResponse(let statusCode):
            return "Server returned an invalid response (HTTP \(statusCode))"
        case .noData:
            return "No data received from the server"
        case .decodingFailed(let error):
            return "Failed to decode response: \(error.localizedDescription)"
        case .requestFailed(let error):
            return "Network request failed: \(error.localizedDescription)"
        case .invalidURL:
            return "The request URL is invalid"
        }
    }
}

// MARK: - Crash Reporter Protocol

protocol CrashReporting {
    func recordError(_ error: Error, userInfo: [String: Any])
    func log(_ message: String)
    func setCustomValue(_ value: Any?, forKey key: String)
}

// MARK: - Crashlytics Implementation (Firebase)

/// Wrapper around Firebase Crashlytics.
/// Replace the body of each method with actual Crashlytics SDK calls.
final class CrashlyticsCrashReporter: CrashReporting {
    static let shared = CrashlyticsCrashReporter()

    func recordError(_ error: Error, userInfo: [String: Any] = [:]) {
        // Crashlytics.crashlytics().record(error: error, userInfo: userInfo)
    }

    func log(_ message: String) {
        // Crashlytics.crashlytics().log(message)
    }

    func setCustomValue(_ value: Any?, forKey key: String) {
        // Crashlytics.crashlytics().setCustomValue(value, forKey: key)
    }
}

// MARK: - Network Service with Error Handling and Crash Reporting

final class ProductService {
    private let session: URLSession
    private let decoder: JSONDecoder
    private let crashReporter: CrashReporting
    private let logger = Logger(subsystem: Bundle.main.bundleIdentifier ?? "com.app", category: "Network")

    init(
        session: URLSession = .shared,
        decoder: JSONDecoder = JSONDecoder(),
        crashReporter: CrashReporting = CrashlyticsCrashReporter.shared
    ) {
        self.session = session
        self.decoder = decoder
        self.crashReporter = crashReporter
    }

    func fetchProducts() async throws -> [Product] {
        let productsURL = URL(string: "https://api.example.com/products")!

        crashReporter.log("Fetching products from \(productsURL.absoluteString)")

        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(from: productsURL)
        } catch let urlError as URLError {
            logger.error("URLError fetching products: \(urlError.localizedDescription)")
            crashReporter.recordError(urlError, userInfo: [
                "endpoint": productsURL.absoluteString,
                "errorCode": urlError.code.rawValue,
                "failingURL": urlError.failureURLString ?? "unknown"
            ])
            throw NetworkError.requestFailed(underlyingError: urlError)
        } catch {
            logger.error("Unexpected error fetching products: \(error.localizedDescription)")
            crashReporter.recordError(error, userInfo: [
                "endpoint": productsURL.absoluteString,
                "context": "unexpected_network_error"
            ])
            throw NetworkError.requestFailed(underlyingError: error)
        }

        // Validate HTTP response
        guard let httpResponse = response as? HTTPURLResponse else {
            let error = NetworkError.invalidResponse(statusCode: -1)
            crashReporter.recordError(error, userInfo: [
                "endpoint": productsURL.absoluteString,
                "context": "non_http_response"
            ])
            throw error
        }

        crashReporter.setCustomValue(httpResponse.statusCode, forKey: "last_http_status")

        guard (200...299).contains(httpResponse.statusCode) else {
            let error = NetworkError.invalidResponse(statusCode: httpResponse.statusCode)
            logger.error("HTTP \(httpResponse.statusCode) for products endpoint")

            // Capture response body for non-sensitive debugging
            let responseBody = String(data: data, encoding: .utf8) ?? "non-UTF8 body"
            crashReporter.recordError(error, userInfo: [
                "endpoint": productsURL.absoluteString,
                "statusCode": httpResponse.statusCode,
                "responseBodyPrefix": String(responseBody.prefix(500))
            ])
            throw error
        }

        // Decode
        do {
            let products = try decoder.decode([Product].self, from: data)
            logger.info("Successfully decoded \(products.count) products")
            return products
        } catch let decodingError as DecodingError {
            logger.error("Decoding error: \(decodingError.localizedDescription)")

            var userInfo: [String: Any] = [
                "endpoint": productsURL.absoluteString,
                "dataSize": data.count,
                "responseBodyPrefix": String(data: data.prefix(500), encoding: .utf8) ?? "non-UTF8"
            ]

            // Add specific decoding context
            switch decodingError {
            case .keyNotFound(let key, let context):
                userInfo["missingKey"] = key.stringValue
                userInfo["codingPath"] = context.codingPath.map(\.stringValue).joined(separator: ".")
            case .typeMismatch(let type, let context):
                userInfo["expectedType"] = String(describing: type)
                userInfo["codingPath"] = context.codingPath.map(\.stringValue).joined(separator: ".")
            case .valueNotFound(let type, let context):
                userInfo["expectedType"] = String(describing: type)
                userInfo["codingPath"] = context.codingPath.map(\.stringValue).joined(separator: ".")
            case .dataCorrupted(let context):
                userInfo["codingPath"] = context.codingPath.map(\.stringValue).joined(separator: ".")
                userInfo["debugDescription"] = context.debugDescription
            @unknown default:
                userInfo["rawDescription"] = decodingError.localizedDescription
            }

            crashReporter.recordError(decodingError, userInfo: userInfo)
            throw NetworkError.decodingFailed(underlyingError: decodingError)
        }
    }
}
```

## Key Points

### 1. Typed Error Enum
A `NetworkError` enum provides clear, categorized error cases instead of letting raw system errors propagate. Each case carries relevant context (status codes, underlying errors) that callers can switch on.

### 2. Crash Reporter Abstraction
The `CrashReporting` protocol decouples your code from any specific SDK (Firebase Crashlytics, Sentry, Datadog, etc.). This makes testing straightforward -- inject a mock reporter in unit tests -- and allows swapping providers without touching business logic.

### 3. What Gets Reported

| Scenario | Data sent to crash reporter |
|---|---|
| **Network failure** (`URLError`) | Endpoint URL, error code, failing URL |
| **Bad HTTP status** | Endpoint, status code, truncated response body |
| **Decoding failure** | Endpoint, data size, truncated body, missing key / type mismatch details, full coding path |

### 4. os.log Integration
The `Logger` from `os.log` writes structured logs to the system console. These show up in Console.app and Xcode's debug console during development but do not leave the device in production (unless the log level is `.fault` or `.error` and the device is connected to a profiling tool).

### 5. Sensitive Data Considerations
- Response bodies are truncated to 500 characters before attaching to crash reports to avoid leaking large payloads or PII.
- Avoid logging or reporting authorization headers, tokens, or user-specific query parameters.

### 6. Retry Strategy (Optional Extension)
For production use, consider wrapping the call with exponential backoff for transient failures:

```swift
func fetchProductsWithRetry(maxAttempts: Int = 3) async throws -> [Product] {
    var lastError: Error?
    for attempt in 1...maxAttempts {
        do {
            return try await fetchProducts()
        } catch let error as NetworkError {
            lastError = error
            switch error {
            case .invalidResponse(let code) where (500...599).contains(code):
                let delay = UInt64(pow(2.0, Double(attempt - 1))) * 1_000_000_000
                try await Task.sleep(nanoseconds: delay)
                continue
            case .requestFailed:
                let delay = UInt64(pow(2.0, Double(attempt - 1))) * 1_000_000_000
                try await Task.sleep(nanoseconds: delay)
                continue
            default:
                throw error // non-retryable (e.g., decoding)
            }
        }
    }
    throw lastError!
}
```

### 7. Using with Third-Party SDKs

To wire up a real SDK, implement the `CrashReporting` protocol. For example, with Sentry:

```swift
import Sentry

final class SentryCrashReporter: CrashReporting {
    func recordError(_ error: Error, userInfo: [String: Any]) {
        SentrySDK.capture(error: error) { scope in
            for (key, value) in userInfo {
                scope.setExtra(value: value, key: key)
            }
        }
    }

    func log(_ message: String) {
        let breadcrumb = Breadcrumb(level: .info, category: "network")
        breadcrumb.message = message
        SentrySDK.addBreadcrumb(breadcrumb)
    }

    func setCustomValue(_ value: Any?, forKey key: String) {
        SentrySDK.configureScope { scope in
            scope.setExtra(value: value, key: key)
        }
    }
}
```

Then inject it:

```swift
let service = ProductService(crashReporter: SentryCrashReporter())
let products = try await service.fetchProductsWithRetry()
```
