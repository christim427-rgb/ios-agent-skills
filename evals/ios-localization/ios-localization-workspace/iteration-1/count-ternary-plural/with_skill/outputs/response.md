This approach is fundamentally broken for localization. The `count == 1 ? singular : plural` ternary assumes every language has exactly two plural forms, which is wrong for the majority of the world's languages.

## The Problem

```swift
let text = count == 1 ? "\(count) item" : "\(count) items"
```

This code has two hard-coded forms: one for exactly 1 and one for everything else. This works in English, which only has `one` and `other` plural categories. But it breaks for every language with more than two plural forms:

- **Russian, Ukrainian** need 4 forms: `one`, `few`, `many`, `other`
  - 1 item, 2 itema, 5 itemov, 1.5 itema
- **Polish** needs 4 forms: `one`, `few`, `many`, `other` (with different rules than Russian)
- **Arabic** needs all 6 CLDR categories: `zero`, `one`, `two`, `few`, `many`, `other`
  - Arabic has a special dual form for exactly 2
- **Czech, Slovak** need 4 forms

With the ternary approach, Russian would show "2 items" (the `other` form) instead of the correct `few` form. The user sees a grammatical error.

Additionally, the strings themselves are hardcoded in English with no localization wrappers at all.

## The Fix: Use .stringsdict or String Catalog Plural Variations

The correct approach is to let the system handle plural selection via CLDR rules:

### Option 1: String Catalog (Xcode 15+, recommended)

In your code:
```swift
// The system automatically selects the correct plural form
let text = String(localized: "items_count \(count)",
                  comment: "Number of items. %lld = count, e.g. '3 items'")
```

In the String Catalog editor, right-click the key and choose "Vary by Plural." Xcode will display all CLDR-required categories for each language automatically.

### Option 2: .stringsdict

```xml
<key>items_count</key>
<dict>
    <key>NSStringLocalizedFormatKey</key>
    <string>%#@count@</string>
    <key>count</key>
    <dict>
        <key>NSStringFormatSpecTypeKey</key>
        <string>NSStringPluralRuleType</string>
        <key>NSStringFormatValueTypeKey</key>
        <string>lld</string>
        <key>one</key>
        <string>%lld item</string>
        <key>other</key>
        <string>%lld items</string>
    </dict>
</dict>
```

For Russian, the translator adds the missing categories (`few`, `many`) with appropriate forms. The system automatically selects the correct form based on CLDR plural rules at runtime.

## Key Takeaway

Never use conditionals (`if`/`switch`/ternary) to select plural forms. Always delegate to the localization system (`.stringsdict` or String Catalog plural variations), which understands the plural rules for every language via the Unicode CLDR.
