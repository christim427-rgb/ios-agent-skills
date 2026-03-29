The issue is that `String(format:)` always outputs Western Arabic digits (0-9) regardless of the user's locale. It does not respect locale settings for numeral systems.

## The Problem

When you use standard formatting:

```swift
label.text = String(format: "%d items", count)
```

This always produces `"5 items"` with Western Arabic digits, even if the user's locale (e.g., Arabic) expects Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩). Arabic-speaking users expect to see `"٥"` not `"5"`.

`String(format:)` is a C-level formatter that operates independently of the device locale. It always uses the "C" locale, which means Western digits, period as decimal separator, and no locale-specific formatting.

## The Fix

### Option 1: `String.localizedStringWithFormat()` (All iOS versions)

```swift
label.text = String.localizedStringWithFormat(
    NSLocalizedString("items_count", comment: "Number of items, %lld = count"),
    count
)
```

`localizedStringWithFormat` respects the user's locale and will output Eastern Arabic numerals when appropriate.

### Option 2: `.formatted()` (iOS 15+)

```swift
label.text = count.formatted()  // Locale-aware by default
```

For Arabic locale, `42.formatted()` produces `"٤٢"` with Eastern Arabic digits.

### Option 3: `NumberFormatter` (Explicit control)

```swift
let formatter = NumberFormatter()
formatter.numberStyle = .decimal
// formatter.locale is already the user's current locale by default
label.text = formatter.string(from: NSNumber(value: count))
```

## When to Use Each

- **`String(format:)`** — Only for non-user-facing purposes (logging, debugging, machine-to-machine communication) where you specifically want consistent Western digit output.
- **`String.localizedStringWithFormat()`** — For user-facing formatted strings on any iOS version. Combines localization key lookup with locale-aware formatting.
- **`.formatted()`** — The modern, preferred API (iOS 15+) for any user-facing number display. Locale-aware by default.
- **`NumberFormatter`** — When you need fine control over formatting (e.g., minimum/maximum fraction digits, specific number styles).

The general rule: any number displayed to users should go through a locale-aware API so that the numeral system, digit grouping, and separators all match the user's expectations.
