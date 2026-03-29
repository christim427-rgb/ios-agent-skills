# System Accessibility Preferences Beyond Reduce Motion

iOS exposes multiple system preferences through `@Environment` in SwiftUI. Each requires specific code-level responses. Reduce Motion is just one of six preferences that demand attention.

## Complete Preference Reference

### 1. Reduce Transparency — `accessibilityReduceTransparency`

Blurred/translucent backgrounds become unreadable for some users. Replace materials with solid backgrounds.

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

.background(
    reduceTransparency
        ? AnyShapeStyle(Color(.systemBackground))
        : AnyShapeStyle(.ultraThinMaterial)
)
```

Replace: `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial`, `.blur()` effects.
Use: `Color(.systemBackground)`, `Color(.secondarySystemBackground)`.

---

### 2. Differentiate Without Color — `accessibilityDifferentiateWithoutColor`

~8% of men and ~0.5% of women have color vision deficiency. When enabled, supplement color-only indicators with shapes, icons, or text.

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var diffWithoutColor

// Status indicator
HStack {
    if diffWithoutColor {
        Image(systemName: isOnline ? "checkmark.circle.fill" : "xmark.circle.fill")
    }
    Circle()
        .fill(isOnline ? Color.green : Color.red)
        .frame(width: 10, height: 10)
    Text(isOnline ? "Online" : "Offline")
}
```

---

### 3. Bold Text / Legibility Weight — `legibilityWeight`

When "Bold Text" is enabled in Settings, `legibilityWeight` returns `.bold`.

```swift
@Environment(\.legibilityWeight) var legibilityWeight

Text("Account Balance")
    .font(.headline)
    .fontWeight(legibilityWeight == .bold ? .heavy : .semibold)
```

Note: Dynamic Type text styles (`Font.headline`, `.body`, etc.) automatically honor Bold Text. This environment value is useful only when you need to apply additional weight adjustments to custom typography.

---

### 4. Increase Contrast — `colorSchemeContrast`

Some users need higher contrast ratios (7:1 instead of 4.5:1). Use semantic system colors which adapt automatically, or check `colorSchemeContrast` for custom colors.

```swift
@Environment(\.colorSchemeContrast) var colorSchemeContrast

let borderColor: Color = colorSchemeContrast == .increased
    ? Color(.label)                  // Maximum contrast border
    : Color(.separator)              // Standard separator

RoundedRectangle(cornerRadius: 8)
    .stroke(borderColor, lineWidth: colorSchemeContrast == .increased ? 2 : 1)
```

UIKit equivalent:
```swift
if traitCollection.accessibilityContrast == .high {
    // Apply high-contrast styling
}
```

---

### 5. Smart Invert / Invert Colors — `accessibilityIgnoresInvertColors`

Smart Invert inverts most UI colors but should NOT invert real-world content (photos, videos, maps). Apply `accessibilityIgnoresInvertColors` to protect such content.

```swift
// SwiftUI — prevents inversion on this view and its subviews
Image("user-photo")
    .accessibilityIgnoresInvertColors(true)

// UIKit
imageView.accessibilityIgnoresInvertColors = true
```

Apply to:
- All photos and real-world images
- Video players
- Maps
- User-generated image content
- Color swatches

Setting on a parent **cascades to all subviews** — set it on a photo container view to protect all photos within.

---

### 6. Reduce Motion — `accessibilityReduceMotion`

Shown for completeness alongside the others.

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

.animation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(), value: state)
.transition(reduceMotion ? .opacity : .slide)
```

---

## Decision Table

| Setting | `@Environment` key | Action When Enabled |
|---|---|---|
| Reduce Motion | `\.accessibilityReduceMotion` | Replace spring/slide with crossfade/easeInOut |
| Reduce Transparency | `\.accessibilityReduceTransparency` | Replace materials with solid `Color(.systemBackground)` |
| Differentiate Without Color | `\.accessibilityDifferentiateWithoutColor` | Add icons/shapes alongside color indicators |
| Bold Text | `\.legibilityWeight` | Value is `.bold` — increase font weight if using custom weights |
| Increase Contrast | `\.colorSchemeContrast` | Value is `.increased` — use 7:1 ratios, darker borders |
| Smart Invert | (applied to view, not environment) | `.accessibilityIgnoresInvertColors(true)` on photos/video |

## Comprehensive Check in a View

```swift
struct AccessibleContentView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    @Environment(\.accessibilityDifferentiateWithoutColor) var diffWithoutColor
    @Environment(\.legibilityWeight) var legibilityWeight
    @Environment(\.colorSchemeContrast) var colorSchemeContrast

    var body: some View {
        // Use these flags throughout the view hierarchy
    }
}
```
