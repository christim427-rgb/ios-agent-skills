# Sentry vs Crashlytics for iOS Crash Reporting

## Short Answer

It depends on your project's ecosystem. If you are already using Firebase (Auth, Firestore, Push Notifications), go with **Firebase Crashlytics**. If you are building a standalone app or want richer error observability, go with **Sentry**.

## Decision Framework

```
What ecosystem is the project in?
|-- Firebase-heavy (Auth, Firestore, Push) --> Firebase Crashlytics (free, tight integration)
|-- Standalone / wants rich observability  --> Sentry (best error context, breadcrumbs, performance)
|-- Needs product analytics + errors       --> Sentry (crashes) + PostHog (analytics, session replay)
|-- Enterprise / custom                    --> Sentry or Datadog + Google Analytics for funnels
```

## Trade-offs

### Firebase Crashlytics

**Advantages:**
- Completely free with no usage caps
- Tight integration with the Firebase ecosystem (Auth, Firestore, Remote Config, Analytics)
- Simple setup if Firebase is already in the project
- Automatic dSYM upload via Firebase CLI or build phase script

**Limitations:**
- Stores only the **8 most recent non-fatal exceptions per session**. Older ones are silently dropped. If your app logs many non-fatals per session, you will lose data unless you implement sampling or deduplication.
- Breadcrumbs are plain strings only -- no structured data support. You cannot attach key-value metadata to individual breadcrumbs the way Sentry allows.
- Less granular error context compared to Sentry (no scoped extras per-capture, no rich breadcrumb categories with structured data)
- Querying and search capabilities in the Firebase console are more limited than Sentry's issue search and event filtering
- CLI-based tooling (`firebase crashlytics:*`) for automation, but no MCP server for direct AI-assistant integration

### Sentry

**Advantages:**
- Best-in-class error context: scoped extras, structured breadcrumbs with categories and key-value data, and rich event search
- No per-session cap on non-fatal errors
- Performance monitoring (transactions, spans) built into the same SDK
- MCP server available, meaning your AI coding assistant can query issues, search events, and pull stack traces and breadcrumb trails directly during debugging sessions
- Better suited for standalone apps without Firebase dependencies

**Limitations:**
- Paid beyond the free tier (event quotas apply)
- Adds a dependency unrelated to Firebase if you are already in that ecosystem
- Slightly more configuration surface area (DSN, options, integrations)

## Critical Rule: Never Run Both as Fatal Crash Reporters

Running Sentry and Crashlytics simultaneously for fatal crash reporting causes **signal handler conflicts**. Both SDKs install handlers for SIGABRT, SIGSEGV, SIGBUS, and other signals. Only the last handler registered receives the signal. `NSSetUncaughtExceptionHandler` supports exactly one handler -- the second call replaces the first.

If you must use both SDKs (for example, Crashlytics for crashes and Sentry for non-fatal error context):

1. Pick one as the **primary fatal crash reporter**
2. Disable crash handling on the secondary -- for example, set `options.enableCrashHandler = false` on Sentry
3. Use the secondary only for non-fatal capture, breadcrumbs, and analytics

## Implementation Approach

Regardless of which SDK you choose, never call Sentry or Crashlytics APIs directly throughout your codebase. Use a protocol-based abstraction:

```swift
protocol ErrorReporter: Sendable {
    func recordNonFatal(_ error: Error, context: [String: Any])
    func addBreadcrumb(message: String, category: String, level: BreadcrumbLevel, data: [String: Any]?)
    func setUserID(_ userID: String?)
    func setCustomKey(_ key: String, value: Any)
    func log(_ message: String)
}
```

This `ErrorReporter` protocol enables:
- **Testability** -- mock it in unit tests without importing any SDK
- **Vendor swapping** -- switch from Crashlytics to Sentry (or vice versa) by changing one concrete implementation
- **Composite reporting** -- wrap multiple backends in a `CompositeErrorReporter` when you need to send non-fatals to more than one service

Then implement `SentryErrorReporter` or `CrashlyticsErrorReporter` as the concrete type, and inject it at app startup.

## dSYMs Are Non-Negotiable

Whichever SDK you choose, without dSYM files your crash reports will show hex addresses instead of function names. Make sure:

- Build Settings -> Debug Information Format is set to **"DWARF with dSYM File"** for all configurations (including Release)
- This applies to **all targets** (main app, extensions, widgets, watch app)
- Add the SDK's dSYM upload script in Build Phases
- Bitcode is deprecated since Xcode 14, so local dSYMs are authoritative

## Non-Fatal Errors Matter More Than Crashes

Crashes affect roughly 1-2% of sessions. Non-fatal errors can silently affect 10-30%+ of sessions. Every `catch` block that handles an error should call `recordNonFatal` through your `ErrorReporter` abstraction. This is where the Crashlytics 8-per-session limit becomes a real concern -- if your app is chatty with non-fatals, Sentry is the safer choice.

## Recommendation Summary

| Factor | Crashlytics | Sentry |
|--------|-------------|--------|
| Cost | Free | Free tier, paid at scale |
| Firebase integration | Native | Separate |
| Non-fatal cap | 8 per session | None |
| Breadcrumb richness | Plain strings | Structured with categories and data |
| AI-assistant integration | CLI tools | MCP server (query issues, events, traces) |
| Performance monitoring | Separate (Firebase Performance) | Built-in |

Pick Crashlytics if Firebase is your backbone. Pick Sentry if observability depth and non-fatal volume matter to you.
