# MetricKit and Whether to Use It Alongside Sentry

## What is MetricKit?

**MetricKit** is an Apple framework introduced in iOS 13 that collects and delivers on-device diagnostic and performance metrics for your app. It provides two main types of data:

### MXMetricPayload (iOS 13+)
Aggregated performance metrics delivered roughly once per day, covering:
- CPU usage and GPU time
- Memory (peak, average)
- Disk I/O (logical writes)
- App launch time (cold/warm/resume)
- Hang rate and hang duration histograms
- Cellular and Wi-Fi network transfer bytes
- Display metrics (scroll hitches, animation glitches)
- Battery usage (foreground/background, location, audio, etc.)

### MXDiagnosticPayload (iOS 14+)
Detailed diagnostic reports including:
- Crash reports with full stack traces
- Hang diagnostics (main thread blocked)
- Disk write exception diagnostics
- CPU exception diagnostics
- App launch diagnostics (iOS 16+)

## How It Works

You subscribe to `MXMetricManager` by conforming to `MXMetricManagerSubscriber`:

```swift
import MetricKit

class MetricsManager: NSObject, MXMetricManagerSubscriber {

    func startReceiving() {
        MXMetricManager.shared.add(self)
    }

    func didReceive(_ payloads: [MXMetricPayload]) {
        // Delivered approximately once every 24 hours
        for payload in payloads {
            let jsonData = payload.jsonRepresentation()
            // Send to your backend or process locally
        }
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        // Crash reports, hangs, CPU/disk exceptions
        for payload in payloads {
            let jsonData = payload.jsonRepresentation()
            // Send to your backend or process locally
        }
    }
}
```

## Should You Use MetricKit Alongside Sentry?

**Yes, they are complementary and not redundant.** Here is why:

### What Sentry Does Better
- **Real-time crash reporting**: Sentry captures crashes immediately and sends them as soon as the app restarts (or even in the same session for non-fatal errors). MetricKit delivers data with up to a 24-hour delay.
- **Breadcrumbs and context**: Sentry attaches user actions, navigation history, custom tags, and contextual data to each error report. MetricKit provides raw stack traces with no application context.
- **Non-fatal error tracking**: Sentry captures handled exceptions, logged errors, and custom events. MetricKit only reports fatal crashes and system-level exceptions.
- **Release tracking and alerting**: Sentry ties errors to releases, lets you set alert rules, and tracks regression.
- **Cross-platform**: If you have Android, web, or backend services, Sentry provides unified error tracking.

### What MetricKit Does Better
- **System-level performance metrics**: Battery usage breakdowns, cellular vs Wi-Fi data consumption, GPU time, and display metrics like scroll hitch rate are only available through MetricKit.
- **Hang diagnostics**: While Sentry can detect ANRs, MetricKit provides Apple's own hang duration histograms and detailed hang call stacks that are consistent with what Apple sees in Xcode Organizer.
- **Disk write exceptions**: MetricKit reports when your app exceeds disk write limits, something Sentry does not track.
- **CPU exceptions**: Reports when your app uses excessive CPU in the background.
- **No performance overhead**: MetricKit data is collected by the OS itself with zero overhead to your app. Sentry's SDK, while lightweight, does add some instrumentation cost.
- **Consistency with App Store metrics**: MetricKit data aligns with what Apple reports in Xcode Organizer and App Store Connect, making it easier to correlate.

### Recommended Approach

Use both:

1. **Sentry** as your primary crash reporting and error monitoring tool for real-time alerting, breadcrumbs, and developer workflow.
2. **MetricKit** as a supplementary data source for system-level performance metrics that Sentry cannot provide.

A practical pattern is to forward MetricKit payloads through Sentry as custom events or attachments:

```swift
func didReceive(_ payloads: [MXDiagnosticPayload]) {
    for payload in payloads {
        // Let Sentry handle its own crash reporting
        // But forward MetricKit diagnostics as additional context
        SentrySDK.capture(message: "MetricKit Diagnostic") { scope in
            scope.setContext(value: [
                "payload": payload.jsonRepresentation().base64EncodedString()
            ], key: "metrickit")
        }
    }
}

func didReceive(_ payloads: [MXMetricPayload]) {
    for payload in payloads {
        // Forward performance metrics to your analytics backend
        // or attach to Sentry as custom metrics
        let json = payload.jsonRepresentation()
        sendToAnalyticsBackend(json)
    }
}
```

### Caveats

- **MetricKit requires iOS 13+** for metrics and **iOS 14+** for diagnostics. If you support older versions, you need `@available` checks.
- **24-hour delay**: MetricKit is not suitable for real-time monitoring or alerting. It is a retrospective analysis tool.
- **Debug vs Release**: MetricKit diagnostic payloads (crashes, hangs) are only delivered for apps distributed through TestFlight or the App Store, not during local development. You can simulate payloads in Xcode for testing.
- **No user identification**: MetricKit payloads are anonymous and aggregated. You cannot correlate a specific crash to a specific user the way you can with Sentry.

### Comparison Table

| Capability | Sentry | MetricKit |
|---|---|---|
| Real-time crash reporting | Yes | No (24h delay) |
| Breadcrumbs and context | Yes | No |
| Non-fatal errors | Yes | No |
| Battery usage breakdown | No | Yes |
| Scroll hitch rate | No | Yes |
| Hang diagnostics | Partial (ANR) | Yes (detailed) |
| Disk write exceptions | No | Yes |
| CPU exceptions | No | Yes |
| Cross-platform | Yes | Apple only |
| Performance overhead | Minimal | Zero |
| Aligns with App Store data | No | Yes |

### Bottom Line

MetricKit and Sentry serve different purposes. Use Sentry for actionable, real-time error tracking with developer workflow integration. Use MetricKit for Apple-specific system performance metrics that help you optimize battery life, reduce hangs, and track metrics consistent with what Apple reports. Together they give you comprehensive observability into your iOS app.
