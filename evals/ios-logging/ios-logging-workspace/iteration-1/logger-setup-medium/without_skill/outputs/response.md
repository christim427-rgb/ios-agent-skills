# Privacy Annotations for Swift Logger Calls

When using Apple's `os.Logger` (or `OSLog`), string interpolations in log messages are **private by default** for non-numeric types. This means dynamic string values will appear as `<private>` in Console.app and log archives unless you explicitly mark them with a privacy level. Numeric types (Int, Double, etc.) are **public by default**.

You control visibility using the `privacy` parameter on each interpolated value.

## Available Privacy Levels

- `.public` -- The value is always visible in logs, even on production devices. Use for non-sensitive data that is safe to appear in diagnostic logs.
- `.private` -- The value is redacted in logs collected from production devices but visible when streaming from Xcode. This is the default for strings.
- `.sensitive` -- Similar to `.private` but with a stronger semantic signal that the data is sensitive (available on newer OS versions).
- `.auto` -- Lets the system decide based on the type (strings default to private, numbers default to public).

You can also use hash-based redaction: `.private(mask: .hash)` which replaces the value with a consistent hash, allowing you to correlate entries without exposing the raw value.

## Corrected Logger Calls

### First call

```swift
logger.error("Request to \(url, privacy: .public) failed for user \(userId, privacy: .private(mask: .hash)) with token \(authToken, privacy: .sensitive)")
```

**Rationale:**

| Value       | Privacy Level              | Why                                                                 |
|-------------|----------------------------|----------------------------------------------------------------------|
| `url`       | `.public`                  | API endpoint URLs are typically non-sensitive and essential for debugging network issues. |
| `userId`    | `.private(mask: .hash)`    | User IDs are personally identifiable. Using `.hash` lets you correlate multiple log entries for the same user without exposing the actual ID. |
| `authToken` | `.sensitive`               | Authentication tokens are highly sensitive credentials. They should never appear in plaintext in logs. Use `.sensitive` (or at minimum `.private`) to ensure they are fully redacted. |

### Second call

```swift
logger.info("Saving order \(orderId, privacy: .public) for \(customerEmail, privacy: .private) total \(amount, privacy: .public)")
```

**Rationale:**

| Value           | Privacy Level   | Why                                                                 |
|-----------------|-----------------|----------------------------------------------------------------------|
| `orderId`       | `.public`       | Order IDs are internal identifiers useful for tracing transactions in logs. Generally safe to expose. |
| `customerEmail` | `.private`      | Email addresses are personal data (PII). They must be redacted in production logs. You could also use `.private(mask: .hash)` if you need to correlate logs by customer. |
| `amount`        | `.public`       | Numeric values like transaction amounts are public by default and are useful for debugging order processing. No PII concern. |

## Key Principles

1. **Strings are private by default.** If you do not add a `privacy` annotation, string interpolations will be redacted as `<private>` in production logs. This is safe but makes debugging harder if you actually need to see the value.

2. **Numbers are public by default.** Integer and floating-point interpolations are visible without any annotation. Add `.private` explicitly if a number is sensitive (e.g., a social security number or account balance).

3. **Never log credentials as public.** Tokens, passwords, API keys, and session identifiers should always be `.private` or `.sensitive`.

4. **Use `.private(mask: .hash)` for correlation.** When you need to group log entries by a user or entity without revealing the actual identifier, the hash mask produces a stable, non-reversible replacement value.

5. **Prefer `.sensitive` over `.private` for credentials.** The `.sensitive` level was introduced to give an even stronger semantic signal that the data requires protection. Use it for authentication tokens, passwords, and similar secrets.

6. **Consider your log audience.** Logs may be collected via sysdiagnose, shared with support teams, or aggregated in crash reporting tools. Anything marked `.public` can end up in those destinations.
