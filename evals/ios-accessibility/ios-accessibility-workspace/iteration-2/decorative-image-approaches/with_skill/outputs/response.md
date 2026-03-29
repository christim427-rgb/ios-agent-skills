# Decorative Images: Image(decorative:) vs .accessibilityHidden(true)

## Both Hide from VoiceOver — But They Are Not Equivalent

Both approaches prevent VoiceOver from announcing an image. The difference is intent and API clarity.

## Image(decorative:) — Preferred SwiftUI Approach

```swift
// ✅ Preferred — explicitly declares this image is decorative at the call site
Image(decorative: "background-gradient")
Image(decorative: "divider-line")
Image(decorative: "hero-illustration")
```

`Image(decorative:)` is the SwiftUI-native way to declare that an image is purely visual and carries no information. The keyword `decorative` communicates intent directly in code — anyone reading it immediately understands why this image has no label.

VoiceOver behavior: the image is not focusable, not announced, and not included in the accessibility tree at all.

## .accessibilityHidden(true) — Valid Alternative

```swift
// ✅ Also correct — hides from VoiceOver
Image("separator")
    .accessibilityHidden(true)
```

`.accessibilityHidden(true)` is a modifier that can be applied to any view, not just images. It is more versatile but slightly more verbose for the simple "this image is decorative" case.

**When to use `.accessibilityHidden(true)` instead:**
- When the view is not an `Image` but should be hidden from VoiceOver (e.g., a decorative `Shape`, `Rectangle`, or `Canvas` background)
- When hiding conditionally based on state

```swift
// Conditional hiding
Image("status-indicator")
    .accessibilityHidden(!isUserFacing)

// Non-image decorative view
Rectangle()
    .fill(LinearGradient(...))
    .accessibilityHidden(true)
```

## Side-by-Side Comparison

```swift
// Image(decorative:) — preferred, declarative
Image(decorative: "star-background")

// .accessibilityHidden(true) — equivalent result, more verbose
Image("star-background")
    .accessibilityHidden(true)
```

Both produce the same accessibility tree result. `Image(decorative:)` is more idiomatic for SwiftUI.

## What NOT to Do

```swift
// ❌ Wrong — empty string label does not hide from VoiceOver, it just announces silence
Image("background")
    .accessibilityLabel("")

// ❌ Wrong — Image(systemName:) without a label or decorative declaration
//    VoiceOver will read the SF Symbol name ("star.fill")
Image(systemName: "star.fill")
// Should be:
Image(decorative: systemName: "star.fill")  // SF Symbol decorative variant
// Or:
Image(systemName: "star.fill")
    .accessibilityHidden(true)
```

## SF Symbols: Decorative Variant

For decorative SF Symbols, there is a dedicated initializer:

```swift
// ✅ Decorative SF Symbol
Image(systemName: "star.fill")
    .accessibilityHidden(true)

// Or using the labeled overload with empty label (not recommended — use .accessibilityHidden instead)
```

## When Is an Image Decorative?

Rule of thumb: if removing the image changes the meaning of the screen or loses information, it is **informative** and needs a label. If it is purely aesthetic (background pattern, divider, illustration that duplicates nearby text), it is **decorative**.

| Image | Decorative? |
|---|---|
| Profile photo in a contact card | No — informative, needs label |
| Background gradient | Yes — purely aesthetic |
| Star icons in a rating display (when "4.5 stars" text is present) | Yes — information conveyed by text |
| Chart bar representing a data value | No — informative, needs label and value |
| Divider line between sections | Yes — purely structural |
| Icon in an icon-only button | No — must have label describing the action |

## Grouping Context

When individual images are decorative inside a grouped container that provides a meaningful composite label, hide each image individually:

```swift
// Rating display — stars are decorative, text provides the information
HStack {
    ForEach(0..<5) { i in
        Image(systemName: i < Int(rating) ? "star.fill" : "star")
            .accessibilityHidden(true)
    }
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(rating, specifier: "%.1f") out of 5 stars")
```
