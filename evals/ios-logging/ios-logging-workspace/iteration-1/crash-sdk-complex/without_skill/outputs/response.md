# Missing Crashes in Sentry and Crashlytics: Diagnosis and Fixes

When running both Sentry and Crashlytics in the same iOS app, crashes can silently disappear from both dashboards. This is a well-known problem rooted in how crash reporting SDKs work at a low level.

## Root Cause: Signal Handler Conflicts

Both Sentry and Crashlytics install their own **Mach exception handlers** and **UNIX signal handlers** (for SIGSEGV, SIGABRT, SIGBUS, etc.) to intercept crashes. The problem is that only one handler can be the "active" handler for a given signal at a time. When two SDKs compete:

1. The SDK initialized **last** overwrites the handler installed by the first.
2. If the last SDK's handler does not properly forward (chain) to the previous handler, the first SDK never sees the crash.
3. In some scenarios, neither SDK successfully captures the crash -- for example, if one SDK's handler crashes itself during processing, or if chaining is broken.

## Common Scenarios Where Crashes Go Missing

### 1. Initialization Order Issues

```swift
// AppDelegate.swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions ...) -> Bool {
    FirebaseApp.configure()       // Crashlytics installs its handlers
    SentrySDK.start { options in  // Sentry overwrites Crashlytics handlers
        options.dsn = "..."
    }
}
```

Sentry initializes second, so it owns the signal handlers. If Sentry's handler does not chain back to Crashlytics, Crashlytics never sees the crash. And if Sentry itself has an issue uploading the report, the crash is lost entirely.

### 2. Out-of-Memory (OOM) Crashes

Neither Sentry nor Crashlytics reliably catches OOM terminations. The OS kills the process with **SIGKILL**, which cannot be caught by any signal handler. Both SDKs use heuristics (detecting that the app was in the foreground, not upgraded, not backgrounded, etc.) to infer OOM, but these heuristics are unreliable and often miss events.

### 3. Watchdog Terminations (0x8BADF00D)

If the main thread is blocked for too long (typically 20+ seconds), the iOS watchdog kills the app. This also uses SIGKILL and is uncatchable. These will not appear in either dashboard unless the SDK has specific watchdog detection heuristics.

### 4. Crashes During SDK Initialization

If the app crashes before both SDKs have finished initializing (e.g., a crash in `application(_:didFinishLaunchingWithOptions:)` before the SDK `start` call), neither SDK has its handlers installed yet.

### 5. Background Crashes

Crashes that occur when the app is in the background or during background tasks may not be reported if the SDK does not get a chance to write the crash report to disk, or if the next foreground session does not trigger the upload.

### 6. Corrupted Crash Reports

If the app crashes in a state where the file system is under pressure or the crash happens during a write operation, the on-disk crash report may be corrupted. The SDK will discard it on next launch.

### 7. NSException Handling Conflicts

Both SDKs set a global `NSUncaughtExceptionHandler`. Only one can be active. If the second SDK does not call the previously installed handler, the first SDK misses all Objective-C exceptions.

```
NSSetUncaughtExceptionHandler() // Only one handler is active globally
```

## How to Fix It

### Option A: Pick One Crash Reporter (Recommended)

The most reliable solution is to use **a single crash reporting SDK** for crash capture. Running two crash reporters is inherently fragile.

- Use **Sentry** for crash reporting AND error tracking.
- OR use **Crashlytics** for crash reporting and Sentry only for non-fatal error/event tracking.

If you use Sentry for everything, disable Crashlytics crash reporting:

```swift
// In your Info.plist, disable Crashlytics auto-collection:
// FirebaseCrashlyticsCollectionEnabled = false

// Or in code before FirebaseApp.configure():
// Then enable only the parts of Firebase you need (Analytics, etc.)
```

### Option B: Configure Proper Handler Chaining

If you must use both, ensure proper initialization order and chaining:

```swift
func application(_ application: UIApplication, didFinishLaunchingWithOptions ...) -> Bool {
    // Initialize Sentry FIRST
    SentrySDK.start { options in
        options.dsn = "..."
        // Sentry will install its handlers first
    }

    // Initialize Firebase/Crashlytics SECOND
    // Crashlytics is designed to chain to previously installed handlers
    FirebaseApp.configure()

    return true
}
```

Crashlytics generally does a better job of chaining to previously installed signal handlers than Sentry does. So initializing Sentry first and Crashlytics second tends to work better for dual-reporting.

### Option C: Disable Sentry's Crash Handling

Use Sentry only for non-fatal events, breadcrumbs, and performance monitoring. Let Crashlytics own crash reporting:

```swift
SentrySDK.start { options in
    options.dsn = "..."
    options.enableCrashHandler = false  // Sentry won't install signal handlers
    // Sentry still captures breadcrumbs, non-fatal events, performance
}

FirebaseApp.configure() // Crashlytics owns all crash reporting
```

### Additional Fixes

#### Ensure dSYMs Are Uploaded

Missing symbolication is often mistaken for missing crashes. The crash may be reported but appears as unsymbolicated garbage that is hard to find.

```bash
# For Sentry - upload dSYMs via sentry-cli
sentry-cli debug-files upload --org YOUR_ORG --project YOUR_PROJECT path/to/dSYMs

# For Crashlytics - ensure the build phase script is present
# ${BUILD_DIR%/Build/*}/SourcePackages/checkouts/firebase-ios-sdk/Crashlytics/run
```

If using Bitcode (pre-Xcode 14), download dSYMs from App Store Connect and upload them manually to both services.

#### Handle Crashes Early in App Lifecycle

Move SDK initialization as early as possible:

```swift
// Consider initializing in main.swift before UIApplicationMain
// or at the very start of didFinishLaunchingWithOptions

// If you have a complex app startup, crashes before SDK init are invisible
```

#### Check Network and Upload Conditions

- Crash reports are stored on disk and uploaded on the **next app launch**.
- If the user uninstalls the app before launching again, the report is lost.
- If the device has no network on the next launch, some SDKs will retry; others may not.
- Verify that your DSN (Sentry) and GoogleService-Info.plist (Crashlytics) are correctly configured.

#### Test Your Setup

Force a test crash to verify both dashboards receive it:

```swift
// Test Crashlytics
Crashlytics.crashlytics().log("Testing crash reporting")
fatalError("Test crash for verification")

// Or for a signal-based crash:
// abort()
```

After the crash, relaunch the app with network access and check both dashboards within a few minutes.

## Summary

| Problem | Solution |
|---|---|
| Signal handler conflicts | Use one crash SDK, or init Sentry first then Crashlytics |
| OOM / Watchdog kills | Accept these are not catchable; use MetricKit for post-hoc data |
| Crash before SDK init | Move initialization as early as possible |
| Missing dSYMs | Automate dSYM upload in CI/CD |
| NSException handler conflict | Use one crash SDK, or ensure chaining |
| Background crash not uploaded | Cannot fully solve; minimize by ensuring quick upload on launch |

The single most impactful fix is to **choose one SDK for crash reporting** and use the other only for supplementary telemetry (non-fatal events, performance, breadcrumbs). Dual crash reporters are a constant source of subtle data loss.
