# Thai User Seeing Year 2568 Instead of 2025

This is caused by the Thai locale using the **Buddhist calendar** by default. The Buddhist calendar year is the Gregorian year plus 543, so 2025 becomes 2568. When you use `DateFormatter` with `dateFormat = "yyyy-MM-dd"` without specifying a locale, it uses the user's current locale (Thai), which uses the Buddhist calendar — and `yyyy` outputs the Buddhist year.

## Understanding the Issue

```swift
// This code on a Thai user's device:
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd"
let dateString = formatter.string(from: Date())
// Output: "2568-03-29" — Buddhist calendar year!
```

The `DateFormatter` defaults to the user's locale and calendar. Thai locale (`th_TH`) defaults to the Buddhist calendar, where the year is offset by +543 from the Gregorian calendar.

## The Fix Depends on the Purpose

### For API/Server Communication: Use en_US_POSIX

If this date string is being sent to a server or API, you must use `en_US_POSIX` locale to force Gregorian calendar output:

```swift
// ✅ For API output — always Gregorian
let formatter = DateFormatter()
formatter.locale = Locale(identifier: "en_US_POSIX")
formatter.timeZone = TimeZone(identifier: "UTC")
formatter.dateFormat = "yyyy-MM-dd"
let dateString = formatter.string(from: Date())
// Output: "2025-03-29" — always Gregorian, regardless of user locale
```

Setting `locale` to `en_US_POSIX` forces the Gregorian calendar, Western Arabic digits, and 24-hour time format. This is the correct approach for any fixed-format date output that will be consumed by machines (APIs, file names, logging, data storage).

### For Displaying to the User: Buddhist Year IS Correct

Here is the critical nuance: **if this date is being displayed to a Thai user, the Buddhist year 2568 is actually correct.** Thai users expect to see Buddhist calendar years in their date displays. Do not force Gregorian on user-facing display.

For user-facing dates, do not use a custom `dateFormat` string at all. Use system styles that automatically adapt to the user's locale and calendar:

```swift
// ✅ For user display — respects user's calendar preference
let formatter = DateFormatter()
formatter.dateStyle = .medium
formatter.timeStyle = .none
label.text = formatter.string(from: date)
// Thai user sees: "29 มี.ค. 2568" (Buddhist calendar) — correct!
// US user sees: "Mar 29, 2025" (Gregorian) — correct!

// ✅ iOS 15+
label.text = date.formatted(.dateTime.year().month().day())
// Automatically uses the user's preferred calendar
```

## Summary Decision Tree

```
Is this date for a server/API/file/log?
├── YES → Use en_US_POSIX locale (forces Gregorian year 2025)
└── NO → Is it displayed to the user?
    ├── YES → Use .dateStyle/.timeStyle or Date.formatted()
    │         (Buddhist year 2568 IS correct for Thai users)
    └── NO → Internal logic → Use Date components, not formatted strings
```

The key insight is that "year 2568" is not a bug for Thai users — it is their expected calendar system. The bug only exists when you send Buddhist calendar dates to a server that expects Gregorian dates, or when you use a custom date format string for user display instead of letting the system handle calendar differences automatically.
