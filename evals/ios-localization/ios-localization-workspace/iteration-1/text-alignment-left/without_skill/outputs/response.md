# Text Alignment: `.left` vs `.natural` in a Localized App

## Recommendation: Use `.natural`

In a localized app, you should use **`.natural`** text alignment, not `.left`.

## Why `.natural`?

`NSTextAlignment.natural` (or `.natural` in SwiftUI) automatically adapts based on the user's language direction:

- For **Left-to-Right (LTR)** languages like English, French, and German, `.natural` resolves to **left-aligned** text.
- For **Right-to-Left (RTL)** languages like Arabic and Hebrew, `.natural` resolves to **right-aligned** text.

## Why Not `.left`?

`NSTextAlignment.left` is an **absolute** alignment. It always aligns text to the left side of the container, regardless of the language direction. For RTL users, this means text will be incorrectly pinned to the left when it should flow from right to left.

## Code Examples

### UIKit
```swift
// Correct for localized apps
label.textAlignment = .natural

// Wrong for localized apps (stays left for Arabic/Hebrew)
label.textAlignment = .left
```

### SwiftUI
SwiftUI's `Text` view uses `.natural` alignment by default, so you typically don't need to set it explicitly. If you do need to set alignment:

```swift
Text("Hello")
    .multilineTextAlignment(.leading) // Use .leading, not .center or .trailing for body text
```

## When to Use `.left`

Only use `.left` when you intentionally want text to stay left-aligned regardless of language -- for example, left-aligned numeric codes or identifiers that should never flip.
