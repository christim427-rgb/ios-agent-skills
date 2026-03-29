# Difference Between Image(decorative:) and Image("name").accessibilityHidden(true)

## Image(decorative:)

Introduced in SwiftUI, this initializer signals at creation time that the image is purely decorative and should not be exposed to assistive technologies.

```swift
Image(decorative: "backgroundPattern")
```

- The image is completely hidden from VoiceOver.
- No accessibility element is created for it.
- The intent is communicated at the API level — it's clear to readers of the code that this image is decorative by design.
- Available from iOS 14+.

## Image("name").accessibilityHidden(true)

This loads a regular image and then applies a modifier to hide it from accessibility:

```swift
Image("backgroundPattern")
    .accessibilityHidden(true)
```

- The image is loaded as a normal accessibility element and then suppressed by the modifier.
- The result is functionally the same as `Image(decorative:)` for VoiceOver.
- The intent is less clear from the call site alone — a reader might wonder if the modifier was applied correctly or if it was an oversight.

## Key Differences

| Aspect | `Image(decorative:)` | `.accessibilityHidden(true)` |
|---|---|---|
| Availability | iOS 14+ | iOS 14+ |
| VoiceOver behavior | Hidden | Hidden |
| Intent clarity | Explicit at init | Explicit via modifier |
| Works on non-Image views | No | Yes (any view) |
| Works with SF Symbols | `Image(decorative: systemName:)` | Yes |
| Can be toggled dynamically | No (baked into init) | Yes (can be conditional) |

## When to Use Each

**Use `Image(decorative:)`** when:
- The image is always and unconditionally decorative.
- It's an asset image (named from the asset catalog).
- You want the intent clear in the initializer.

**Use `.accessibilityHidden(true)`** when:
- You need to conditionally hide/show an element to VoiceOver based on state.
- You're hiding something other than an `Image` (a `VStack`, `ZStack`, etc.).
- You need compatibility with a pattern where other modifiers are already chained.

```swift
// Conditional hiding based on state
Image("statusIcon")
    .accessibilityHidden(!showToVoiceOver)

// Always decorative — prefer Image(decorative:)
Image(decorative: "dividerLine")
```

## Important Note on SF Symbols

```swift
// For a decorative SF Symbol:
Image(decorative: systemName: "circle.fill")

// Or:
Image(systemName: "circle.fill")
    .accessibilityHidden(true)
```

Without hiding, `Image(systemName:)` will attempt to derive a label from the symbol name — which is sometimes correct ("checkmark") and sometimes confusing ("chevron.right.2").
