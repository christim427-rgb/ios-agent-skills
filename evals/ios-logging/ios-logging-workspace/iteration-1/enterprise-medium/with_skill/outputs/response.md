# Retry Mechanism for Network Requests with Exponential Backoff, Jitter, and Full Observability

## Architecture Overview

The retry mechanism sits in the Application Layer of the observability stack and integrates with both the Logging Layer (`os.Logger`) and the Crash Layer (`ErrorReporter` protocol). The key design principle: **log every attempt as a warning breadcrumb, but only report to your crash SDK after all retries are exhausted**. This prevents noisy transient failures from flooding Sentry/Crashlytics while still giving you full visibility into retry patterns.

```
Caller (ViewModel / Service)
   └─▶ retryWithBackoff(operation:action:)
           ├── attempt 1 → success → return result
           ├── attempt 1 → failure → Logger.warning + breadcrumb → sleep with backoff+jitter
           ├── attempt 2 → failure → Logger.warning + breadcrumb → sleep with backoff+jitter
           └── attempt 3 → failure → Logger.error + ErrorReporter.recordNonFatal → throw
```

## Prerequisites

Before implementing this, you need two foundational pieces from the skill's recommended observability stack:

### 1. Logger Extension (Subsystem/Category)

```swift
import OSLog

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier ?? "com.app"

    static let networking = Logger(subsystem: subsystem, category: "networking")
}
```

### 2. ErrorReporter Protocol

Abstract your crash SDK behind a protocol so the retry logic never calls Sentry or Crashlytics directly. This enables testability and vendor swapping.

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

Provide a concrete implementation wrapping your chosen SDK (Sentry, Crashlytics, or a composite of both). See the crash-sdk-integration reference for full implementations.

## The Retry Function

```swift
import OSLog

func retryWithBackoff<T>(
    maxAttempts: Int = 3,
    base: Double = 0.25,
    operation: String = "unknown",
    action: () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 1...maxAttempts {
        do {
            return try await action()
        } catch {
            lastError = error

            // 1. ALWAYS: Structured log with privacy annotations
            Logger.networking.warning(
                "Attempt \(attempt, privacy: .public)/\(maxAttempts, privacy: .public) failed for \(operation, privacy: .public): \(error.localizedDescription, privacy: .public)"
            )

            // 2. ALWAYS: Breadcrumb for crash SDK context trail
            ErrorReporter.shared.addBreadcrumb(
                message: "Retry attempt \(attempt) failed",
                category: "network",
                level: .warning,
                data: [
                    "attempt": attempt,
                    "operation": operation,
                    "error": "\(error)"
                ]
            )

            // 3. Wait with exponential backoff + jitter (except on last attempt)
            if attempt < maxAttempts {
                let delay = min(pow(2, Double(attempt)) * base, 60)
                let jitter = Double.random(in: 0...(delay * 0.5))
                try await Task.sleep(nanoseconds: UInt64((delay + jitter) * 1_000_000_000))
            }
        }
    }

    // All retries exhausted — NOW report to crash SDK as non-fatal
    ErrorReporter.shared.recordNonFatal(lastError!, context: [
        "operation": operation,
        "maxAttempts": maxAttempts
    ])

    throw lastError!
}
```

### Why This Design

- **`os.Logger` at `.warning` level on each attempt**: Warnings are always persisted to disk, so you can pull them from Console.app or `log collect` on any device. Using `.warning` (not `.error`) distinguishes transient retries from terminal failures.
- **Breadcrumbs on each attempt**: If the operation eventually causes a crash downstream, the breadcrumb trail shows exactly which retries preceded it. Breadcrumbs are buffered locally and attached to the next error or crash report automatically.
- **`recordNonFatal` only after exhaustion**: This is critical. If you report every failed attempt, a single flaky endpoint retried 3 times across 100K users generates 300K non-fatal events. Crashlytics has a hard limit of 8 non-fatals per session. Sentry has rate limits. Report once when the operation truly fails.
- **Exponential backoff formula**: `min(pow(2, attempt) * base, 60)` with a `base` of 0.25 seconds gives delays of 0.5s, 1s, 2s for 3 attempts. The cap at 60 seconds prevents absurd waits if `maxAttempts` is raised.
- **Jitter**: `Double.random(in: 0...(delay * 0.5))` adds up to 50% of the delay as random jitter. This prevents the thundering herd problem where thousands of devices retry at the exact same instant after a server outage.

## Integrating with CategorizedError

Use the `CategorizedError` protocol to ensure only retryable errors trigger retries. Non-retryable errors (404, decoding failures) and auth errors should fail immediately.

```swift
enum ErrorCategory {
    case retryable
    case nonRetryable
    case requiresLogout
}

protocol CategorizedError: Error {
    var category: ErrorCategory { get }
}

enum NetworkError: Error, CategorizedError {
    case timeout
    case serverError(Int)
    case notFound
    case decodingFailed(Error)
    case unauthorized
    case noConnection

    var category: ErrorCategory {
        switch self {
        case .timeout, .serverError, .noConnection:
            return .retryable
        case .notFound, .decodingFailed:
            return .nonRetryable
        case .unauthorized:
            return .requiresLogout
        }
    }
}
```

Then create a smarter retry variant that checks the category:

```swift
func retryNetworkRequest<T>(
    maxAttempts: Int = 3,
    base: Double = 0.25,
    operation: String,
    action: () async throws -> T
) async throws -> T {
    var lastError: Error?

    for attempt in 1...maxAttempts {
        do {
            return try await action()
        } catch {
            lastError = error

            Logger.networking.warning(
                "Attempt \(attempt, privacy: .public)/\(maxAttempts, privacy: .public) failed for \(operation, privacy: .public): \(error.localizedDescription, privacy: .public)"
            )

            ErrorReporter.shared.addBreadcrumb(
                message: "Retry attempt \(attempt) failed",
                category: "network",
                level: .warning,
                data: [
                    "attempt": attempt,
                    "operation": operation,
                    "error": "\(error)"
                ]
            )

            // Check if error is retryable — bail immediately if not
            if let categorized = error as? CategorizedError {
                switch categorized.category {
                case .nonRetryable:
                    Logger.networking.error(
                        "Non-retryable error for \(operation, privacy: .public), failing immediately: \(error.localizedDescription, privacy: .public)"
                    )
                    ErrorReporter.shared.recordNonFatal(error, context: [
                        "operation": operation,
                        "reason": "nonRetryable",
                        "attempt": attempt
                    ])
                    throw error

                case .requiresLogout:
                    Logger.networking.error(
                        "Auth error for \(operation, privacy: .public), requires logout: \(error.localizedDescription, privacy: .public)"
                    )
                    ErrorReporter.shared.recordNonFatal(error, context: [
                        "operation": operation,
                        "reason": "requiresLogout",
                        "attempt": attempt
                    ])
                    throw error

                case .retryable:
                    break // Continue to backoff logic below
                }
            }

            if attempt < maxAttempts {
                let delay = min(pow(2, Double(attempt)) * base, 60)
                let jitter = Double.random(in: 0...(delay * 0.5))
                try await Task.sleep(nanoseconds: UInt64((delay + jitter) * 1_000_000_000))
            }
        }
    }

    ErrorReporter.shared.recordNonFatal(lastError!, context: [
        "operation": operation,
        "maxAttempts": maxAttempts
    ])
    throw lastError!
}
```

## Usage in a ViewModel

```swift
@MainActor
final class ProfileViewModel: ObservableObject {
    @Published var profile: UserProfile?
    @Published var isLoading = false

    private let errorHandler: ErrorHandler

    func loadProfile() {
        isLoading = true

        Task {
            do {
                let result = try await retryNetworkRequest(
                    operation: "loadUserProfile"
                ) {
                    try await apiClient.fetchProfile()
                }
                self.profile = result
            } catch {
                // Error is already logged and reported inside retryNetworkRequest.
                // Here we only handle the UI response via the centralized handler.
                errorHandler.handle(error, context: "ProfileViewModel.loadProfile")
            }
            isLoading = false
        }
    }
}
```

## Usage in a SwiftUI `.task {}` Modifier

When using retries inside `.task {}`, you must handle `CancellationError` separately. The view can disappear mid-retry, and you should not report cancellation as a failure.

```swift
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()

    var body: some View {
        content
            .task {
                do {
                    try await viewModel.loadProfile()
                } catch is CancellationError {
                    // Normal — view disappeared during retry. Not an error.
                    Logger.networking.debug("Profile load cancelled — view disappeared")
                } catch {
                    // Already reported inside retryNetworkRequest
                }
            }
    }
}
```

## Validating HTTP Status Codes

A common silent failure pattern: `URLSession` does not throw on HTTP 4xx/5xx responses. You must validate the status code and throw a typed error so the retry mechanism can categorize it.

```swift
func fetchData(from url: URL) async throws -> Data {
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.noConnection
    }

    switch httpResponse.statusCode {
    case 200...299:
        return data
    case 401:
        throw NetworkError.unauthorized
    case 404:
        throw NetworkError.notFound
    case 500...599:
        throw NetworkError.serverError(httpResponse.statusCode)
    default:
        throw NetworkError.serverError(httpResponse.statusCode)
    }
}
```

## What You Get in Production

When a network request fails all retries, your crash dashboard (Sentry/Crashlytics) will show:

1. **One non-fatal event** with context: `{"operation": "loadUserProfile", "maxAttempts": 3}`
2. **Three breadcrumbs** preceding it, each with the attempt number, operation name, and specific error message
3. **os.Logger entries** on the device at `.warning` level for each attempt, and `.error` for the final failure, all with privacy-annotated dynamic strings

This gives you the full retry timeline without flooding your crash SDK with transient noise. You can see the exact sequence of events leading to the failure, which is what transforms a multi-day debugging session into a quick investigation.
