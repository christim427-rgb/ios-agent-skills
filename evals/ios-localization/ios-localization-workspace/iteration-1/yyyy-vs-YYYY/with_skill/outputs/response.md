The problem is `YYYY` — this is the **ISO week-numbering year**, not the calendar year. You need lowercase `yyyy`.

## The Difference

- **`yyyy`** — Calendar year. December 30, 2024 is in calendar year **2024**. This is what you almost always want.
- **`YYYY`** — ISO week-numbering year. It returns the year that the current ISO week belongs to. Near the boundaries of January 1st, this can differ from the calendar year.

## Concrete Example

**Date: December 30, 2024** (a Monday)

This day falls in ISO week 1 of 2025 (because ISO weeks start on Monday, and this Monday is the start of the first week of 2025).

```swift
formatter.dateFormat = "yyyy-MM-dd"  // "2024-12-30" (correct)
formatter.dateFormat = "YYYY-MM-dd"  // "2025-12-30" (WRONG — shows 2025 for a 2024 date!)
```

The result `"2025-12-30"` is completely wrong — it says December 30, 2025, when the actual date is December 30, 2024.

Similarly, **January 1, 2025** (a Wednesday) could show as 2024 with `YYYY` in some years when January 1 falls in the last ISO week of the previous year.

This bug appears silently for 360+ days a year and only manifests during the last few days of December or first few days of January, making it extremely hard to catch in testing.

## Another Common Specifier Trap: DD vs dd

While fixing `YYYY`, also watch out for `DD`:

- **`dd`** — Day of month (01-31). This is what you want.
- **`DD`** — Day of year (001-366).

```swift
formatter.dateFormat = "MM/DD/yyyy"  // January 15 → "01/015/2025" (day 15 of the year!)
formatter.dateFormat = "MM/dd/yyyy"  // January 15 → "01/15/2025" (correct)
```

## The Fix

```swift
// Correct
formatter.dateFormat = "yyyy-MM-dd"

// Full quick reference of commonly confused specifiers:
// yyyy = calendar year (2025)        YYYY = ISO week year (WRONG near Jan 1)
// dd   = day of month (01-31)        DD   = day of year (001-366)
// MM   = month (01-12)               mm   = minutes (00-59)
// HH   = 24-hour (00-23)             hh   = 12-hour (01-12, needs AM/PM)
```

And remember: if this date is displayed to users, you should not be using `dateFormat` at all. Use `.dateStyle`/`.timeStyle` or `Date.formatted()` instead, which handle locale-specific ordering automatically.
