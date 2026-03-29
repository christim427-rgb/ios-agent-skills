# Sentry vs Firebase Crashlytics for iOS Crash Reporting

Both Sentry and Firebase Crashlytics are mature, well-regarded crash reporting solutions for iOS. The right choice depends on your team size, budget, existing infrastructure, and how much observability you need beyond just crashes.

---

## Firebase Crashlytics

### Strengths

- **Free and unlimited.** Crashlytics has no usage caps or paid tiers for crash reporting. For indie developers or small teams on a budget, this is a significant advantage.
- **Tight Firebase integration.** If you already use Firebase Analytics, Remote Config, or other Firebase services, Crashlytics fits naturally into that ecosystem. Crash data links to Analytics events automatically.
- **Lightweight SDK.** The SDK is relatively small and has minimal performance overhead.
- **Real-time crash alerts.** The Firebase console shows new crashes quickly, and you can set up alerts via email or PagerDuty.
- **Google-backed.** Long-term maintenance and reliability are generally not a concern.

### Weaknesses

- **Crash-focused only.** Crashlytics is primarily a crash and non-fatal error reporter. It does not handle general-purpose logging, performance traces (that is a separate Firebase Performance product), or breadcrumb trails in the same depth as Sentry.
- **Limited querying.** The Firebase console does not offer the same level of issue search, filtering, or custom dashboards that Sentry provides.
- **No on-premise option.** Data lives on Google servers. If you have strict data residency or compliance requirements, this may be a blocker.
- **Vendor lock-in to Firebase/Google.** Adopting Crashlytics typically means adopting the broader Firebase SDK and Google Analytics, which increases your dependency surface.

---

## Sentry

### Strengths

- **Full observability platform.** Sentry goes well beyond crash reporting. It captures breadcrumbs (user actions leading up to a crash), performance transactions, HTTP request tracing, and custom context. This makes debugging significantly easier.
- **Rich issue management.** Sentry provides robust grouping, deduplication, assignment, and integration with tools like Jira, GitHub Issues, Slack, and PagerDuty. The web UI is powerful for triaging and prioritizing issues.
- **Breadcrumbs and context.** Sentry automatically captures a trail of UI events, network calls, and console logs leading up to a crash. This context is invaluable for reproducing issues.
- **Self-hosted option.** If data residency or compliance matters, you can run Sentry on your own infrastructure.
- **Cross-platform consistency.** If your organization also has Android, web, or backend services, Sentry provides a unified view across all platforms with correlated traces.
- **Performance monitoring built in.** App start times, slow/frozen frames, HTTP request durations, and custom transactions are all part of the same SDK.
- **Open source.** The SDK and the server are open source, giving you transparency and the ability to contribute or fork if needed.

### Weaknesses

- **Cost at scale.** Sentry is free for small volumes (the Developer plan), but the Team and Business plans charge based on event volume. For apps with millions of users, costs can grow.
- **Heavier SDK.** The Sentry SDK is larger than Crashlytics, particularly if you enable performance monitoring and all integrations. This adds to your app binary size.
- **Setup complexity.** Sentry has more configuration options (DSN, sample rates, breadcrumb filters, integrations). This flexibility comes with a steeper initial learning curve.
- **Requires dSYM upload management.** Like Crashlytics, you need to upload dSYMs for symbolication, but the Sentry CLI and fastlane plugin handle this well.

---

## Side-by-Side Comparison

| Aspect | Crashlytics | Sentry |
|---|---|---|
| **Price** | Free | Free tier; paid plans by event volume |
| **Crash reporting** | Excellent | Excellent |
| **Non-fatal errors** | Yes | Yes |
| **Breadcrumbs** | Limited | Rich and automatic |
| **Performance monitoring** | Separate product (Firebase Performance) | Built into the same SDK |
| **Issue management** | Basic | Advanced (assign, link, resolve, regress) |
| **Integrations** | Firebase ecosystem | Jira, GitHub, Slack, PagerDuty, and many more |
| **Self-hosted** | No | Yes |
| **SDK size impact** | Small | Moderate |
| **Cross-platform** | Android, iOS, Flutter, Unity | iOS, Android, web, backend, Flutter, React Native, and more |
| **Data residency** | Google servers only | Cloud or self-hosted |
| **SwiftUI support** | Basic | View hierarchy breadcrumbs, SentrySDK options |
| **SPM support** | Yes | Yes |

---

## Recommendation

- **Choose Crashlytics if** you are a solo developer or small team, you are already invested in the Firebase ecosystem, cost is a primary concern, and you mainly need to know "what crashed and how often."

- **Choose Sentry if** you need deeper debugging context (breadcrumbs, performance data, custom tags), you work on a larger team that benefits from issue assignment and integrations, you need a self-hosted or data-residency-compliant solution, or you want a single observability platform across iOS, Android, and backend.

For most professional iOS teams shipping production apps, Sentry provides meaningfully better debugging workflows that justify the cost. For hobby projects or Firebase-heavy apps, Crashlytics is a solid zero-cost choice.

---

## Basic Integration Examples

### Crashlytics (via SPM)

```swift
// AppDelegate or App init
import FirebaseCrashlytics

FirebaseApp.configure()

// Log a non-fatal error
Crashlytics.crashlytics().record(error: myError)

// Set user identifier for crash reports
Crashlytics.crashlytics().setUserID("user-123")

// Add custom keys
Crashlytics.crashlytics().setCustomValue("premium", forKey: "account_type")
```

### Sentry (via SPM)

```swift
import Sentry

SentrySDK.start { options in
    options.dsn = "https://your-dsn@sentry.io/project-id"
    options.tracesSampleRate = 0.2
    options.enableAutoPerformanceTracing = true
    options.attachScreenshot = true
    options.enableUserInteractionTracing = true
}

// Capture a non-fatal error
SentrySDK.capture(error: myError)

// Add breadcrumb
let crumb = Breadcrumb(level: .info, category: "navigation")
crumb.message = "User opened settings"
SentrySDK.addBreadcrumb(crumb)

// Set user context
SentrySDK.setUser(User(userId: "user-123"))
```

Both SDKs require uploading dSYM files for symbolicated crash reports. Automate this in your CI pipeline using fastlane or the respective CLI tools.
