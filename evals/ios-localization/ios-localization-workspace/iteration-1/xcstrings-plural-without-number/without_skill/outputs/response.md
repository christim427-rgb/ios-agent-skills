# Pluralizing "Day" / "Days" Without Showing the Count

## The Challenge

You want to display just "Day" or "Days" (without the number) based on a count, but String Catalogs and `.stringsdict` are designed around displaying the number as part of the string.

## Can String Catalogs Handle This?

String Catalogs (`.xcstrings`) use plural variations that are tied to a numeric substitution variable. The plural system expects the number to appear in the string. If you define a plural variation, the count is typically embedded in the output string (e.g., `"%lld days"`).

String Catalogs **cannot** natively handle pluralization without displaying the number in the resulting string. The plural selection mechanism requires the integer argument, but you can work around this.

## Workaround with .stringsdict

You can use a `.stringsdict` file for this specific case, where you define plural forms that don't include the number in the output:

```xml
<key>day_count</key>
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
```

Usage:

```swift
let label = String.localizedStringWithFormat(
    NSLocalizedString("day_count", comment: "Day/Days label without count"),
    count
)
// count = 1 -> "Day"
// count = 2 -> "Days"
```

The number is used for **selecting** the plural form but does not appear in the output because the format strings (`Day`, `Days`) don't include `%lld`.

## Alternative: Computed Property

If you only need English and a few languages, a simpler approach is a computed property:

```swift
let label = count == 1
    ? String(localized: "day_singular", comment: "Singular: Day")
    : String(localized: "day_plural", comment: "Plural: Days")
```

However, this ternary approach only works for languages with two plural forms and breaks for languages like Russian, Polish, or Arabic.

## Recommendation

Use `.stringsdict` for this case, as it properly handles all plural categories across all languages while allowing you to omit the number from the displayed string.
