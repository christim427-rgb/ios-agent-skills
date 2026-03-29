# Thai User Sees Year 2568 Instead of 2025

## The Cause

Thailand uses the **Buddhist calendar** by default, where the year is the Gregorian year plus 543. So 2025 in the Gregorian calendar is 2568 in the Buddhist calendar.

Your code:

```swift
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd"
let dateString = formatter.string(from: Date())
```

When a Thai user runs this, `DateFormatter` uses their device's locale and calendar settings. The `yyyy` format specifier outputs the year in the user's calendar system, so it outputs `2568` instead of `2025`.

## The Fix Depends on the Purpose

### For API/Server Communication: Use `en_US_POSIX`

If this date string is being sent to a server or used for data interchange, you need the Gregorian calendar year. Force the locale to `en_US_POSIX`:

```swift
let formatter = DateFormatter()
formatter.locale = Locale(identifier: "en_US_POSIX")
formatter.dateFormat = "yyyy-MM-dd"
let dateString = formatter.string(from: Date())
// Always outputs Gregorian: "2025-03-29"
```

The `en_US_POSIX` locale locks the formatter to the Gregorian calendar and 24-hour time, regardless of the user's settings. This is the correct approach for any non-user-facing date strings (API calls, file names, database storage, etc.).

### For Display to the User: Use `.dateStyle` or `Date.formatted()`

If this date is shown to the user, **the Buddhist year (2568) is correct for Thai users**. Don't force Gregorian on user-facing dates. Instead, use system formatters that automatically adapt:

```swift
// iOS 15+
let displayString = date.formatted(.dateTime.year().month().day())

// Or with DateFormatter
let formatter = DateFormatter()
formatter.dateStyle = .medium
formatter.timeStyle = .none
let displayString = formatter.string(from: date)
```

These will show the date in the format and calendar system the user expects.

## Key Principle

- **Machine-readable dates** (APIs, JSON, databases): Always use `en_US_POSIX` locale with explicit `dateFormat`
- **User-visible dates** (UI labels, messages): Use `.dateStyle`/`.timeStyle` or `Date.formatted()`, and let the system handle the user's calendar and locale preferences

The Buddhist calendar year is not a bug for Thai users -- it's their expected date representation. Only force Gregorian when the date is for programmatic use, not human display.
