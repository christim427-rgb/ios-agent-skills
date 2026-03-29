# HIPAA-Compliant Logging Strategy for a SwiftUI + async/await Health Tech App

## 1. Core Principles

When building a logging system for a HIPAA-adjacent health tech app, three concerns must be balanced:

- **Debuggability**: Engineers need enough context to diagnose issues in production.
- **Compliance**: Protected Health Information (PHI) and Personally Identifiable Information (PII) must never appear in logs that leave the device or persist unencrypted.
- **Performance**: Logging must not degrade the user experience, especially in async/concurrent contexts.

---

## 2. Use Apple's Unified Logging (os.Logger)

Apple's `os.Logger` (available since iOS 14) is the recommended foundation. It provides:

- **Privacy annotations** built into the API (`%{public}` vs `%{private}`)
- **Log levels** (debug, info, notice, error, fault)
- **High performance** with deferred string interpolation
- **Integration with Console.app and Instruments** for on-device debugging

### 2.1 Define Subsystem and Category Constants

```swift
import os

enum LogSubsystem {
    static let app = "com.yourcompany.healthapp"
}

enum LogCategory: String {
    case network = "Network"
    case auth = "Auth"
    case sync = "DataSync"
    case ui = "UI"
    case vitals = "Vitals"
    case storage = "Storage"
}

extension Logger {
    static func logger(for category: LogCategory) -> Logger {
        Logger(subsystem: LogSubsystem.app, category: category.rawValue)
    }

    static let network = logger(for: .network)
    static let auth = logger(for: .auth)
    static let sync = logger(for: .sync)
    static let ui = logger(for: .ui)
    static let vitals = logger(for: .vitals)
    static let storage = logger(for: .storage)
}
```

### 2.2 Privacy-Aware Logging

The key HIPAA-relevant feature of `os.Logger` is its privacy model. By default, dynamic values are redacted in log archives unless explicitly marked `public`.

```swift
// GOOD: Patient ID is redacted by default in log collection
Logger.vitals.info("Fetching vitals for patient \(patientId, privacy: .private)")

// GOOD: HTTP status codes are safe to expose
Logger.network.error("Request failed with status \(statusCode, privacy: .public)")

// GOOD: Use hashed values for correlation without exposing PHI
Logger.sync.info("Syncing record \(recordId.hashedForLogging, privacy: .public)")

// BAD: Never do this
Logger.vitals.info("Patient name: \(patient.fullName, privacy: .public)")
```

**Rule**: Any value that could identify a patient or contain health data MUST use `.private` (the default) or `.sensitive`. Only operational metadata (status codes, endpoint paths without query params, durations, counts) should be `.public`.

---

## 3. Data Classification for Logging

Create an explicit classification system so developers know what can and cannot be logged:

| Classification | Examples | Logging Rule |
|---|---|---|
| **PHI** | Patient name, DOB, diagnoses, vitals, medications | NEVER log in plaintext. Use `.private` or redact entirely. |
| **PII** | Email, phone, address, device identifiers | Use `.private`. Redact from any exported logs. |
| **Operational** | HTTP status, endpoint path, latency, error codes | Safe to log as `.public`. |
| **Debug** | View lifecycle, state transitions, feature flags | Safe to log at `.debug` level. Stripped in release by default. |

### 3.1 Redaction Helper

```swift
protocol LogRedactable {
    var redactedDescription: String { get }
}

extension String {
    var hashedForLogging: String {
        let data = Data(self.utf8)
        let hash = SHA256.hash(data: data)
        return hash.prefix(8).map { String(format: "%02x", $0) }.joined()
    }
}

// Use for correlation without exposing real IDs
struct PatientReference: LogRedactable {
    let id: String
    var redactedDescription: String { id.hashedForLogging }
}
```

---

## 4. Network Layer Logging

For your REST API layer, log request/response metadata without capturing bodies that may contain PHI.

### 4.1 Request/Response Logger

```swift
actor NetworkLogger {
    private static let logger = Logger.network

    static func logRequest(_ request: URLRequest, correlationId: String) {
        let method = request.httpMethod ?? "UNKNOWN"
        let path = request.url?.path ?? "unknown"
        // Log the path but NOT query parameters (may contain PHI)
        logger.info(
            "[\(correlationId, privacy: .public)] \(method, privacy: .public) \(path, privacy: .public)"
        )
    }

    static func logResponse(
        _ response: HTTPURLResponse,
        duration: Duration,
        correlationId: String
    ) {
        let status = response.statusCode
        logger.info(
            """
            [\(correlationId, privacy: .public)] \
            Status: \(status, privacy: .public) \
            Duration: \(duration.formatted(), privacy: .public)
            """
        )

        if status >= 400 {
            logger.error(
                "[\(correlationId, privacy: .public)] HTTP error \(status, privacy: .public)"
            )
        }
    }

    // NEVER log response bodies in production -- they likely contain PHI
    static func logResponseBody(_ data: Data, correlationId: String) {
        #if DEBUG
        // Only in debug builds, and even then, be careful
        logger.debug(
            "[\(correlationId, privacy: .public)] Body size: \(data.count, privacy: .public) bytes"
        )
        #endif
    }
}
```

### 4.2 Integration with URLSession

```swift
final class APIClient: Sendable {
    private let session: URLSession

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let correlationId = UUID().uuidString.prefix(8).description
        let startTime = ContinuousClock.now

        var urlRequest = endpoint.urlRequest
        urlRequest.addValue(correlationId, forHTTPHeaderField: "X-Correlation-ID")

        NetworkLogger.logRequest(urlRequest, correlationId: correlationId)

        do {
            let (data, response) = try await session.data(for: urlRequest)
            let httpResponse = response as! HTTPURLResponse
            let duration = ContinuousClock.now - startTime

            NetworkLogger.logResponse(httpResponse, duration: duration, correlationId: correlationId)

            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            Logger.network.error(
                "[\(correlationId, privacy: .public)] Failed: \(error.localizedDescription, privacy: .public)"
            )
            throw error
        }
    }
}
```

---

## 5. Structured Error Logging

Create a system for capturing actionable error context without PHI.

```swift
enum AppError: Error {
    case networkFailure(statusCode: Int, endpoint: String, correlationId: String)
    case decodingFailure(type: String, field: String?, correlationId: String)
    case authExpired
    case storageFailure(operation: String)
    case syncConflict(recordHash: String)
}

extension AppError {
    func log() {
        switch self {
        case .networkFailure(let status, let endpoint, let correlationId):
            Logger.network.error(
                "Network failure: \(status, privacy: .public) at \(endpoint, privacy: .public) [\(correlationId, privacy: .public)]"
            )
        case .decodingFailure(let type, let field, let correlationId):
            Logger.sync.error(
                "Decode error: type=\(type, privacy: .public) field=\(field ?? "unknown", privacy: .public) [\(correlationId, privacy: .public)]"
            )
        case .authExpired:
            Logger.auth.warning("Auth token expired, triggering refresh")
        case .storageFailure(let operation):
            Logger.storage.fault("Storage failure during \(operation, privacy: .public)")
        case .syncConflict(let recordHash):
            Logger.sync.warning("Sync conflict on record \(recordHash, privacy: .public)")
        }
    }
}
```

---

## 6. Log Level Strategy

| Level | Use Case | Persisted? | Contains PHI? |
|---|---|---|---|
| `.debug` | Detailed flow tracing, state dumps | No (stripped in release) | Acceptable in DEBUG builds only |
| `.info` | Normal operations: API calls, sync events | Persisted briefly | Never |
| `.notice` | Significant state changes (login, sync complete) | Persisted | Never |
| `.error` | Recoverable failures (network timeout, decode error) | Persisted | Never |
| `.fault` | Unrecoverable failures (database corruption, crash) | Persisted indefinitely | Never |

**Key rule**: `.debug` logs are automatically excluded from `log collect` and sysdiagnose in release builds. Use this level liberally during development.

---

## 7. Async/Await Considerations

### 7.1 Task-Local Correlation IDs

Use `TaskLocal` to propagate correlation IDs through async call chains without passing them as parameters everywhere.

```swift
enum LogContext {
    @TaskLocal static var correlationId: String = "none"
    @TaskLocal static var feature: String = "unknown"
}

// Usage in an async flow
func syncPatientData() async throws {
    try await LogContext.$correlationId.withValue(UUID().uuidString.prefix(8).description) {
        try await LogContext.$feature.withValue("patient-sync") {
            Logger.sync.info(
                "[\(LogContext.correlationId, privacy: .public)] Starting \(LogContext.feature, privacy: .public)"
            )

            let records = try await fetchRecords()
            try await processRecords(records)

            Logger.sync.info(
                "[\(LogContext.correlationId, privacy: .public)] Completed \(LogContext.feature, privacy: .public)"
            )
        }
    }
}
```

### 7.2 Actor-Based Log Buffering (for crash-safe breadcrumbs)

```swift
actor DiagnosticBreadcrumbs {
    static let shared = DiagnosticBreadcrumbs()

    private var breadcrumbs: [(timestamp: Date, message: String)] = []
    private let maxCount = 50

    func add(_ message: String) {
        let entry = (timestamp: Date(), message: message)
        breadcrumbs.append(entry)
        if breadcrumbs.count > maxCount {
            breadcrumbs.removeFirst()
        }
    }

    /// Export breadcrumbs for crash reports -- must be PHI-free
    func export() -> String {
        breadcrumbs.map { "\($0.timestamp.ISO8601Format()): \($0.message)" }
            .joined(separator: "\n")
    }

    func clear() {
        breadcrumbs.removeAll()
    }
}
```

---

## 8. What NOT to Log (HIPAA Checklist)

Enforce this via code review and linter rules:

- Patient names, dates of birth, Social Security numbers
- Diagnosis codes (ICD-10) or descriptions
- Medication names or dosages
- Lab results or vital sign values
- Insurance or billing information
- Full device identifiers (use hashed versions)
- Request/response bodies from clinical API endpoints
- Authentication tokens or credentials
- Full URLs with query parameters (may contain patient IDs)

### 8.1 Compile-Time Enforcement

Use a wrapper type to make it harder to accidentally log PHI:

```swift
@propertyWrapper
struct PHIProtected<Value> {
    var wrappedValue: Value

    var projectedValue: String {
        "<REDACTED>"
    }
}

struct PatientRecord {
    @PHIProtected var name: String
    @PHIProtected var dateOfBirth: Date
    @PHIProtected var diagnosis: String
    let recordId: String  // Operational, safe to log
}

// When someone tries to log:
let patient = PatientRecord(name: "Jane", dateOfBirth: .now, diagnosis: "...", recordId: "abc123")
Logger.vitals.info("Processing record \(patient.recordId, privacy: .public)")
// patient.$name returns "<REDACTED>" if accidentally interpolated
```

---

## 9. Remote/Crash Reporting Integration

If you use a crash reporting service (Crashlytics, Sentry, Datadog, etc.):

### 9.1 Sanitized Breadcrumbs Only

```swift
protocol CrashReporter: Sendable {
    func addBreadcrumb(_ message: String, category: String)
    func recordError(_ error: Error, context: [String: String])
}

extension CrashReporter {
    func addSafeBreadcrumb(_ message: String, category: LogCategory) {
        // Double-check: never send PHI to third-party services
        addBreadcrumb(message, category: category.rawValue)
    }

    func recordSafeError(_ error: AppError) {
        // Only operational context, never PHI
        let context: [String: String]
        switch error {
        case .networkFailure(let status, let endpoint, let correlationId):
            context = [
                "status": "\(status)",
                "endpoint": endpoint,
                "correlationId": correlationId
            ]
        default:
            context = [:]
        }
        recordError(error, context: context)
    }
}
```

### 9.2 Disable Automatic Data Collection

Most third-party SDKs collect data by default. For HIPAA compliance:

- Disable automatic screen name tracking (screen names may reveal health context)
- Disable automatic breadcrumb capture for network requests (bodies may contain PHI)
- Disable user identifier auto-collection
- Use only opaque, hashed user IDs
- Ensure the vendor has signed a Business Associate Agreement (BAA) if processing any PHI

---

## 10. Debug vs. Release Configuration

```swift
enum LoggingConfiguration {
    static func configure() {
        #if DEBUG
        // In debug builds, allow verbose logging to Console.app
        // PHI may appear in .debug level -- acceptable for local dev only
        #else
        // In release builds:
        // - .debug messages are automatically stripped by os.Logger
        // - Ensure no PHI in .info and above
        // - Enable crash breadcrumbs
        // - Configure remote reporting with PHI filters
        #endif
    }
}
```

---

## 11. Audit Logging

HIPAA requires audit trails for access to PHI. This is separate from diagnostic logging:

```swift
actor AuditLogger {
    static let shared = AuditLogger()
    private let logger = Logger(subsystem: LogSubsystem.app, category: "Audit")

    /// Log PHI access events for compliance. These go to your
    /// secure audit backend, NOT to general diagnostic logs.
    func logAccess(
        action: AuditAction,
        resourceType: String,
        resourceHash: String,
        userId: String
    ) async {
        // Send to your secure, HIPAA-compliant audit service
        let event = AuditEvent(
            timestamp: Date(),
            action: action,
            resourceType: resourceType,
            resourceHash: resourceHash,
            userId: userId
        )

        // Log a sanitized version locally for debugging
        logger.notice(
            "Audit: \(action.rawValue, privacy: .public) on \(resourceType, privacy: .public)"
        )

        // Send full event to secure audit backend
        try? await auditService.submit(event)
    }
}

enum AuditAction: String {
    case viewed
    case created
    case updated
    case deleted
    case exported
    case shared
}
```

---

## 12. Testing Your Logging

```swift
// Create a test spy to verify logging behavior
final class LogSpy: @unchecked Sendable {
    private(set) var messages: [String] = []
    private let lock = NSLock()

    func log(_ message: String) {
        lock.withLock { messages.append(message) }
    }

    func assertNoPHI(knownPHI: [String]) {
        for message in messages {
            for phi in knownPHI {
                XCTAssertFalse(
                    message.contains(phi),
                    "PHI leaked in log: found '\(phi)' in '\(message)'"
                )
            }
        }
    }
}
```

---

## 13. Summary Checklist

1. Use `os.Logger` with privacy annotations as the foundation.
2. Classify all data fields as PHI, PII, or Operational before logging.
3. Default to `.private` for all dynamic values; explicitly opt in to `.public` only for operational data.
4. Never log request/response bodies from clinical endpoints.
5. Use correlation IDs (via `@TaskLocal`) for tracing async flows.
6. Use `.debug` level for development-only verbose output.
7. Wrap PHI fields with `@PHIProtected` or similar to prevent accidental logging.
8. Sanitize all data sent to third-party crash/analytics services.
9. Require BAAs from any third-party service that could receive PHI.
10. Implement a separate audit log for PHI access events.
11. Write tests that assert no PHI leakage in log output.
12. Review logging in code reviews with the same scrutiny as security changes.
