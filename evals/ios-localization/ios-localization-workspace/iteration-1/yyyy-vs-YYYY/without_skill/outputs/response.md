# YYYY vs yyyy Date Format Bug

## The Problem

```swift
formatter.dateFormat = "YYYY-MM-dd"
```

`YYYY` is the **ISO week-numbering year**, not the calendar year. `yyyy` is the **calendar year**. They differ near the boundaries of the year.

## How It Breaks

The ISO week-numbering year assigns each week to the year that contains the Thursday of that week. This means:

- **December 30, 2024** (Monday) falls in ISO week 1 of 2025. With `YYYY`, it displays as **2025-12-30** instead of 2024-12-30.
- **January 1, 2023** (Sunday) falls in ISO week 52 of 2022. With `YYYY`, it displays as **2022-01-01** instead of 2023-01-01.

The bug only manifests for a few days around January 1st each year, making it hard to catch in testing.

## The Fix

```swift
formatter.dateFormat = "yyyy-MM-dd"  // lowercase yyyy = calendar year
```

## Another Common Trap: DD vs dd

While you are at it, watch out for a related specifier mistake:

- `dd` = day of the **month** (01-31) -- this is what you almost always want
- `DD` = day of the **year** (001-366)

Using `DD` instead of `dd` would show "060" on March 1st instead of "01".

## Summary

| Specifier | Meaning | Example for Dec 30, 2024 |
|-----------|---------|--------------------------|
| `yyyy` | Calendar year | 2024 |
| `YYYY` | ISO week-numbering year | 2025 |
| `dd` | Day of month | 30 |
| `DD` | Day of year | 365 |

Always use lowercase `yyyy` and `dd` unless you specifically intend ISO week-year or day-of-year semantics.
