# Fixing Blur Effects for Reduce Transparency Accessibility Setting

## The Problem

When a user enables **Settings > Accessibility > Display & Text Size > Reduce Transparency**, iOS replaces translucent/blur effects with solid backgrounds. If your app uses `.ultraThinMaterial` (or any material modifier) as the primary background for content areas, those views may become unreadable — typically showing a flat gray or dark surface with insufficient contrast for text on top.

---

## The Fix: Detect `isReduceTransparencyEnabled` and Provide a Fallback

iOS provides `UIAccessibility.isReduceTransparencyEnabled` (UIKit) and the SwiftUI environment value `\.accessibilityReduceTransparency` to detect this setting at runtime.

### SwiftUI Approach

```swift
struct BlurredCard: View {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency

    var body: some View {
        content
            .background {
                if reduceTransparency {
                    // Solid, opaque fallback with sufficient contrast
                    Color(uiColor: .systemBackground)
                } else {
                    // Normal blur material
                    RoundedRectangle(cornerRadius: 16)
                        .fill(.ultraThinMaterial)
                }
            }
    }

    var content: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Title")
                .font(.headline)
            Text("Body text")
                .font(.body)
        }
        .padding()
    }
}
```

### UIKit Approach

```swift
func updateBackground() {
    if UIAccessibility.isReduceTransparencyEnabled {
        blurView.isHidden = true
        containerView.backgroundColor = .systemBackground
    } else {
        blurView.isHidden = false
        containerView.backgroundColor = .clear
    }
}

override func viewDidLoad() {
    super.viewDidLoad()
    updateBackground()

    NotificationCenter.default.addObserver(
        self,
        selector: #selector(reduceTransparencyChanged),
        name: UIAccessibility.reduceTransparencyStatusDidChangeNotification,
        object: nil
    )
}

@objc func reduceTransparencyChanged() {
    updateBackground()
}
```

---

## Key Principles

### 1. Always React to Runtime Changes
Users can toggle Reduce Transparency without relaunching your app. In UIKit, observe `UIAccessibility.reduceTransparencyStatusDidChangeNotification`. In SwiftUI, `@Environment(\.accessibilityReduceTransparency)` updates automatically.

### 2. Choose Solid Fallback Colors With Sufficient Contrast
Use semantic colors like `.systemBackground`, `.secondarySystemBackground`, or `.tertiarySystemBackground` — they automatically adapt to light/dark mode and provide proper contrast. Avoid arbitrary hardcoded hex colors as fallbacks.

### 3. Ensure Text Contrast on the Fallback Background
If your text color was chosen to look good on a blurred background, double-check it meets WCAG AA contrast ratio (4.5:1 for normal text, 3:1 for large text) on the solid fallback. Use `.label`, `.secondaryLabel`, etc. rather than custom colors where possible.

### 4. Consider Navigation Bars and Tab Bars
System bars handle Reduce Transparency automatically. Custom overlays and cards you build yourself need manual handling.

### 5. Apply Consistently Throughout the App
Audit every place `.ultraThinMaterial`, `.thinMaterial`, `.regularMaterial`, `.thickMaterial`, `.ultraThickMaterial`, or `UIBlurEffect` is used and provide a solid fallback in each case.

---

## Reusable SwiftUI ViewModifier

For apps with many blur surfaces, encapsulate the pattern:

```swift
struct AccessibleMaterialBackground: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    var material: Material = .ultraThinMaterial
    var fallbackColor: Color = Color(uiColor: .systemBackground)
    var shape: AnyShape = AnyShape(Rectangle())

    func body(content: Content) -> some View {
        content.background {
            if reduceTransparency {
                shape.fill(fallbackColor)
            } else {
                shape.fill(material)
            }
        }
    }
}

extension View {
    func accessibleMaterial(
        _ material: Material = .ultraThinMaterial,
        fallback: Color = Color(uiColor: .systemBackground)
    ) -> some View {
        modifier(AccessibleMaterialBackground(material: material, fallbackColor: fallback))
    }
}

// Usage
MyCardView()
    .accessibleMaterial(.ultraThinMaterial, fallback: Color(uiColor: .secondarySystemBackground))
```

---

## Testing

1. Go to **Settings > Accessibility > Display & Text Size > Reduce Transparency** and toggle it on.
2. Return to your app (no restart needed) and verify all previously blurred surfaces now show solid, readable backgrounds.
3. Test in both Light and Dark mode.
4. Use the **Accessibility Inspector** (Xcode > Open Developer Tool > Accessibility Inspector) to check contrast ratios on your fallback surfaces.

---

## Summary

| Context | API to Check | Change Notification |
|---|---|---|
| SwiftUI | `@Environment(\.accessibilityReduceTransparency)` | Automatic (env value) |
| UIKit | `UIAccessibility.isReduceTransparencyEnabled` | `reduceTransparencyStatusDidChangeNotification` |

Replace `.ultraThinMaterial` (and all other material modifiers) with a solid semantic color when `reduceTransparency` is `true`. Use semantic system colors for automatic light/dark adaptation and adequate contrast.
