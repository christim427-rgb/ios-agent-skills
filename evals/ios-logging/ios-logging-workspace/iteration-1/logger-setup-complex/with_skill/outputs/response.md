# HIPAA-Adjacent Health Tech Logging Strategy

## Guiding Principles

Health tech apps handle sensitive data -- vitals, medications, conditions, appointment details -- that falls under HIPAA-adjacent obligations even if you are not a covered entity. The logging strategy must satisfy two competing goals:

1. **Debuggability**: When a sync fails at 2 AM for a user in a poor-connectivity region, you need enough context to reproduce and fix it without asking the user.
2. **Compliance**: No Protected Health Information (PHI) or Personally Identifiable Information (PII) may appear in logs, crash reports, or breadcrumb trails in plaintext.

The entire strategy rests on three non-negotiable rules:

- No `print()` in production code -- use `os.Logger` with privacy annotations.
- No catch block without observability -- every caught error must be logged AND reported to a remote crash service.
- No `try?` on operations where failure matters -- network calls, persistence, auth, and anything user-facing must use `do/catch`.

---

## 1. Observability Stack Overview

```
Presentation Layer   -> SwiftUI error state + centralized ErrorHandler
Application Layer    -> ErrorReporter protocol (abstracts Sentry)
Logging Layer        -> os.Logger with subsystem/category + privacy annotations
Diagnostics Layer    -> MetricKit (OOM, watchdog kills, hangs)
Crash Layer          -> Sentry (fatal crashes + non-fatals + breadcrumbs) + dSYMs
```

**SDK choice**: For a standalone health tech app talking to a REST API (not Firebase-based), Sentry is the recommended primary crash reporter. It provides the richest error context, breadcrumbs, and performance monitoring. If you also need product analytics, pair Sentry (crashes) with PostHog (analytics, session replay) -- but PostHog is not a crash reporter on iOS.

Never run two fatal crash reporters simultaneously. Signal handler conflicts between Sentry and Crashlytics mean only the last one registered receives SIGABRT/SIGSEGV signals.

---

## 2. Logger Setup with Health-Specific Categories

```swift
import os

extension Logger {
    private static let subsystem = Bundle.main.bundleIdentifier!

    // Standard categories
    static let networking = Logger(subsystem: subsystem, category: "Networking")
    static let auth       = Logger(subsystem: subsystem, category: "Authentication")
    static let database   = Logger(subsystem: subsystem, category: "Database")
    static let ui         = Logger(subsystem: subsystem, category: "UI")
    static let lifecycle  = Logger(subsystem: subsystem, category: "Lifecycle")
    static let sync       = Logger(subsystem: subsystem, category: "Sync")

    // Health-domain categories
    static let healthData = Logger(subsystem: subsystem, category: "HealthData")
    static let vitals     = Logger(subsystem: subsystem, category: "Vitals")
    static let medications = Logger(subsystem: subsystem, category: "Medications")
    static let appointments = Logger(subsystem: subsystem, category: "Appointments")
}
```

### Log Level Discipline

| Level | Persisted? | Use for in your health app |
|---|---|---|
| `.debug` | No (memory only, discarded) | Request/response sizes, decoding steps, cache hits -- free in production |
| `.info` | Memory only (captured on faults) | Successful sync completion, background refresh triggers |
| `.notice` | Persisted to disk | User initiated actions (started a measurement, opened a record) |
| `.error` | Always persisted | API failures, decode failures, sync conflicts |
| `.fault` | Always persisted + process chain | Unexpected nil where data should exist, database corruption |

`.debug` messages are zero-cost in production -- the compiler optimizes away message creation entirely. You can leave verbose debug logging in your networking layer safely.

---

## 3. Privacy Annotations -- The Core of HIPAA-Adjacent Compliance

This is the single most important section. Apple's `os.Logger` redacts dynamic strings by default in production logs (they appear as `<private>` without a debugger attached). You must use this system deliberately.

### Classification Rules for Health Data

```
Is this value safe for anyone with log access to see?
+-- YES (HTTP status codes, endpoint paths like /api/v1/vitals, error codes,
|        operation names, retry counts, response sizes)
|   -> privacy: .public
|
+-- NO -- Is it PHI or PII?
    +-- YES (patient name, DOB, diagnosis, medication names tied to a user,
    |        vitals readings, email, phone)
    |   +-- Do you need cross-event correlation?
    |   |   +-- YES -> privacy: .private(mask: .hash)
    |   |   +-- NO  -> privacy: .private
    |   +-- Is it a clinical value (heart rate, blood glucose)?
    |       -> DO NOT LOG THE VALUE. Log the operation name and outcome only.
    |
    +-- NO -- Is it a secret (token, API key, refresh token)?
        -> DO NOT LOG IT AT ALL. If you must reference it: privacy: .sensitive
```

### Concrete Patterns

```swift
// Networking -- safe to log endpoint and status, never log body
Logger.networking.info("GET \(endpoint, privacy: .public) started")
Logger.networking.error(
    "GET \(endpoint, privacy: .public) failed: HTTP \(statusCode, privacy: .public)"
)

// Auth -- hash the user identifier for correlation, never log tokens
Logger.auth.notice("Login attempt for \(userId, privacy: .private(mask: .hash))")
Logger.auth.error("Auth failed: \(error.localizedDescription, privacy: .public)")
// NEVER: Logger.auth.debug("Token: \(accessToken)") -- even at debug level

// Health data -- log the operation, not the clinical values
Logger.vitals.notice("Vitals sync started, \(recordCount, privacy: .public) records pending")
Logger.vitals.error("Vitals sync failed at record \(index, privacy: .public): \(error.localizedDescription, privacy: .public)")
// NEVER: Logger.vitals.info("Heart rate: \(bpm)") -- this is PHI

// Medications -- log operation outcomes, not medication names
Logger.medications.notice("Medication schedule updated, \(count, privacy: .public) entries")
Logger.medications.error("Medication fetch failed: \(error.localizedDescription, privacy: .public)")

// Database
Logger.database.error(
    "Save failed: code=\(nsError.code, privacy: .public) domain=\(nsError.domain, privacy: .public)"
)
```

**Critical rule**: Clinical values (heart rate, blood pressure, glucose readings, medication names, diagnosis codes) must never appear in logs, even with `.private` annotation. Log the operation name and outcome (success/failure/count), not the data itself.

---

## 4. ErrorReporter Protocol -- Vendor-Agnostic Abstraction

Never call Sentry APIs directly throughout the codebase. Use a protocol so you can swap vendors, test in isolation, and enforce redaction at a single chokepoint.

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

### Sentry Implementation

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

### PHI-Safe Redaction Layer

Add a redaction layer that sits between your application code and the ErrorReporter so PHI can never leak into crash reports:

```swift
enum Redactor {
    static func maskID(_ id: String) -> String {
        guard id.count > 4 else { return "****" }
        return "***\(id.suffix(4))"
    }

    static func maskEmail(_ email: String) -> String {
        guard let at = email.firstIndex(of: "@") else { return "***" }
        return "\(email.prefix(1))***\(email[at...])"
    }
}

// Usage -- all context values must go through Redactor before reaching Sentry
ErrorReporter.shared.recordNonFatal(error, context: [
    "userId": Redactor.maskID(userId),       // "***4f8a"
    "email": Redactor.maskEmail(email),       // "j***@example.com"
    "operation": "vitalsSync",                // Non-PII: no redaction
    "recordCount": pendingCount               // Aggregate count, not PHI
])
```

### Model-Level Protection with @Redacted

Prevent accidental PHI leaks through string interpolation anywhere in the codebase:

```swift
@propertyWrapper
struct Redacted<Value> {
    var wrappedValue: Value
}

extension Redacted: CustomStringConvertible {
    var description: String { "--redacted--" }
}

extension Redacted: CustomDebugStringConvertible {
    var debugDescription: String { "--redacted--" }
}

// Health data models
struct PatientRecord {
    let id: String
    @Redacted var name: String
    @Redacted var dateOfBirth: Date
    @Redacted var diagnosis: String
    @Redacted var medications: [String]
    let lastSyncDate: Date  // Non-PHI, safe to log
}
```

Even if someone accidentally writes `Logger.healthData.info("\(patient)")`, the PHI fields will show as `--redacted--`.

---

## 5. REST API Network Layer with Full Observability

Your async/await networking layer must validate HTTP status codes explicitly. URLSession does not throw for HTTP errors -- a 500 and a 200 both return `(Data, URLResponse)` successfully.

```swift
final class APIClient {
    private let session: URLSession
    private let baseURL: URL

    func request<T: Decodable>(_ endpoint: String, method: String = "GET") async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint)

        // Breadcrumb before the call
        ErrorReporter.shared.addBreadcrumb(
            message: "\(method) \(endpoint)",
            category: "network", level: .info, data: nil
        )

        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        // URLSession does NOT throw for HTTP errors -- you must check yourself
        guard (200...299).contains(httpResponse.statusCode) else {
            Logger.networking.error(
                "\(method, privacy: .public) \(endpoint, privacy: .public) -> HTTP \(httpResponse.statusCode, privacy: .public)"
            )
            throw NetworkError.httpError(
                statusCode: httpResponse.statusCode,
                data: data
            )
        }

        Logger.networking.debug(
            "\(method, privacy: .public) \(endpoint, privacy: .public) -> \(data.count, privacy: .public) bytes"
        )

        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            Logger.networking.error(
                "Decode failed for \(endpoint, privacy: .public): \(error.localizedDescription, privacy: .public)"
            )
            throw error
        }
    }
}
```

**Never log request or response bodies** -- they may contain PHI (vitals, medications, patient data). Log the endpoint path, HTTP method, status code, and byte count only.

### Retry with Exponential Backoff

For transient failures (timeouts, 5xx), retry before reporting to Sentry. Only report after all retries are exhausted to avoid noise:

```swift
func retryWithBackoff<T>(
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
                "Attempt \(attempt, privacy: .public)/\(maxAttempts, privacy: .public) for \(operation, privacy: .public): \(error.localizedDescription, privacy: .public)"
            )
            ErrorReporter.shared.addBreadcrumb(
                message: "Retry attempt \(attempt) failed",
                category: "network", level: .warning,
                data: ["attempt": attempt, "operation": operation]
            )
            if attempt < maxAttempts {
                let delay = min(pow(2, Double(attempt)) * base, 60)
                let jitter = Double.random(in: 0...(delay * 0.5))
                try await Task.sleep(nanoseconds: UInt64((delay + jitter) * 1_000_000_000))
            }
        }
    }
    // All retries exhausted -- now report
    ErrorReporter.shared.recordNonFatal(lastError!, context: [
        "operation": operation,
        "maxAttempts": maxAttempts
    ])
    throw lastError!
}
```

---

## 6. SwiftUI Integration -- Async/Await Error Handling

### The .task {} Trap

SwiftUI's `.task` modifier signature is `@Sendable () async -> Void` -- it does not throw. Errors must be caught explicitly. When a view disappears, `.task` cancels its work by throwing `CancellationError` -- this is normal lifecycle behavior, not a failure.

```swift
struct VitalsView: View {
    @State private var vitals: [VitalReading] = []
    @State private var loadError: Error?
    @EnvironmentObject var errorHandler: ErrorHandler

    var body: some View {
        VitalsListContent(vitals: vitals, error: loadError)
            .task {
                do {
                    vitals = try await vitalsService.fetchLatest()
                } catch is CancellationError {
                    // View disappeared -- expected, do not report
                } catch {
                    loadError = error
                    errorHandler.handle(error, context: "VitalsView.fetchLatest")
                }
            }
    }
}
```

### Centralized ErrorHandler

Route all errors through a single handler that logs, reports, and categorizes:

```swift
@MainActor
final class ErrorHandler: ObservableObject {
    @Published var currentAlert: AlertInfo?

    func handle(_ error: Error, context: String) {
        // 1. Always log
        Logger.ui.error("\(context, privacy: .public): \(error.localizedDescription, privacy: .public)")

        // 2. Always report to Sentry
        ErrorReporter.shared.recordNonFatal(error, context: ["context": context])

        // 3. Route based on category
        if let categorized = error as? CategorizedError {
            switch categorized.category {
            case .retryable:
                currentAlert = AlertInfo(
                    title: "Temporary Issue",
                    message: "Please try again in a moment."
                )
            case .nonRetryable:
                currentAlert = AlertInfo(
                    title: "Something Went Wrong",
                    message: error.localizedDescription
                )
            case .requiresLogout:
                AuthManager.shared.logout()
                currentAlert = AlertInfo(
                    title: "Session Expired",
                    message: "Please sign in again."
                )
            }
        }
    }
}
```

### Error Categorization for Health App Errors

```swift
enum NetworkError: Error, CategorizedError {
    case timeout
    case serverError(Int)
    case unauthorized
    case forbidden
    case notFound
    case decodingFailed(Error)
    case invalidResponse
    case httpError(statusCode: Int, data: Data)

    var category: ErrorCategory {
        switch self {
        case .timeout, .serverError:
            return .retryable
        case .unauthorized:
            return .requiresLogout
        case .notFound, .decodingFailed, .invalidResponse, .httpError, .forbidden:
            return .nonRetryable
        }
    }
}
```

---

## 7. Task {} Safety -- Every Unstructured Task Needs a do/catch

`Task.init` is `@discardableResult`. If code inside throws, the error is silently discarded.

```swift
// WRONG -- error vanishes
func syncHealthRecords() {
    Task {
        try await uploadPendingVitals()  // If this throws, nobody knows
    }
}

// CORRECT -- observable error handling
func syncHealthRecords() {
    Task {
        do {
            try await uploadPendingVitals()
        } catch is CancellationError {
            // Task was cancelled -- normal
        } catch {
            Logger.sync.error("Vitals sync failed: \(error.localizedDescription, privacy: .public)")
            ErrorReporter.shared.recordNonFatal(error, context: ["operation": "vitalsSync"])
        }
    }
}
```

---

## 8. MetricKit -- Catching What Crash Reporters Cannot

In-process crash reporters (Sentry) cannot detect OOM kills, watchdog terminations, or background task timeouts -- the OS sends SIGKILL, which cannot be caught. MetricKit runs out-of-process and observes these.

```swift
import MetricKit

class AppMetrics: NSObject, MXMetricManagerSubscriber {
    static let shared = AppMetrics()

    func startReceiving() {
        MXMetricManager.shared.add(self)
        processDiagnostics(MXMetricManager.shared.pastDiagnosticPayloads)
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        processDiagnostics(payloads)
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            if let exitMetrics = payload.applicationExitMetrics {
                let bg = exitMetrics.backgroundExitData
                let fg = exitMetrics.foregroundExitData
                let oomCount = bg.cumulativeMemoryPressureExitCount
                    + fg.cumulativeMemoryPressureExitCount
                let watchdogCount = bg.cumulativeAppWatchdogExitCount

                if oomCount > 0 || watchdogCount > 0 {
                    forwardToBackend(type: "exitMetrics", data: [
                        "oom": oomCount,
                        "watchdog": watchdogCount,
                        "backgroundTaskTimeout": bg.cumulativeBackgroundTaskAssertionTimeoutExitCount
                    ])
                }
            }
        }
    }

    private func processDiagnostics(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            payload.crashDiagnostics?.forEach { crash in
                forwardToBackend(type: "crash", data: crash.jsonRepresentation())
            }
            payload.hangDiagnostics?.forEach { hang in
                forwardToBackend(type: "hang", data: hang.jsonRepresentation())
            }
        }
    }

    private func forwardToBackend(type: String, data: Any) {
        // Send to your analytics backend
        // Stacks are unsymbolicated -- requires server-side symbolication with dSYMs
    }
}
```

Initialize in your app entry point alongside Sentry:

```swift
@main
struct HealthApp: App {
    init() {
        SentrySDK.start { options in
            options.dsn = "https://your-dsn@sentry.io/project"
            options.enableAutoSessionTracking = true
        }
        AppMetrics.shared.startReceiving()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

---

## 9. Background Sync Error Capture

If your health app syncs data in the background via `BGTaskScheduler`, those failures are invisible by default:

```swift
func handleSync(task: BGProcessingTask) {
    scheduleNextSync()

    task.expirationHandler = {
        Logger.lifecycle.warning("Background sync expired by system")
        ErrorReporter.shared.addBreadcrumb(
            message: "BGTask expired", category: "background", level: .warning, data: nil
        )
        task.setTaskCompleted(success: false)
    }

    Task {
        do {
            try await performHealthDataSync()
            task.setTaskCompleted(success: true)
        } catch {
            Logger.sync.error("Background sync failed: \(error.localizedDescription, privacy: .public)")
            ErrorReporter.shared.recordNonFatal(error, context: ["task": "healthDataSync"])
            task.setTaskCompleted(success: false)
        }
    }
}
```

---

## 10. Privacy Manifests and App Store Compliance

Since May 2024, `PrivacyInfo.xcprivacy` files are enforced during App Store review. Your app must declare use of Required Reason APIs:

- `UserDefaults` usage
- File timestamp APIs
- System boot time APIs
- Disk space APIs

Sentry ships its own privacy manifest that Xcode merges automatically. Verify this is present in your build.

### dSYM Configuration Checklist

Without dSYMs, crash reports show hex addresses instead of function names:

- Build Settings -> Debug Information Format -> "DWARF with dSYM File" for ALL configurations
- Apply to ALL targets (main app, widgets, extensions)
- Add Sentry dSYM upload script in Build Phases
- If you have app extensions (HealthKit background delivery, widgets): initialize Sentry separately in each extension target

---

## 11. Compliance Summary -- What Goes Where

| Data type | os.Logger | Sentry crash reports | Breadcrumbs |
|---|---|---|---|
| Endpoint paths (`/api/v1/vitals`) | `.public` | Yes | Yes |
| HTTP status codes | `.public` | Yes | Yes |
| Error descriptions | `.public` | Yes | Yes |
| Record counts | `.public` | Yes | Yes |
| User IDs | `.private(mask: .hash)` | Via Redactor.maskID only | No |
| Email addresses | `.private(mask: .hash)` | Via Redactor.maskEmail only | No |
| Clinical values (HR, BP, glucose) | **Never log** | **Never include** | **Never include** |
| Medication names | **Never log** | **Never include** | **Never include** |
| Diagnosis/condition codes | **Never log** | **Never include** | **Never include** |
| Auth tokens / API keys | **Never log** | **Never include** | **Never include** |
| Request/response bodies | **Never log** | **Never include** | **Never include** |

---

## 12. Implementation Checklist

1. Create `Logger` extensions with health-domain categories
2. Create `ErrorReporter` protocol and `SentryErrorReporter` implementation
3. Create `Redactor` utility and `@Redacted` property wrapper for health data models
4. Audit all `print()` calls -- replace with appropriate Logger level and privacy annotations
5. Audit all `try?` usages -- convert any touching network, persistence, or auth to `do/catch`
6. Audit all `Task {}` blocks -- ensure `do/catch` wraps any throwing code, with `CancellationError` handled separately
7. Wrap REST API layer with HTTP status validation and breadcrumbs (never log bodies)
8. Add `retryWithBackoff` for transient network failures
9. Inject `ErrorHandler` as `@EnvironmentObject` at the app root for centralized SwiftUI error routing
10. Add MetricKit subscriber for OOM/watchdog detection
11. Verify dSYM configuration for all targets
12. Add `PrivacyInfo.xcprivacy` declarations
13. If using app extensions (widgets, HealthKit background delivery): initialize Sentry separately in each
14. Review Sentry's data residency options for HIPAA -- consider Sentry's Business plan with BAA if you handle actual PHI
