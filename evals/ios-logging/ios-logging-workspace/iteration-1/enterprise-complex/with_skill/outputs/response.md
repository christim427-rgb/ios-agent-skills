# Fixing Missing Extension Crashes in Sentry

## Root Cause

Widget extensions and notification service extensions run in **separate processes** from your main app. The Sentry SDK you initialize in your main app's `AppDelegate` or `@main` struct only monitors that one process. Crashes in extension processes are completely invisible to it because each process has its own address space, signal handlers, and lifecycle.

## Fix: Initialize Sentry Separately in Each Extension

Every extension target needs its own independent `SentrySDK.start` call at its entry point.

### Notification Service Extension

```swift
class NotificationService: UNNotificationServiceExtension {
    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        // Initialize crash SDK for this extension process
        SentrySDK.start { options in
            options.dsn = "https://your-dsn@sentry.io/project"
            options.enableAutoSessionTracking = false // Important for extensions
        }

        // ... handle notification
    }
}
```

### Widget Extension

```swift
@main
struct MyWidget: Widget {
    init() {
        SentrySDK.start { options in
            options.dsn = "https://your-dsn@sentry.io/project"
            options.enableAutoSessionTracking = false
        }
    }

    var body: some WidgetConfiguration {
        // ...
    }
}
```

**Key detail:** Set `enableAutoSessionTracking = false` in extensions. Extensions have short, system-managed lifecycles and session tracking does not apply meaningfully to them.

## Full Extension Checklist

1. **Each extension target needs its own Sentry SDK initialization** -- the main app's `SentrySDK.start` does not cover extensions because they are separate processes.

2. **Each extension target needs dSYM upload in its build phases.** Go to Build Settings for every target (main app, widget extension, notification service extension) and confirm:
   - Debug Information Format is set to **"DWARF with dSYM File"** for all configurations (especially Release).
   - The Sentry dSYM upload build phase script runs for each target, not just the main app. Without this, crash reports from extensions will show hex addresses instead of symbolicated function names.

3. **Use App Groups to share error configuration** between the main app and extensions. This lets you centralize your DSN string and any shared error metadata rather than hardcoding the same values in multiple places.

4. **Monitor memory limits carefully.** Extensions run under much tighter constraints than the main app -- widgets get roughly 50 MB. An out-of-memory kill in a widget will not produce a standard crash report. Use MetricKit's `MXAppExitMetric` to detect these OOM terminations, as they are only visible through out-of-process diagnostics.

## Use an ErrorReporter Abstraction

Rather than calling `SentrySDK` directly throughout your code, wrap it behind a protocol so that both your main app and extensions use the same reporting interface:

```swift
protocol ErrorReporter: Sendable {
    func recordNonFatal(_ error: Error, context: [String: Any])
    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?)
    func setUserID(_ userID: String?)
    func setCustomKey(_ key: String, value: Any)
    func log(_ message: String)
}
```

Implement this with a `SentryErrorReporter` class and set it up in each target's entry point. This gives you vendor independence (you can swap Sentry for another SDK without touching all your error-handling call sites) and makes testing straightforward since you can inject a mock reporter in unit tests.

## Verifying the Fix

After deploying the changes:

1. Trigger a test crash in each extension (e.g., `fatalError("Test widget crash")` in a debug build).
2. Confirm that the crash appears in your Sentry dashboard with fully symbolicated stack traces.
3. Send a test non-fatal error from each extension using `ErrorReporter.shared.recordNonFatal(...)` and verify it shows up under Sentry issues.
4. Check that the Sentry events are tagged with the correct extension target name so you can filter widget crashes from notification extension crashes in the dashboard.

## Summary

The fix comes down to one principle: **each process needs its own crash SDK initialization.** Your main app, widget extension, and notification service extension are three separate processes. Initialize Sentry in all three, ensure dSYMs are uploaded for all three targets, and crashes from extensions will start appearing in your dashboard.
