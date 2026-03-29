# Fixed Width on Localized Text: German Truncation

The problem is the fixed `width: 120` on a container displaying localized text. **German translations average 30% longer than English**, and short strings can expand even more dramatically — a simple "OK" becomes "Einverstanden" (3x longer). A fixed width of 120 points that fits the English text will truncate the German translation.

## The Problem

```swift
// ❌ Fixed width — truncates longer translations
Text(localizedString).frame(width: 120)
```

This is a common localization issue. Text expansion varies significantly by language:

| Source Language | Target Expansion |
|---|---|
| English -> German | +30% average |
| English -> French | +15-20% |
| English -> Japanese | Can be shorter (but needs vertical space for ruby annotations) |
| Short strings like "OK" -> German "Einverstanden" | 3x longer |

## The Fix

Use flexible constraints instead of fixed widths:

```swift
// ✅ Flexible — text can grow as needed
Text(localizedString)
    .frame(maxWidth: .infinity, alignment: .leading)

// ✅ Or simply remove the width constraint entirely
Text(localizedString)

// ✅ If you need a maximum, use maxWidth with flexible minimum
Text(localizedString)
    .frame(minWidth: 80, maxWidth: 200)
```

In UIKit, use Auto Layout constraints that allow the label to grow:

```swift
// ✅ Let the label size itself
label.setContentHuggingPriority(.required, for: .horizontal)
label.setContentCompressionResistancePriority(.required, for: .horizontal)
// Or set numberOfLines = 0 to allow wrapping
label.numberOfLines = 0
```

## Testing Text Expansion

Use Xcode's **Double Length Pseudolanguage** to test text expansion without needing actual translations. This doubles every string, simulating worst-case expansion:

**Edit Scheme -> Options -> Application Language -> Double Length Pseudolanguage**

Run through every screen in your app with this pseudolanguage enabled. Any text that gets truncated or breaks the layout needs flexible constraints.

Also test with the **Bounded Pseudolanguage** which wraps strings in `[# #]` brackets, making it easy to see exactly where text is being clipped.

## General Rule

Never use fixed widths on containers that hold localized text. Use flexible Auto Layout constraints and always test with Double Length pseudolanguage to catch truncation issues early.
