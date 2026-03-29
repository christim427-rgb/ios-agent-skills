# What is MetricKit and Should You Use It Alongside Sentry?

## What is MetricKit?

MetricKit is Apple's first-party diagnostic framework (available since iOS 13, with diagnostics from iOS 14+ and immediate delivery from iOS 15+). Its defining characteristic is that it runs **out-of-process** -- meaning it operates in a separate system process from your app. This is critical because it allows MetricKit to observe app terminations that happen outside your app's control.

MetricKit provides two categories of data:

1. **Diagnostic payloads** -- crash call stacks, hang diagnostics (main thread blocked >250ms), excessive disk write diagnostics, and CPU exception diagnostics.
2. **Metric payloads** -- aggregated performance data including application exit metrics that tell you *why* the app was terminated (OOM, watchdog kill, background task timeout, etc.).

## Why MetricKit Catches What Sentry Cannot

In-process crash reporters like Sentry work by installing signal handlers inside your app's process. When a standard crash occurs (segfault, unhandled exception), the signal handler fires and Sentry captures the event. However, there are several termination scenarios where the OS kills your app with `SIGKILL` -- a signal that **cannot be caught by any in-process handler**:

- **OOM (Out of Memory) kills** -- the OS terminates your app when memory pressure is too high
- **Watchdog kills** -- the OS terminates your app for taking too long to respond (e.g., during launch or background task execution)
- **Thermal throttle terminations** -- the device is overheating and the OS kills your app
- **Background task assertion timeouts** -- your background task exceeded its allotted time

Because MetricKit runs in a separate system process, it observes all of these terminations. Sentry can only attempt OOM detection through heuristics (inferring that the previous session ended in an OOM based on circumstantial evidence), which is unreliable compared to MetricKit's direct observation.

## Should You Use Both? Yes.

The recommendation is to use MetricKit **alongside** Sentry, not instead of it. They cover complementary gaps:

| Capability | MetricKit | Sentry |
|---|---|---|
| OOM detection | Yes (direct, out-of-process) | Limited (heuristic-based) |
| Watchdog kills | Yes | No |
| Background terminations | Yes (exit metrics) | No |
| Symbolication | Manual (you must symbolicate on your server using dSYMs) | Automatic |
| User opt-in required | Yes (user must enable "Share with App Developers" in Settings) | No |
| Coverage | Only opted-in users (~20-30% typical) | All users |
| Breadcrumbs | No | Yes |
| Rich context and tags | No | Yes |
| Non-fatal error tracking | No | Yes |
| Real-time alerting | No | Yes |

In the observability stack, they occupy different layers:

```
Presentation Layer  -> SwiftUI error state + centralized ErrorHandling
Application Layer   -> ErrorReporter protocol (abstracts Sentry/Crashlytics)
Logging Layer       -> os.Logger with subsystem/category and privacy annotations
Diagnostics Layer   -> MetricKit (OOM, watchdog kills, hangs -- out-of-process)
Crash Layer         -> Sentry (rich context, breadcrumbs, automatic symbolication)
```

## How to Set It Up

Create a MetricKit subscriber and register it at app launch:

```swift
import MetricKit

class AppMetrics: NSObject, MXMetricManagerSubscriber {
    static let shared = AppMetrics()

    func startReceiving() {
        MXMetricManager.shared.add(self)
        // iOS 15+: process any pending diagnostics immediately
        processDiagnostics(MXMetricManager.shared.pastDiagnosticPayloads)
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        processDiagnostics(payloads)
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        processMetrics(payloads)
    }

    private func processDiagnostics(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            payload.crashDiagnostics?.forEach { crash in
                forwardToBackend(type: "crash", data: crash.jsonRepresentation())
            }
            payload.hangDiagnostics?.forEach { hang in
                forwardToBackend(type: "hang", data: hang.jsonRepresentation())
            }
            payload.diskWriteExceptionDiagnostics?.forEach { diskWrite in
                forwardToBackend(type: "diskWrite", data: diskWrite.jsonRepresentation())
            }
            payload.cpuExceptionDiagnostics?.forEach { cpu in
                forwardToBackend(type: "cpuException", data: cpu.jsonRepresentation())
            }
        }
    }

    private func processMetrics(_ payloads: [MXMetricPayload]) {
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

    private func forwardToBackend(type: String, data: Any) {
        // Send to your analytics backend
        // Note: stacks are unsymbolicated -- requires server-side symbolication with dSYMs
    }
}
```

Initialize it in your app entry point:

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

## Key Considerations

1. **MetricKit stacks are unsymbolicated.** You need to set up server-side symbolication using dSYMs. Make sure your build settings have Debug Information Format set to "DWARF with dSYM File" for all targets.

2. **Coverage is limited to opted-in users.** Only users who have enabled "Share with App Developers" in their device settings will send MetricKit data. This is typically a minority of your user base, so treat MetricKit data as a statistical sample rather than a complete picture.

3. **Do not use MetricKit crash diagnostics as a replacement for Sentry crash reporting.** Use MetricKit specifically for the things Sentry cannot see: OOM counts, watchdog kills, background termination breakdowns, and hang diagnostics. Let Sentry handle standard crashes where it provides superior context (breadcrumbs, tags, user info, automatic symbolication).

4. **Key diagnostic types to monitor:**
   - `MXCrashDiagnostic` -- crash stacks (unsymbolicated)
   - `MXHangDiagnostic` -- main thread hangs exceeding 250ms
   - `MXDiskWriteExceptionDiagnostic` -- excessive disk I/O
   - `MXCPUExceptionDiagnostic` -- excessive CPU usage
   - `applicationExitMetrics` -- counts of each termination reason

## Summary

MetricKit and Sentry serve different purposes and together provide comprehensive observability. Sentry gives you rich, real-time crash reporting with breadcrumbs and context for all users. MetricKit gives you visibility into the invisible killers -- OOM terminations, watchdog kills, and background terminations -- that no in-process crash reporter can detect. Use both.
