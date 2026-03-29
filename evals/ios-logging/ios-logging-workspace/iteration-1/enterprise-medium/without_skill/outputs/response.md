# Retry Mechanism for Network Requests with Exponential Backoff, Jitter, and Observability

## Overview

This implementation provides a production-ready retry mechanism for iOS network requests featuring exponential backoff with jitter, comprehensive logging via `os.log` (Apple's unified logging system), and structured error tracking.

---

## 1. Retry Configuration

```swift
import Foundation
import os.log

struct RetryConfiguration {
    let maxRetries: Int
    let baseDelay: TimeInterval
    let maxDelay: TimeInterval
    let jitterFactor: Double // 0.0 to 1.0
    let retryableStatusCodes: Set<Int>
    let retryableErrors: Set<URLError.Code>

    static let `default` = RetryConfiguration(
        maxRetries: 3,
        baseDelay: 1.0,
        maxDelay: 30.0,
        jitterFactor: 0.5,
        retryableStatusCodes: Set([408, 429, 500, 502, 503, 504]),
        retryableErrors: Set([
            .timedOut,
            .networkConnectionLost,
            .notConnectedToInternet,
            .cannotConnectToHost
        ])
    )
}
```

## 2. Retry Metrics (Observability)

```swift
struct RetryMetrics {
    let requestID: UUID
    let url: String
    let method: String
    let attempt: Int
    let maxAttempts: Int
    let delayApplied: TimeInterval
    let statusCode: Int?
    let error: Error?
    let startTime: Date
    let endTime: Date

    var duration: TimeInterval {
        endTime.timeIntervalSince(startTime)
    }
}

final class RetryObserver {
    private let logger: Logger
    private let signposter: OSSignposter

    init(subsystem: String = Bundle.main.bundleIdentifier ?? "com.app.networking",
         category: String = "RetryMechanism") {
        self.logger = Logger(subsystem: subsystem, category: category)
        self.signposter = OSSignposter(subsystem: subsystem, category: category)
    }

    func logAttemptStart(requestID: UUID, url: String, attempt: Int, maxAttempts: Int) {
        logger.info("""
            [Retry] Starting attempt \(attempt)/\(maxAttempts) \
            requestID=\(requestID.uuidString) \
            url=\(url, privacy: .private)
            """)
    }

    func logAttemptResult(metrics: RetryMetrics) {
        if let statusCode = metrics.statusCode, (200..<300).contains(statusCode) {
            logger.info("""
                [Retry] Success on attempt \(metrics.attempt)/\(metrics.maxAttempts) \
                requestID=\(metrics.requestID.uuidString) \
                status=\(statusCode) \
                duration=\(String(format: "%.3f", metrics.duration))s
                """)
        } else if let statusCode = metrics.statusCode {
            logger.warning("""
                [Retry] Failed attempt \(metrics.attempt)/\(metrics.maxAttempts) \
                requestID=\(metrics.requestID.uuidString) \
                status=\(statusCode) \
                duration=\(String(format: "%.3f", metrics.duration))s
                """)
        } else if let error = metrics.error {
            logger.error("""
                [Retry] Error on attempt \(metrics.attempt)/\(metrics.maxAttempts) \
                requestID=\(metrics.requestID.uuidString) \
                error=\(error.localizedDescription, privacy: .public) \
                duration=\(String(format: "%.3f", metrics.duration))s
                """)
        }
    }

    func logBackoff(requestID: UUID, delay: TimeInterval, attempt: Int) {
        logger.info("""
            [Retry] Backing off \(String(format: "%.2f", delay))s before attempt \(attempt + 1) \
            requestID=\(requestID.uuidString)
            """)
    }

    func logExhausted(requestID: UUID, totalAttempts: Int, totalDuration: TimeInterval) {
        logger.error("""
            [Retry] All \(totalAttempts) attempts exhausted \
            requestID=\(requestID.uuidString) \
            totalDuration=\(String(format: "%.3f", totalDuration))s
            """)
    }

    func beginInterval(_ name: StaticString) -> OSSignpostIntervalState {
        let signpostID = signposter.makeSignpostID()
        return signposter.beginInterval(name, id: signpostID)
    }

    func endInterval(_ name: StaticString, _ state: OSSignpostIntervalState) {
        signposter.endInterval(name, state)
    }
}
```

## 3. Core Retry Client

```swift
final class RetryingNetworkClient {
    private let session: URLSession
    private let configuration: RetryConfiguration
    private let observer: RetryObserver

    init(session: URLSession = .shared,
         configuration: RetryConfiguration = .default,
         observer: RetryObserver = RetryObserver()) {
        self.session = session
        self.configuration = configuration
        self.observer = observer
    }

    // MARK: - Exponential Backoff with Jitter

    /// Calculates delay using "decorrelated jitter" strategy.
    /// Formula: delay = min(maxDelay, random_between(baseDelay, baseDelay * 2^attempt * (1 + jitter)))
    private func calculateDelay(forAttempt attempt: Int) -> TimeInterval {
        let exponentialDelay = configuration.baseDelay * pow(2.0, Double(attempt))
        let jitterRange = exponentialDelay * configuration.jitterFactor
        let jitter = Double.random(in: -jitterRange...jitterRange)
        let delay = exponentialDelay + jitter
        return min(max(delay, 0), configuration.maxDelay)
    }

    // MARK: - Retry Logic

    func data(for request: URLRequest) async throws -> (Data, URLResponse) {
        let requestID = UUID()
        let url = request.url?.absoluteString ?? "unknown"
        let method = request.httpMethod ?? "GET"
        let overallStart = Date()

        let intervalState = observer.beginInterval("NetworkRequestWithRetry")

        var lastError: Error?

        for attempt in 1...configuration.maxRetries + 1 {
            observer.logAttemptStart(
                requestID: requestID,
                url: url,
                attempt: attempt,
                maxAttempts: configuration.maxRetries + 1
            )

            let attemptStart = Date()

            do {
                let (data, response) = try await session.data(for: request)

                let attemptEnd = Date()
                let httpResponse = response as? HTTPURLResponse
                let statusCode = httpResponse?.statusCode ?? 0

                let metrics = RetryMetrics(
                    requestID: requestID,
                    url: url,
                    method: method,
                    attempt: attempt,
                    maxAttempts: configuration.maxRetries + 1,
                    delayApplied: 0,
                    statusCode: statusCode,
                    error: nil,
                    startTime: attemptStart,
                    endTime: attemptEnd
                )
                observer.logAttemptResult(metrics: metrics)

                // Check if status code is retryable
                if configuration.retryableStatusCodes.contains(statusCode) {
                    if attempt <= configuration.maxRetries {
                        let delay = calculateDelay(forAttempt: attempt - 1)
                        observer.logBackoff(requestID: requestID, delay: delay, attempt: attempt)

                        // Respect Retry-After header if present
                        let actualDelay = retryAfterDelay(from: httpResponse) ?? delay
                        try await Task.sleep(nanoseconds: UInt64(actualDelay * 1_000_000_000))
                        continue
                    }
                }

                // Success or non-retryable status
                observer.endInterval("NetworkRequestWithRetry", intervalState)
                return (data, response)

            } catch let urlError as URLError {
                let attemptEnd = Date()
                let metrics = RetryMetrics(
                    requestID: requestID,
                    url: url,
                    method: method,
                    attempt: attempt,
                    maxAttempts: configuration.maxRetries + 1,
                    delayApplied: 0,
                    statusCode: nil,
                    error: urlError,
                    startTime: attemptStart,
                    endTime: attemptEnd
                )
                observer.logAttemptResult(metrics: metrics)

                lastError = urlError

                guard configuration.retryableErrors.contains(urlError.code),
                      attempt <= configuration.maxRetries else {
                    observer.endInterval("NetworkRequestWithRetry", intervalState)
                    throw urlError
                }

                let delay = calculateDelay(forAttempt: attempt - 1)
                observer.logBackoff(requestID: requestID, delay: delay, attempt: attempt)
                try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))

            } catch {
                // Non-URLError -- don't retry
                observer.endInterval("NetworkRequestWithRetry", intervalState)
                throw error
            }
        }

        observer.logExhausted(
            requestID: requestID,
            totalAttempts: configuration.maxRetries + 1,
            totalDuration: Date().timeIntervalSince(overallStart)
        )
        observer.endInterval("NetworkRequestWithRetry", intervalState)
        throw lastError ?? URLError(.unknown)
    }

    // MARK: - Retry-After Header Parsing

    private func retryAfterDelay(from response: HTTPURLResponse?) -> TimeInterval? {
        guard let retryAfterValue = response?.value(forHTTPHeaderField: "Retry-After") else {
            return nil
        }

        // Retry-After can be seconds (integer) or an HTTP date
        if let seconds = Double(retryAfterValue) {
            return seconds
        }

        let formatter = DateFormatter()
        formatter.dateFormat = "EEE, dd MMM yyyy HH:mm:ss zzz"
        formatter.locale = Locale(identifier: "en_US_POSIX")
        if let date = formatter.date(from: retryAfterValue) {
            return max(0, date.timeIntervalSinceNow)
        }

        return nil
    }
}
```

## 4. Usage Example

```swift
let client = RetryingNetworkClient(
    configuration: RetryConfiguration(
        maxRetries: 3,
        baseDelay: 0.5,
        maxDelay: 16.0,
        jitterFactor: 0.25,
        retryableStatusCodes: Set([429, 500, 502, 503, 504]),
        retryableErrors: Set([.timedOut, .networkConnectionLost])
    )
)

func fetchUserProfile(userID: String) async throws -> UserProfile {
    var request = URLRequest(url: URL(string: "https://api.example.com/users/\(userID)")!)
    request.httpMethod = "GET"
    request.setValue("application/json", forHTTPHeaderField: "Accept")

    let (data, _) = try await client.data(for: request)
    return try JSONDecoder().decode(UserProfile.self, from: data)
}
```

## 5. Viewing Logs in Console.app and Instruments

### Console.app

Filter logs in Console.app using:
- **Subsystem**: Your bundle identifier (e.g., `com.yourapp`)
- **Category**: `RetryMechanism`
- **Message**: Filter by `[Retry]` prefix

This gives you a real-time stream of retry attempts, backoff delays, and failures.

### Instruments

The `OSSignposter` integration means each retry sequence appears as a measurable interval in Instruments. Open the **os_signpost** instrument to see:

- Total duration of a retry sequence
- Visual timeline of retries with gaps showing backoff periods
- Correlation with other system activity (network, CPU)

### Log Levels Used

| Level     | When Used                                  |
|-----------|--------------------------------------------|
| `.info`   | Attempt start, successful completion, backoff delays |
| `.warning`| Retryable HTTP error status codes          |
| `.error`  | Network errors, all retries exhausted      |

## 6. Key Design Decisions

### Why Exponential Backoff with Jitter?

Plain exponential backoff causes the "thundering herd" problem when many clients retry simultaneously after an outage. Adding jitter spreads retries across a time window, reducing server load during recovery. The implementation uses **full jitter** where the delay is randomized within a range centered on the exponential value.

### Why `os.log` over `print` or Third-Party Loggers?

- **Performance**: `os.log` is lazy -- the system only formats the string if the log level is active. There is near-zero overhead when logs are not being observed.
- **Privacy**: The `privacy` parameter controls what appears in production logs vs. debug sessions. URLs are marked `.private` so they are redacted in production log captures but visible during development.
- **Integration**: Logs appear in Console.app, Xcode console, and can be collected via log profiles for crash diagnostics.
- **Persistence**: The system manages log storage and rotation automatically.

### Why `OSSignposter`?

`OSSignposter` integrates with Instruments to create measurable time intervals. This lets you:
- Profile retry behavior in the Instruments timeline
- Measure total time spent in retry sequences
- Identify retry storms correlated with other performance events

### Cancellation Support

Because the implementation uses `async/await` with `Task.sleep`, it automatically supports Swift concurrency cancellation. If the calling `Task` is cancelled during a backoff sleep, the `CancellationError` propagates immediately rather than waiting for the full delay.

### Retry-After Header

The implementation respects the HTTP `Retry-After` header, which servers use (especially with 429 status codes) to tell clients exactly how long to wait. When present, this overrides the calculated exponential backoff delay.

## 7. Testing the Retry Logic

```swift
import XCTest

final class RetryingNetworkClientTests: XCTestCase {

    func testExponentialBackoffCalculation() {
        // Verify delays increase exponentially
        let config = RetryConfiguration(
            maxRetries: 5,
            baseDelay: 1.0,
            maxDelay: 60.0,
            jitterFactor: 0.0, // No jitter for deterministic testing
            retryableStatusCodes: Set([500]),
            retryableErrors: Set([.timedOut])
        )

        let client = RetryingNetworkClient(configuration: config)

        // With jitter=0, delays should be exactly: 1, 2, 4, 8, 16
        // Access via a test helper or make calculateDelay internal for testing
    }

    func testRespectsMaxDelay() {
        let config = RetryConfiguration(
            maxRetries: 10,
            baseDelay: 1.0,
            maxDelay: 5.0,
            jitterFactor: 0.0,
            retryableStatusCodes: Set([500]),
            retryableErrors: Set([.timedOut])
        )

        // Even at attempt 10 (2^10 = 1024), delay should cap at 5.0
    }

    func testDoesNotRetryNonRetryableStatusCodes() async throws {
        // Mock URLSession returning 404
        // Assert only 1 attempt was made
    }

    func testRetriesOnServerError() async throws {
        // Mock URLSession returning 503 then 200
        // Assert 2 attempts were made
    }

    func testCancellationDuringBackoff() async throws {
        let task = Task {
            try await client.data(for: request)
        }

        // Cancel during backoff
        try await Task.sleep(nanoseconds: 500_000_000)
        task.cancel()

        // Assert CancellationError is thrown
    }
}
```

## 8. Production Considerations

- **Idempotency**: Only retry requests that are safe to repeat. GET requests are inherently idempotent. For POST/PUT/PATCH, ensure your API supports idempotency keys or only retry if the error occurred before the server processed the request.
- **Circuit Breaker**: For high-traffic apps, combine this retry mechanism with a circuit breaker pattern to stop retrying entirely when a service is clearly down, avoiding wasted resources.
- **Metrics Aggregation**: In production, consider forwarding `RetryMetrics` to your analytics pipeline to track retry rates, success-after-retry rates, and average retry counts per endpoint.
- **Memory/Battery**: On iOS, be mindful that aggressive retries drain battery. The `maxDelay` cap and limited `maxRetries` help, but consider reducing retries when the device is on low power mode (`ProcessInfo.processInfo.isLowPowerModeEnabled`).
