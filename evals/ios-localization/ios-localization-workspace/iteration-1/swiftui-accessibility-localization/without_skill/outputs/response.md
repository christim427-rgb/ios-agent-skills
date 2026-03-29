# Localizing Accessibility Labels in SwiftUI

## Your Current Code

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel("Share")
```

## How SwiftUI Handles This

In SwiftUI, the `.accessibilityLabel("Share")` modifier accepts a `LocalizedStringKey` when you pass a string literal. This means SwiftUI will **automatically look up** `"Share"` in your String Catalog (`.xcstrings`) or `.strings` file for localization.

So the good news is that if you pass a string literal, SwiftUI treats it as a localization key automatically.

## What You Need to Ensure

1. **The key must exist in your String Catalog / .strings file.** The auto-localization only works if you have provided translations for the key `"Share"` in each language you support. If the key is missing, it will just display `"Share"` in English.

2. **Consider using a semantic key with a translator comment** for better translation quality:

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel(Text("share_button.accessibility",
        comment: "Accessibility label for button that shares current content"))
```

Using a semantic key like `"share_button.accessibility"` instead of the English word `"Share"` avoids ambiguity -- translators will know this is an action button label, not the noun "share" (as in a stock share).

## Variables vs Literals

Be aware that if you use a variable instead of a literal, auto-localization does not happen:

```swift
let label = "Share"
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel(label) // This uses String, NOT LocalizedStringKey -- no localization!
```

To fix this with a variable, explicitly wrap it:

```swift
.accessibilityLabel(Text(LocalizedStringKey(label)))
```

## Summary

- String literals in `.accessibilityLabel()` auto-localize via `LocalizedStringKey`.
- Make sure the translations exist in your localization files.
- Prefer semantic keys with comments for clarity.
- Variables require explicit `LocalizedStringKey` conversion.
