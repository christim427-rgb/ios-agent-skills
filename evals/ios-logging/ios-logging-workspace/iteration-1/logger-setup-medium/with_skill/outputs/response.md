# Privacy Annotations for Logger Calls

## Key Rule

In `os.Logger`, **dynamic strings are redacted by default** in production logs -- they appear as `<private>` unless you attach a debugger. You must add explicit privacy annotations to every interpolated value, choosing the right level based on the data's sensitivity.

## Line 1: Network Error with User Credentials

```swift
// Original (BAD -- no annotations, useless in production)
logger.error("Request to \(url) failed for user \(userId) with token \(authToken)")
// Production output: "Request to <private> failed for user <private> with token <private>"
```

**Corrected version:**

```swift
logger.error("Request to \(url.absoluteString, privacy: .public) failed for user \(userId, privacy: .private(mask: .hash)) with token \(authToken, privacy: .sensitive)")
```

Annotation rationale for each value:

| Value | Annotation | Why |
|---|---|---|
| `url.absoluteString` | `.public` | URL paths are operational data safe for anyone with log access. **Caveat:** if the URL contains user-identifying segments (e.g., `/users/john@example.com/profile`), strip or redact the PII portion before logging -- URL paths with embedded emails or user IDs are a commonly missed operational leak. |
| `userId` | `.private(mask: .hash)` | This is PII (a personal identifier). The hash mask produces a stable hash so you can correlate events for the same user across log entries without exposing the raw ID. |
| `authToken` | `.sensitive` | **Tokens should not be logged at all.** Auth tokens, JWT/OAuth tokens, refresh tokens, API keys, and session tokens are authentication data that must never appear in logs. If you absolutely must reference it, `.sensitive` ensures it is always redacted -- even during development. The best practice is to remove the token from the log message entirely. |

**Recommended rewrite (remove the token entirely):**

```swift
logger.error("Request to \(url.absoluteString, privacy: .public) failed for user \(userId, privacy: .private(mask: .hash))")
```

## Line 2: Order Logging with Customer Email

```swift
// Original (BAD -- no annotations)
logger.info("Saving order \(orderId) for \(customerEmail) total \(amount)")
// Production output: "Saving order <private> for <private> total <private>"
// Note: numeric types default to public, but string types default to private
```

**Corrected version:**

```swift
logger.info("Saving order \(orderId, privacy: .public) for \(customerEmail, privacy: .private(mask: .hash)) total \(amount, privacy: .public)")
```

Annotation rationale for each value:

| Value | Annotation | Why |
|---|---|---|
| `orderId` | `.public` | An order identifier is operational data -- safe for log consumers. It identifies the transaction, not the person. |
| `customerEmail` | `.private(mask: .hash)` | Email addresses are PII (personal identifiers under both GDPR and CCPA). Using `mask: .hash` lets you correlate orders for the same customer across log entries without exposing the raw email. If you do not need cross-event correlation, plain `.private` is sufficient. |
| `amount` | `.public` | A transaction amount is operational/financial context, not PII. Numeric types are public by default in `os.Logger`, but adding the explicit annotation makes intent clear and avoids relying on implicit behavior. |

## Decision Guide Summary

Use this quick reference when choosing a privacy annotation:

```
Is the value safe for anyone with log access to see?
  YES (URL paths, error codes, status codes, operation names, order IDs)
    -> privacy: .public
  NO -- Is it PII or user-specific data?
    YES -- Do you need to correlate events for the same user?
      YES -> privacy: .private(mask: .hash)
      NO  -> privacy: .private
    NO -- Is it a secret (token, password, API key)?
      -> DO NOT LOG IT. If you must reference it: privacy: .sensitive
  UNSURE
    -> Default to .private (you can always relax later)
```

## Additional Notes

- **Always specify annotations explicitly.** Leaving interpolated strings without an annotation means they silently become `<private>` in production, making your logs useless for debugging.
- **Never log authentication data.** Passwords, tokens, API keys, client secrets, and session tokens should be excluded from log messages entirely -- not just redacted.
- **Watch for PII in URLs.** If a URL contains embedded emails or user IDs in its path (e.g., `/users/john@example.com/`), that URL should not be marked `.public` without sanitization first.
