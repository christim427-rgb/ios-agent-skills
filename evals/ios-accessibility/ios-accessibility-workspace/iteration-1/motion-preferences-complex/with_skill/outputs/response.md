# System Accessibility Preferences for a Truly Adaptive iOS UI

Beyond Reduce Motion, iOS exposes six additional system accessibility preferences you should check to build a truly adaptive UI. Each maps to a SwiftUI `@Environment` key or a UIKit trait/API, and each failing to respect it is classified as a **HIGH** severity issue — meaning the UI breaks under that user's system settings.

---

## 1. Reduce Motion (`accessibilityReduceMotion`)

Starting here as the baseline, since you already know it.

**What it signals:** The user experiences vestibular disorders, motion sickness, or discomfort from spatial animation.

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring()) {
    showDetail.toggle()
}

// For transitions:
.transition(reduceMotion ? .opacity : .slide)
```

**Key principle:** Do not remove animation entirely — replace aggressive spatial motion (slides, scales, 3D transforms, springs) with a subtle crossfade/opacity change. Complete removal of feedback feels broken.

**Animations that always need a reduce-motion alternative:**
- Parallax effects, scaling/zooming transitions
- Sliding or pushing transitions
- Spinning or rotating animations
- Auto-scrolling carousels, auto-playing video
- Bouncing springs

**Safe without an alternative:** opacity/crossfade, color changes, simple state changes without spatial movement.

**UIKit equivalent:**
```swift
UIAccessibility.isReduceMotionEnabled
```

---

## 2. Increase Contrast (`colorSchemeContrast` / `accessibilityContrast`)

**What it signals:** The user has low vision or difficulty distinguishing elements with standard contrast. They have explicitly asked for higher contrast throughout the system.

**WCAG baseline:** 4.5:1 for normal text, 3:1 for large text and UI components (AA). When Increase Contrast is enabled, target 7:1 for text (AAA level).

```swift
// SwiftUI
@Environment(\.colorSchemeContrast) var contrast

var borderColor: Color {
    contrast == .increased ? Color(.label) : Color(.separator)
}

// UIKit
if traitCollection.accessibilityContrast == .high {
    layer.borderColor = UIColor.label.cgColor
    layer.borderWidth = 2
}
```

**Asset catalog approach:** Define four color variants per asset:
- Any Appearance
- Dark Appearance
- Any High Contrast
- Dark High Contrast

System semantic colors (`.label`, `.systemBackground`, etc.) adapt automatically. Custom colors need explicit high-contrast variants.

---

## 3. Reduce Transparency (`accessibilityReduceTransparency`)

**What it signals:** The user finds translucent/blurred elements hard to read — blur-behind and vibrancy effects reduce legibility for many low-vision users.

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency

.background(
    reduceTransparency
        ? AnyShapeStyle(Color(.systemBackground))
        : AnyShapeStyle(.ultraThinMaterial)
)
```

**What to replace when enabled:**
- `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial` → `Color(.systemBackground)` or `Color(.secondarySystemBackground)`
- `.blur()` effects → solid background
- Any translucent overlay → opaque equivalent with sufficient contrast

**UIKit equivalent:**
```swift
UIAccessibility.isReduceTransparencyEnabled
```

---

## 4. Differentiate Without Color (`accessibilityDifferentiateWithoutColor`)

**What it signals:** The user has a color vision deficiency (affects ~8% of men, ~0.5% of women). Color alone cannot be the sole indicator of state, status, or meaning.

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var diffWithoutColor

// Status indicator — never color-only
HStack {
    if diffWithoutColor {
        Image(systemName: isOnline ? "checkmark.circle.fill" : "xmark.circle.fill")
    } else {
        Circle().fill(isOnline ? .green : .red)
    }
    Text(isOnline ? "Online" : "Offline")
}
```

**This preference is additive to good baseline design.** Best practice is to never use color as the sole indicator regardless of this flag — always pair color with shape, icon, pattern, or text. The environment key lets you provide enhanced non-color cues for users who have explicitly signaled they need them.

**UIKit equivalent:**
```swift
UIAccessibility.shouldDifferentiateWithoutColor
```

---

## 5. Dynamic Type Size (`dynamicTypeSize`)

**What it signals:** The user has changed their preferred text size — either smaller for density, or larger (including the five Accessibility sizes beyond the standard range) for readability. Roughly 25%+ of users have a non-default text size setting.

```swift
@Environment(\.dynamicTypeSize) var typeSize

// Adapt layout at accessibility sizes
var body: some View {
    if typeSize.isAccessibilitySize {
        VStack(alignment: .leading) { content }
    } else {
        HStack { content }
    }
}
```

**The prerequisite — never hardcode font sizes:**
```swift
// Never
.font(.system(size: 17))

// Always — Dynamic Type text style
.font(.body)

// Custom font that still scales
.font(.custom("MyFont", size: 17, relativeTo: .body))

// UIKit
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)
label.adjustsFontForContentSizeCategory = true
```

**Use `@ScaledMetric` for non-text dimensions that should grow with type size:**
```swift
@ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 24
Image(systemName: "star").frame(width: iconSize, height: iconSize)
```

**Use `ViewThatFits` (iOS 16+) for layout adaptation:**
```swift
ViewThatFits {
    HStack { label; value }  // preferred
    VStack { label; value }  // fallback at large sizes
}
```

---

## 6. Smart Invert Colors (`accessibilityIgnoresInvertColors`)

**What it signals:** The user is using Smart Invert Colors (a low-vision aid that inverts most of the screen). Smart Invert is intelligent enough to skip images — but only if you opt out correctly.

```swift
// SwiftUI — opt a view out of inversion
Image("product-photo")
    .accessibilityIgnoresInvertColors(true)

// UIKit
imageView.accessibilityIgnoresInvertColors = true
```

**Always set on:**
- Photos and real-world images
- Video player views
- Maps
- User-generated content (profile avatars, user photos)
- Color pickers or any UI where color fidelity is meaningful

Setting this property on a parent view cascades to all subviews, so you can opt out an entire media container at once.

Using semantic system colors (`.label`, `.systemBackground`, `.tint`) ensures text and chrome invert correctly without any extra work.

---

## Complete SwiftUI Environment Key Reference

| Preference | Environment Key | UIKit Equivalent |
|---|---|---|
| Reduce Motion | `\.accessibilityReduceMotion` | `UIAccessibility.isReduceMotionEnabled` |
| Increase Contrast | `\.colorSchemeContrast` (`.increased`) | `traitCollection.accessibilityContrast == .high` |
| Reduce Transparency | `\.accessibilityReduceTransparency` | `UIAccessibility.isReduceTransparencyEnabled` |
| Differentiate Without Color | `\.accessibilityDifferentiateWithoutColor` | `UIAccessibility.shouldDifferentiateWithoutColor` |
| Dynamic Type Size | `\.dynamicTypeSize` | `traitCollection.preferredContentSizeCategory` |
| Smart Invert | `accessibilityIgnoresInvertColors(_:)` modifier | `view.accessibilityIgnoresInvertColors` |

---

## Recommended Implementation Pattern

Check all preferences at the view level where they're relevant, or create an environment object that aggregates them for use across the app:

```swift
struct AdaptiveUIEnvironment: EnvironmentKey {
    static let defaultValue = AdaptiveUIEnvironment()
}

// Or read directly in each view where needed:
struct AdaptiveCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    @Environment(\.colorSchemeContrast) var contrast
    @Environment(\.accessibilityDifferentiateWithoutColor) var diffWithoutColor
    @Environment(\.dynamicTypeSize) var typeSize

    var body: some View {
        content
            .background(
                reduceTransparency
                    ? AnyShapeStyle(Color(.systemBackground))
                    : AnyShapeStyle(.ultraThinMaterial)
            )
            .overlay(
                contrast == .increased
                    ? RoundedRectangle(cornerRadius: 12).stroke(Color(.label), lineWidth: 1)
                    : nil
            )
    }
}
```

---

## Severity Summary

All six preferences carry a **HIGH** severity when ignored — the UI breaks under that user's system settings:

| Preference | Effect if Ignored |
|---|---|
| Reduce Motion | Vestibular symptoms; nausea; disorientation |
| Increase Contrast | Text/UI becomes unreadable for low-vision users |
| Reduce Transparency | Blurred overlays obscure content, reduce legibility |
| Differentiate Without Color | State/status invisible to colorblind users |
| Dynamic Type | Text unreadable at large sizes; layout breaks at accessibility sizes |
| Smart Invert | Photos/videos appear incorrectly inverted; color pickers unusable |

A truly adaptive UI reads all six, responds to each, and tests with each enabled — both individually and in combination (e.g., Dark Mode + Increase Contrast + Reduce Transparency is a common configuration for low-vision users).
