# Logging and GDPR Compliance in iOS Apps

When implementing logging in an iOS app, GDPR compliance requires careful attention to what data you capture, how you store it, and how you handle user rights. Here are the key areas to watch out for.

## 1. Avoid Logging Personally Identifiable Information (PII)

The most critical rule is to never log PII unless absolutely necessary and properly justified. Common PII that accidentally ends up in logs includes:

- **User names, email addresses, phone numbers**
- **Device identifiers** (IDFA, IDFV, serial numbers)
- **IP addresses** (considered PII under GDPR)
- **Location data** (GPS coordinates, city names derived from location)
- **Authentication tokens and session IDs** (can be linked back to a user)
- **Health or biometric data** (special category data under GDPR, requiring even stricter handling)

### Practical steps

- Use redaction mechanisms. Apple's `OSLog` / `Logger` framework supports privacy annotations:
  ```swift
  let logger = Logger(subsystem: "com.example.app", category: "network")
  logger.info("User logged in: \(username, privacy: .private)")
  ```
  The `.private` annotation ensures the value is redacted in log collection unless a debugger is attached.
- Build wrapper functions that automatically strip or hash sensitive fields before they reach the log sink.
- Audit all log statements during code review specifically for PII leakage.

## 2. Distinguish Log Levels and Environments

- **Debug/verbose logs** should only be active in development builds. Use compile-time flags (`#if DEBUG`) or configuration-based checks to ensure verbose logging is stripped from release builds.
- **Production logs** should be minimal and contain only operational data needed for crash diagnosis or performance monitoring, with no user-specific content.

## 3. Third-Party Logging and Analytics SDKs

Many third-party SDKs (Crashlytics, Firebase Analytics, Sentry, Datadog, etc.) collect and transmit log data to external servers. Under GDPR:

- **Data processing agreements (DPAs)** must be in place with every third-party processor that receives log data.
- Understand where the data is stored geographically. If logs are sent to servers outside the EU/EEA, you need appropriate transfer mechanisms (Standard Contractual Clauses, adequacy decisions, etc.).
- Configure SDKs to disable automatic PII collection where possible. For example, Crashlytics can capture custom keys -- make sure those keys do not contain PII.
- Review SDK default behaviors. Some SDKs automatically capture device IDs, user agents, or breadcrumbs that may contain sensitive information.

## 4. Data Retention and Deletion

GDPR requires that personal data not be kept longer than necessary:

- **Set retention policies** for all log storage. Logs containing any data linkable to a user should have a defined expiration.
- **On-device logs**: If you store logs locally (e.g., in files or Core Data), implement automatic rotation and deletion.
- **Remote logs**: Configure your log aggregation service to auto-delete logs after a defined period (e.g., 30 or 90 days).
- **Right to erasure**: If a user requests deletion of their data under GDPR Article 17, you must be able to identify and remove their data from logs as well, or demonstrate that logs are anonymized and cannot be linked back to the individual.

## 5. User Consent

Under GDPR, you generally need a lawful basis for processing personal data. For logging:

- **Legitimate interest** can sometimes justify minimal operational logging (crash reporting, security monitoring), but you must document a Legitimate Interest Assessment (LIA).
- **Consent** may be required for analytics or behavioral logging. If so, do not begin logging user-identifiable data until consent is obtained. Integrate with a Consent Management Platform (CMP) or Apple's App Tracking Transparency (ATT) framework where applicable.
- If a user withdraws consent, stop collecting their data in logs going forward.

## 6. Network Request and Response Logging

A common pitfall is logging full HTTP requests and responses during development and forgetting to disable it in production:

- Request URLs may contain query parameters with tokens or user IDs.
- Request/response bodies may contain full user profiles, payment details, or other sensitive data.
- Headers often contain authorization tokens.

Strip or redact sensitive fields from any network logging that persists in production.

## 7. Crash Reports and Diagnostics

Apple's own crash reporting (via Xcode Organizer or MetricKit) is generally privacy-safe, but custom crash reporters may capture:

- Stack traces that include variable values containing PII.
- Breadcrumbs or user actions that reveal behavior patterns.
- Custom metadata attached to crash reports.

Review what your crash reporter captures and ensure PII is excluded.

## 8. NSLog vs. os_log / Logger

- `NSLog` writes to the system log and is accessible via Console.app and device syslog. It offers no built-in redaction and persists longer than you might expect.
- `os_log` (and the newer `Logger` API in iOS 14+) supports privacy annotations and integrates with Apple's unified logging system, which automatically manages log persistence and access levels.
- Prefer `Logger` / `os_log` over `NSLog` or `print` for any production logging.

## 9. Documentation and Accountability

GDPR Article 30 requires records of processing activities. Your logging practices should be documented:

- What data is logged and why.
- Where logs are stored and for how long.
- Who has access to logs.
- What safeguards are in place (encryption, access controls, redaction).

## 10. Encryption and Access Control

- Logs stored on device should leverage iOS Data Protection (NSFileProtectionComplete or similar) so they are encrypted at rest.
- Logs transmitted to remote servers should use TLS.
- Access to production log systems should be restricted and audited.

---

## Summary Checklist

| Area | Action |
|------|--------|
| PII in logs | Audit and redact all personal data; use `privacy: .private` |
| Log levels | Disable verbose logging in production builds |
| Third-party SDKs | Verify DPAs, data residency, and default collection behavior |
| Retention | Set and enforce automatic log rotation and deletion policies |
| Consent | Obtain lawful basis before logging user-identifiable data |
| Network logging | Redact URLs, headers, and bodies in production |
| Crash reports | Review captured metadata for PII |
| API choice | Use `Logger` / `os_log` instead of `NSLog` or `print` |
| Documentation | Maintain records of processing activities for logging |
| Security | Encrypt logs at rest and in transit; restrict access |
