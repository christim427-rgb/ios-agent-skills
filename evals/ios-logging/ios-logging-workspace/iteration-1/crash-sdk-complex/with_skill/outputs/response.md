# Why Crashes Disappear When Running Both Sentry and Crashlytics

Running Sentry and Crashlytics simultaneously is the root cause. There are two distinct problems: signal handler conflicts between the SDKs, and an entire category of terminations that neither SDK can detect.

## Problem 1: Signal Handler Conflicts (Fatal Crashes Lost)

Both Sentry and Crashlytics install handlers for POSIX signals (SIGABRT, SIGSEGV, SIGBUS, etc.) and both call `NSSetUncaughtExceptionHandler`. The OS only supports **one handler per signal** — the second registration silently replaces the first.

The result depends on SDK initialization order:

- If Sentry initializes last, it receives fatal signals; Crashlytics misses them.
- If Crashlytics initializes last, it receives fatal signals; Sentry misses them.
- In some race conditions or re-entrant crashes, **neither** captures the report completely, and the crash vanishes from both dashboards.

This is the most likely explanation for crashes disappearing from both dashboards simultaneously.

## Problem 2: OS-Level Kills (Invisible to Both SDKs)

Even if you fix the signal conflict, there is a category of terminations that **no in-process crash reporter can ever catch**:

- **OOM (out-of-memory) kills** — the OS sends SIGKILL, which cannot be caught by any signal handler.
- **Watchdog terminations** — the OS kills your app for taking too long to resume or finish a background task.
- **Thermal kills** — the OS terminates your process under thermal pressure.
- **Background task timeouts** — the system terminates the process when a `BGTask` assertion expires.

Since Sentry and Crashlytics both run inside your app's process, they are terminated along with it. No crash report is generated. Users experience the app vanishing, but neither dashboard shows anything.

## The Fix

### Step 1: Pick ONE Fatal Crash Reporter

Choose one SDK for fatal crash handling and disable crash capture on the other:

```swift
// AppDelegate or @main App init

// Option A: Crashlytics is primary (recommended if you use Firebase ecosystem)
FirebaseApp.configure()  // Crashlytics captures fatals automatically

SentrySDK.start { options in
    options.dsn = "your-dsn"
    options.enableCrashHandler = false  // Disable Sentry's signal handlers
    // Sentry still captures non-fatals, breadcrumbs, and performance data
}

// Option B: Sentry is primary (recommended for standalone apps)
SentrySDK.start { options in
    options.dsn = "your-dsn"
    // Sentry captures fatals
}

FirebaseApp.configure()
// Use Crashlytics only for non-fatal recording and logs
```

### Step 2: Use an ErrorReporter Abstraction

Do not scatter SDK calls throughout the codebase. Create a protocol so both SDKs receive non-fatal errors and breadcrumbs consistently:

```swift
protocol ErrorReporter: Sendable {
    func recordNonFatal(_ error: Error, context: [String: Any])
    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?)
    func setUserID(_ userID: String?)
    func setCustomKey(_ key: String, value: Any)
    func log(_ message: String)
}
```

Then use a composite that forwards to both:

```swift
final class CompositeErrorReporter: ErrorReporter {
    private let reporters: [ErrorReporter]

    init(_ reporters: ErrorReporter...) {
        self.reporters = reporters
    }

    func recordNonFatal(_ error: Error, context: [String: Any]) {
        reporters.forEach { $0.recordNonFatal(error, context: context) }
    }

    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?) {
        reporters.forEach { $0.addBreadcrumb(message: message, category: category, level: level, data: data) }
    }

    // ... delegate all methods to both reporters
}
```

This way both dashboards get non-fatal errors and breadcrumbs, but only one handles fatal signal capture.

### Step 3: Add MetricKit for OS-Level Kills

MetricKit runs **out-of-process** in a separate system daemon. It detects the terminations that neither Sentry nor Crashlytics can see:

```swift
import MetricKit

class AppMetrics: NSObject, MXMetricManagerSubscriber {
    static let shared = AppMetrics()

    func startReceiving() {
        MXMetricManager.shared.add(self)
        // iOS 15+: process any diagnostics from previous sessions immediately
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
                    // Forward to your backend — these are crashes
                    // that Sentry and Crashlytics will never report
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
        // Note: MetricKit stacks are unsymbolicated —
        // you need server-side symbolication with dSYMs
    }
}
```

Initialize it at app launch:

```swift
@main
struct MyApp: App {
    init() {
        AppMetrics.shared.startReceiving()
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }
}
```

**MetricKit limitation**: It only covers users who have opted into "Share with App Developers" in Settings, so coverage is partial. But it is the only way to detect OOM and watchdog kills.

### Step 4: Verify dSYMs for All Targets

Without dSYM files, crash reports from any source show hex addresses instead of function names. Verify this for every target in your project (main app, extensions, widgets):

- Build Settings > Debug Information Format > **"DWARF with dSYM File"** for Release (and all other configurations)
- Add the dSYM upload build phase script for your primary crash SDK
- Bitcode is deprecated since Xcode 14, so local dSYMs are authoritative

### Step 5: Note Crashlytics Non-Fatal Limit

Crashlytics stores only the **8 most recent non-fatal exceptions per session**. If your app reports many non-fatals per session, earlier ones are silently dropped. If you see gaps in Crashlytics non-fatal data, this limit is likely the cause. Consider sampling or deduplication on the Crashlytics side if volume is high.

## Summary

| Problem | Cause | Fix |
|---|---|---|
| Fatal crashes missing from one or both dashboards | Signal handler conflict between dual SDKs | Disable crash handler on the secondary SDK |
| OOM / watchdog kills not reported anywhere | In-process reporters die with the app | Add MetricKit (out-of-process) |
| Crash stacks are unsymbolicated | Missing dSYMs | Set "DWARF with dSYM File" on all targets, upload dSYMs |
| Non-fatals missing from Crashlytics | 8 per-session limit | Deduplicate or sample before recording |

The correct observability stack is:

```
Presentation Layer  -> SwiftUI error state + centralized ErrorHandling
Application Layer   -> ErrorReporter protocol (abstracts Sentry + Crashlytics)
Logging Layer       -> os.Logger with subsystem/category and privacy annotations
Diagnostics Layer   -> MetricKit (OOM, watchdog kills, hangs — out-of-process)
Crash Layer         -> One primary SDK for fatals (Sentry OR Crashlytics) + dSYMs
```
