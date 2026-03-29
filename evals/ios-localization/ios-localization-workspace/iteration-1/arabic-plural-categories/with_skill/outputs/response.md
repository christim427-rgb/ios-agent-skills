Arabic has the most complex plural system of any commonly supported language. It requires all **6 CLDR plural categories**: `zero`, `one`, `two`, `few`, `many`, and `other`.

## Arabic Plural Categories

| Category | Rule | Example Numbers |
|---|---|---|
| `zero` | The number 0 | 0 |
| `one` | The number 1 | 1 |
| `two` | The number 2 (dual form) | 2 |
| `few` | 3-10, and numbers ending in 03-10 | 3, 4, 5, 6, 7, 8, 9, 10, 103, 104, 105, 106, 107, 108, 109, 110, 203... |
| `many` | 11-99, and numbers ending in 11-99 | 11, 12, 13, 25, 50, 99, 111, 112, 199, 211... |
| `other` | 100-102, 200-202, 300-302... | 100, 101, 102, 200, 201, 202, 300... |

## Why the `two` Category Matters

Arabic has a grammatical **dual form** specifically for the number 2. This is a distinct morphological form that does not exist in most other languages. For example, the word for "books":

| Number | Category | Arabic Form |
|---|---|---|
| 0 | zero | ٠ كتب |
| 1 | one | كتاب واحد |
| 2 | two | كتابان (dual form) |
| 3 | few | ٣ كتب |
| 11 | many | ١١ كتابًا |
| 100 | other | ١٠٠ كتاب |

If you only implement `one`/`other` (the common AI failure pattern), you miss four categories and produce grammatically incorrect Arabic for most numbers.

## Implementation

### String Catalog

In your String Catalog, right-click the key and choose "Vary by Plural." Xcode will automatically show all six categories for Arabic when you add it as a target language.

### .stringsdict

```xml
<key>books_count</key>
<dict>
    <key>NSStringLocalizedFormatKey</key>
    <string>%#@count@</string>
    <key>count</key>
    <dict>
        <key>NSStringFormatSpecTypeKey</key>
        <string>NSStringPluralRuleType</string>
        <key>NSStringFormatValueTypeKey</key>
        <string>lld</string>
        <key>zero</key>
        <string>لا كتب</string>
        <key>one</key>
        <string>كتاب واحد</string>
        <key>two</key>
        <string>كتابان</string>
        <key>few</key>
        <string>%lld كتب</string>
        <key>many</key>
        <string>%lld كتابًا</string>
        <key>other</key>
        <string>%lld كتاب</string>
    </dict>
</dict>
```

## Testing

Use the verification test set to exercise all category boundaries:
```
[0, 1, 2, 3, 4, 5, 10, 11, 12, 14, 20, 21, 22, 25, 100, 101, 111, 1.5]
```

Also remember that Arabic uses Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩) by default, so use locale-aware number formatting (`NumberFormatter` or `.formatted()`) rather than `String(format:)` to ensure correct digit rendering.
