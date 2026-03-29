# Missing en_US_POSIX Locale for Date Parsing

## The Problem

```swift
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
let date = formatter.date(from: serverResponse.createdAt)
```

This code breaks for some users because `DateFormatter` uses the user's current locale and calendar by default. Two specific failure modes:

### Failure 1: Buddhist Calendar (Thai Users)

Users with Thai locale use the Buddhist calendar by default, where the year is 543 years ahead of the Gregorian calendar (2025 becomes 2568). When parsing a server date string like `"2025-01-15T10:30:00"`, the formatter interprets "2025" through the Buddhist calendar lens, causing incorrect date parsing.

### Failure 2: 12-Hour Time Format

Users who have 12-hour time enabled in their locale settings can cause `HH:mm:ss` parsing to fail entirely. The formatter may expect AM/PM designators and reject 24-hour time strings like `"14:30:00"`.

## The Fix

Always set `locale` to `en_US_POSIX` when parsing fixed-format date strings (like API responses):

```swift
let formatter = DateFormatter()
formatter.locale = Locale(identifier: "en_US_POSIX")
formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
let date = formatter.date(from: serverResponse.createdAt)
```

For iOS 15+, you can also use `ISO8601DateFormatter` for ISO 8601 strings:

```swift
let formatter = ISO8601DateFormatter()
let date = formatter.date(from: serverResponse.createdAt)
```

## When to Use en_US_POSIX vs User Locale

- **Parsing/serializing data** (API communication, file storage): Always use `en_US_POSIX`. This ensures consistent behavior regardless of the user's device settings.
- **Displaying dates to users**: Use `.dateStyle`/`.timeStyle` or `Date.FormatStyle` (iOS 15+), which automatically adapts to the user's locale and calendar preferences.

```swift
// For display:
let displayFormatter = DateFormatter()
displayFormatter.dateStyle = .medium
displayFormatter.timeStyle = .short
label.text = displayFormatter.string(from: date)
```

## Summary

The `en_US_POSIX` locale is the single most important setting for date parsing of machine-readable strings. Without it, your date parsing is a ticking time bomb that will silently fail for users with non-Gregorian calendars or non-standard time settings.
