# Custom dateFormat for User-Facing Display

## The Problem

```swift
let formatter = DateFormatter()
formatter.dateFormat = "MM/dd/yyyy"
label.text = formatter.string(from: date)
```

`MM/dd/yyyy` is the US date format. Most of the world uses different date ordering:

- **US**: 03/29/2025 (MM/dd/yyyy)
- **UK/Europe**: 29/03/2025 (dd/MM/yyyy)
- **Germany**: 29.03.2025 (dd.MM.yyyy)
- **Japan**: 2025/03/29 (yyyy/MM/dd)
- **China**: 2025-03-29 (yyyy-MM-dd)

Hardcoding `MM/dd/yyyy` means international users see dates in an unfamiliar and potentially confusing format. A date like 03/04/2025 could be interpreted as March 4 or April 3 depending on the user's expectations.

## Recommended Fixes

### Option 1: dateStyle / timeStyle (Simplest)

```swift
let formatter = DateFormatter()
formatter.dateStyle = .medium
formatter.timeStyle = .none
label.text = formatter.string(from: date)
// US: "Mar 29, 2025"
// Germany: "29.03.2025"
// Japan: "2025/03/29"
```

### Option 2: Date.formatted() (iOS 15+)

```swift
label.text = date.formatted(.dateTime.month().day().year())
// Automatically adapts to user's locale
```

### Option 3: setLocalizedDateFormatFromTemplate() (Custom Pattern)

If you need a specific set of date components but want locale-appropriate ordering:

```swift
let formatter = DateFormatter()
formatter.setLocalizedDateFormatFromTemplate("MMddyyyy")
label.text = formatter.string(from: date)
// US: "03/29/2025"
// Germany: "29.03.2025"
// Japan: "2025/03/29"
```

This method takes a "template" of desired components and automatically reorders them and adds the correct separators for the user's locale.

## When Custom dateFormat IS Appropriate

Only use `formatter.dateFormat = "..."` when:
- Parsing machine-readable strings (API responses, file formats) -- and always pair with `en_US_POSIX` locale
- Writing dates to a specific format for data exchange

For all user-facing date display, use `dateStyle`, `Date.formatted()`, or `setLocalizedDateFormatFromTemplate()`.
