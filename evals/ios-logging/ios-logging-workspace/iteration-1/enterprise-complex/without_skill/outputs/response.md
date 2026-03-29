# Fixing Sentry Crash Reporting in Widget and Notification Service Extensions

## The Problem

App extensions (Widget Extensions, Notification Service Extensions, etc.) run in **separate processes** from the main app. This is the root cause: Sentry is likely only initialized in the main app target, so crashes in extension processes are never captured.

## Key Issues to Address

### 1. Initialize Sentry in Each Extension Target

Each extension has its own entry point and runs in its own process. You must call `SentrySDK.start` in every extension that you want crash reporting for.

**For a Widget Extension (TimelineProvider-based):**

In your widget's main entry point or `TimelineProvider`, initialize Sentry early. If using SwiftUI widget lifecycle (`@main` struct), you can use an `init()`:

```swift
import Sentry
import WidgetKit
import SwiftUI

@main
struct MyWidget: Widget {
    init() {
        SentrySDK.start { options in
            options.dsn = "https://your-dsn@sentry.io/project-id"
            options.debug = false
            // Use a lower sample rate for extensions to reduce overhead
            options.sampleRate = 1.0
            options.enableAutoSessionTracking = false
        }
    }

    var body: some WidgetConfiguration {
        // ...
    }
}
```

**For a Notification Service Extension:**

Initialize in the `didReceive(_:withContentHandler:)` method or in the `init()` of your `UNNotificationServiceExtension` subclass:

```swift
import Sentry
import UserNotifications

class NotificationService: UNNotificationServiceExtension {
    override init() {
        super.init()
        SentrySDK.start { options in
            options.dsn = "https://your-dsn@sentry.io/project-id"
            options.debug = false
            options.enableAutoSessionTracking = false
        }
    }

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        // Your notification handling code
    }

    override func serviceExtensionTimeWillExpire() {
        // Flush Sentry before the extension is killed
        SentrySDK.flush(timeout: 2.0)
    }
}
```

### 2. Add the Sentry SDK to Each Extension Target

In your Xcode project, make sure the Sentry library is linked to each extension target, not just the main app:

- **If using Swift Package Manager:** Go to each extension target's "Frameworks, Libraries, and Embedded Content" section and add the `Sentry` package product.
- **If using CocoaPods:** Add `pod 'Sentry'` to each extension target in your `Podfile`:

```ruby
target 'MyApp' do
  pod 'Sentry'
end

target 'MyWidgetExtension' do
  pod 'Sentry'
end

target 'MyNotificationServiceExtension' do
  pod 'Sentry'
end
```

- **If using Carthage:** Ensure the Sentry framework is embedded in each extension target.

### 3. Use Distinct Environment or Tags to Differentiate Crashes

To tell apart crashes from the main app vs. extensions in your Sentry dashboard, set the `environment` or use tags:

```swift
SentrySDK.start { options in
    options.dsn = "https://your-dsn@sentry.io/project-id"
    options.environment = "widget-extension"  // or "notification-service-extension"
    // Or use a tag approach:
    options.beforeSend = { event in
        event.tags?["app.component"] = "widget-extension"
        return event
    }
}
```

### 4. Handle Extension Memory and Lifecycle Constraints

Extensions have strict memory limits (typically around 30-50 MB for widgets, even less for notification service extensions) and short execution windows. Adjust Sentry configuration accordingly:

```swift
SentrySDK.start { options in
    options.dsn = "https://your-dsn@sentry.io/project-id"

    // Disable features that consume memory or are not relevant in extensions
    options.enableAutoSessionTracking = false
    options.enableAutoPerformanceTracing = false
    options.enableUIViewControllerTracing = false
    options.enableNetworkTracking = false
    options.enableFileIOTracing = false
    options.enableSwizzling = false
    options.enableAppHangTracking = false
    options.enableCaptureFailedRequests = false

    // Attach fewer breadcrumbs
    options.maxBreadcrumbs = 20

    // Lower sample rate if needed
    options.tracesSampleRate = 0
}
```

### 5. Flush Events Before Extension Termination

Extensions can be terminated abruptly by the system. Always call `SentrySDK.flush(timeout:)` before the extension completes its work so that pending events are sent:

```swift
override func serviceExtensionTimeWillExpire() {
    SentrySDK.flush(timeout: 2.0)
    // Deliver whatever you have
    if let contentHandler = contentHandler, let bestAttemptContent = bestAttemptContent {
        contentHandler(bestAttemptContent)
    }
}
```

For widgets, there is less direct lifecycle control, but Sentry should be able to send events on the next timeline reload if the crash is captured to disk.

### 6. Upload dSYMs for All Targets

Sentry needs debug symbols (dSYMs) to symbolicate crash reports. Make sure you are uploading dSYMs for every target, not just the main app:

- If using `sentry-cli` in a build phase, ensure it runs for each target, or runs once and uploads all dSYMs from the build directory.
- If uploading manually or through CI, collect dSYMs from all targets:

```bash
# Upload all dSYMs from the archive
sentry-cli upload-dif --include-sources ./Build/Products/
```

- Verify in Xcode Build Settings that `DEBUG_INFORMATION_FORMAT` is set to `dwarf-with-dsym` for each extension target in Release configuration.

### 7. Shared DSN Configuration

To avoid hardcoding the DSN in multiple places, consider using an App Group or a shared configuration file:

```swift
// In a shared framework or file included in all targets
enum SentryConfig {
    static let dsn = "https://your-dsn@sentry.io/project-id"

    static func start(component: String) {
        SentrySDK.start { options in
            options.dsn = Self.dsn
            options.environment = component
            options.enableAutoSessionTracking = false
            options.enableAutoPerformanceTracing = false

            if component != "main-app" {
                // Lighter config for extensions
                options.enableSwizzling = false
                options.enableUIViewControllerTracing = false
                options.enableAppHangTracking = false
                options.tracesSampleRate = 0
                options.maxBreadcrumbs = 20
            }
        }
    }
}
```

Then in each target:

```swift
// Main app
SentryConfig.start(component: "main-app")

// Widget
SentryConfig.start(component: "widget-extension")

// Notification Service
SentryConfig.start(component: "notification-service-extension")
```

## Verification Checklist

1. **Sentry SDK is linked** to each extension target (not just the main app).
2. **`SentrySDK.start` is called** in each extension's initialization path.
3. **dSYMs are uploaded** for all targets (main app + extensions) with `dwarf-with-dsym` format enabled.
4. **`SentrySDK.flush`** is called before extension work completes, especially in `serviceExtensionTimeWillExpire()`.
5. **Memory-heavy features are disabled** in extension configurations to stay within system limits.
6. **Environment or tags** are set so you can filter crashes by component in the Sentry dashboard.
7. **Test by triggering a crash** in the widget or notification extension (e.g., `fatalError("Test crash")`) and confirming it appears in Sentry.

## Common Pitfalls

- **Forgetting to link the framework:** The extension will compile but Sentry simply will not be present at runtime, causing a silent failure or dylib crash.
- **Not uploading extension dSYMs:** Crashes appear in Sentry as unsymbolicated hex addresses.
- **Extension killed before flush:** If Sentry does not have time to send events, they may be lost. The SDK stores events on disk and attempts to send them on the next launch, but extensions may not relaunch frequently.
- **Using the same session tracking:** Extensions should have `enableAutoSessionTracking = false` since they do not have the same lifecycle concept as the main app and can skew session/crash-free rate metrics.
