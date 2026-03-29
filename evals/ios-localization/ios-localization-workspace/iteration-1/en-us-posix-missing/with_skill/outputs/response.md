The issue is a missing `en_US_POSIX` locale on the `DateFormatter`. Without it, the formatter uses the user's device locale, which causes parsing failures for two distinct categories of users.

## The Problem

```swift
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
let date = formatter.date(from: serverResponse.createdAt)
```

This code has no `locale` set, so `DateFormatter` defaults to the user's current locale. This causes two failure modes:

### Failure 1: Buddhist Calendar Users (Thailand, etc.)

Users with Thai locale and Buddhist calendar get `yyyy` interpreted as Buddhist year. The Buddhist calendar year is Gregorian year + 543, so:

- Server sends: `"2025-03-29T14:30:00"`
- Formatter expects Buddhist year `2568` for the current year
- Parsing the Gregorian year `2025` either fails entirely (returns `nil`) or produces a date 543 years in the past

This affects users in Thailand and any user who has selected the Buddhist calendar in their device settings.

### Failure 2: 12-Hour Time Users

Users whose device is set to 12-hour time format cause `HH` (24-hour hours) to be interpreted differently:

- Server sends: `"2025-03-29T14:30:00"`
- On a 12-hour device, the formatter may reject `14` as an invalid hour, or misparse the time
- This returns `nil` from `.date(from:)`, which can crash if force-unwrapped

This affects users in the US, UK, Australia, and many other regions where 12-hour time is the default.

## The Fix

Always set `locale` to `en_US_POSIX` when parsing fixed-format date strings from APIs:

```swift
let formatter = DateFormatter()
formatter.locale = Locale(identifier: "en_US_POSIX")
formatter.timeZone = TimeZone(identifier: "UTC")  // Or the server's timezone
formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
let date = formatter.date(from: serverResponse.createdAt)
```

The `en_US_POSIX` locale is a special locale that:
- Always uses the Gregorian calendar
- Always uses 24-hour time
- Never changes behavior based on user settings
- Is specifically designed for parsing fixed-format machine-readable dates

### iOS 16+ Alternative

For ISO 8601 dates, use the dedicated parser:

```swift
let date = try Date.ISO8601FormatStyle().parse(serverResponse.createdAt)
```

## Important Distinction

- **API date parsing** (machine-to-machine): Always use `en_US_POSIX`. The goal is consistent parsing regardless of user settings.
- **User-facing date display**: Never use `en_US_POSIX`. Use `.dateStyle`/`.timeStyle` or `Date.formatted()` so dates appear in the user's expected format and calendar.
