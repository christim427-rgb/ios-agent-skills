# Logging and GDPR Compliance in iOS Apps

GDPR (and CCPA) compliance in logging is a critical concern for iOS developers because the app publisher is the **data controller** responsible for all data processing -- including what happens inside third-party SDKs like Sentry or Crashlytics. Here is what you need to watch out for.

---

## 1. Know What Counts as Personal Data

GDPR classifies the following as personal information, and logging any of it without proper safeguards is a compliance risk:

- **IP addresses, device IDs (IDFA, IDFV), and behavioral data** are all personal data under GDPR.
- **Email addresses, phone numbers, full names, and government IDs** are obvious PII, but they frequently leak into logs through URL paths (e.g., `/users/john@example.com/profile`), HTTP request/response bodies, database query parameters, and stack traces.

## 2. Never Log These Categories

Certain data should never appear in your logs at all:

- **Authentication data**: passwords, password hashes, JWT/OAuth tokens, refresh tokens, API keys, client secrets, session tokens, CSRF tokens.
- **Personal identifiers**: emails, phone numbers, full names, SSNs, passport numbers, IDFA/IDFV without consent.
- **Sensitive data**: location data (without explicit consent), HealthKit data, financial data (account/card numbers), communication contents (messages, emails).

## 3. Watch for Operational Leaks (Commonly Missed)

These are the sources that most teams overlook:

- **Full HTTP request/response bodies** -- these may contain authorization headers or user data in POST bodies.
- **Database queries with user parameters** -- an unredacted Core Data fault description can expose entity values.
- **URL paths containing emails or user IDs** -- a URL like `/users/john@example.com/profile` logged as-is leaks PII.
- **Stack traces with user data** in variable names or captured closures.

## 4. Use os.Logger Privacy Annotations as Your First Line of Defense

Apple's `os.Logger` redacts dynamic strings by default in production (they appear as `<private>`). You must use explicit privacy annotations on every interpolated value:

- **`privacy: .public`** -- for safe operational data like URL paths, error codes, status codes.
- **`privacy: .private`** -- for user-specific data like IDs, emails, names. These are redacted in production logs.
- **`privacy: .private(mask: .hash)`** -- when you need to correlate events for the same user across log entries without exposing the actual value.
- **`privacy: .sensitive`** -- for passwords or tokens (though these ideally should not be logged at all).
- **If unsure, default to `.private`** -- you can always relax the annotation later.

Example:

```swift
logger.notice("Login for \(username, privacy: .private(mask: .hash)), plan: \(plan, privacy: .public)")
```

## 5. Redact PII in Crash Reporting Metadata

Crash reporting SDKs (Sentry, Crashlytics) send metadata to remote servers. You must redact PII before attaching context to error reports. Build a `Redactor` utility that masks identifiers:

- Mask user IDs to show only the last 4 characters (e.g., `***4f8a`).
- Mask emails to show only the first character and domain (e.g., `j***@example.com`).
- Mask phone numbers to show only the last 4 digits.

Use a `@Redacted` property wrapper on model fields containing PII (email, phone number). This prevents accidental exposure through `print()`, `String(describing:)`, or log interpolation -- the wrapper overrides `CustomStringConvertible` and `CustomDebugStringConvertible` to output `--redacted--` instead of the actual value.

## 6. Privacy Manifests Are Mandatory (Since May 2024)

Apple requires `PrivacyInfo.xcprivacy` files that declare use of Required Reason APIs. Apps submitted without proper manifests are **rejected during App Store review**. APIs requiring declaration include:

- `UserDefaults`
- File timestamp APIs (`NSFileCreationDate`, `NSFileModificationDate`)
- System boot time APIs
- Disk space APIs

Crash reporting SDKs like Sentry and Crashlytics ship their own manifests (Xcode merges them automatically), but if any SDK you use lacks one, you must add declarations to your own manifest.

## 7. Crash Reporting and ATT Consent

Crash reporting generally does **not** require App Tracking Transparency (ATT) consent, provided:

- The data is used only for improving your own app.
- The data is not shared with data brokers.
- The data is not linked with third-party data for advertising.

However, some SDKs have their own requirements. For example, Firebase Crashlytics's terms (Section 2.6) require developers to obtain EU user consent for data transfer and storage. Always read your specific SDK's data processing terms.

## 8. Practical Checklist

- Replace all `print()` calls with `os.Logger` using appropriate privacy annotations.
- Audit every `catch` block and error report for PII leakage in context dictionaries.
- Audit URL logging -- strip or redact any user identifiers embedded in URL paths.
- Never log full HTTP request/response bodies in production.
- Use the `@Redacted` property wrapper on model fields that contain PII.
- Build a `Redactor` utility for masking IDs, emails, and phone numbers in crash report metadata.
- Include a `PrivacyInfo.xcprivacy` manifest and verify all Required Reason API usage is declared.
- Review your crash reporting SDK's specific GDPR/data processing terms and obtain EU user consent if required.
- Default to `privacy: .private` for any dynamic value you are unsure about.

---

The core principle: treat every log statement and every crash report context field as a potential data leak. Use Apple's built-in privacy annotations as your first defense, redact before sending to remote services, and audit regularly for the operational leaks that slip through code review.
