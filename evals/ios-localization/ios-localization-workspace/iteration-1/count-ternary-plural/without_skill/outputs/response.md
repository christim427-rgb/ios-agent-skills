# The Ternary Pluralization Anti-Pattern

## The Problem

```swift
let text = count == 1 ? "\(count) item" : "\(count) items"
```

This assumes there are only two plural forms: singular (1) and plural (everything else). This works for English, but **many languages have more than two plural forms**, and this approach completely breaks for them.

## Languages This Breaks For

- **Russian**: needs 4 forms (one, few, many, other). The ternary gives wrong results for 2-4 ("few" form), 5-20 ("many" form), etc.
- **Polish**: needs 4 forms with different rules than Russian.
- **Arabic**: needs 6 forms (zero, one, two, few, many, other), including a special dual form for exactly 2.
- **Czech, Croatian, Serbian**: also need multiple forms.
- **Welsh, Irish**: have their own multi-category systems.

## The Fix

Use `.stringsdict` or String Catalog plural variations. These integrate with Apple's CLDR-based plural system that knows the correct rules for every language.

### Using .stringsdict:

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

Then in code:

```swift
let text = String.localizedStringWithFormat(
    NSLocalizedString("items_count", comment: "Number of items in the list"),
    count
)
```

### Using String Catalog (Xcode 15+):

In the String Catalog editor, mark the string as having plural variations. Xcode will prompt you for the correct number of forms for each language.

The system will automatically apply the correct CLDR plural rules for each language at runtime, without you needing to write any conditional logic.
