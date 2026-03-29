# Pluralizing Without Showing the Count in String Catalogs

**String Catalogs cannot handle this case.** Pluralization in `.xcstrings` requires a visible numeric value to drive the plural rule selection. If you need to display "Day" vs "Days" without showing the count (e.g., showing "Days" for a filter label when the interval is multiple days, but without displaying the actual number), String Catalogs do not support this pattern.

## Why String Catalogs Cannot Do This

String Catalog plural variations are driven by a numeric format argument (`%lld`, `%d`, etc.) that determines which plural category to use. The number must appear in the output string. There is no mechanism to use a number for category selection while hiding it from the displayed text.

## The Solution: Use .stringsdict

For pluralization without a visible number, `.stringsdict` is still required, even alongside `.xcstrings`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>interval_unit</key>
    <dict>
        <key>NSStringLocalizedFormatKey</key>
        <string>%#@days@</string>
        <key>days</key>
        <dict>
            <key>NSStringFormatSpecTypeKey</key>
            <string>NSStringPluralRuleType</string>
            <key>NSStringFormatValueTypeKey</key>
            <string>lld</string>
            <key>one</key>
            <string>Day</string>
            <key>other</key>
            <string>Days</string>
        </dict>
    </dict>
</dict>
</plist>
```

Notice the `one` and `other` values do not include `%lld` — the number drives plural selection but is not displayed. You use it in code like:

```swift
let label = String(format: NSLocalizedString("interval_unit", comment: ""), dayCount)
// dayCount = 1 → "Day"
// dayCount = 3 → "Days"
```

## Important Constraint

You **cannot** have both a `.strings`/`.stringsdict` file and a `.xcstrings` file with the same table name (e.g., both called "Localizable"). They cannot coexist. So if your main strings are in `Localizable.xcstrings`, you would need to put this `.stringsdict` in a differently named table, or keep a separate `.stringsdict` file alongside your String Catalog with a different table name.

This is one of the few cases where `.stringsdict` remains necessary even in modern projects using String Catalogs.
