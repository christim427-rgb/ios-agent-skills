# Fixing Blur Effects for Reduce Transparency

## The Problem

When a user enables **Settings > Accessibility > Display & Text Size > Reduce Transparency**, `.ultraThinMaterial` and other blur/translucency effects become unreadable. The system requests that apps replace semi-transparent layers with solid opaque backgrounds — but apps that hardcode material styles ignore this preference entirely.

This is a **🟡 HIGH** severity issue: the app breaks under an active system accessibility setting.

## The Fix

Read the `accessibilityReduceTransparency` environment value in SwiftUI and conditionally substitute a solid background for every material/blur usage.

### SwiftUI — Single View

```swift
// ❌ Before: always blurred, unreadable with reduce transparency enabled
struct CardView: View {
    var body: some View {
        Text("Account Balance")
            .padding()
            .background(.ultraThinMaterial)
            .clipShape(.rect(cornerRadius: 12))
    }
}

// ✅ After: respects Reduce Transparency
struct CardView: View {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    var body: some View {
        Text("Account Balance")
            .padding()
            .background(
                reduceTransparency
                    ? AnyShapeStyle(Color(.systemBackground))
                    : AnyShapeStyle(.ultraThinMaterial)
            )
            .clipShape(.rect(cornerRadius: 12))
    }
}
```

### SwiftUI — Reusable ViewModifier (recommended for apps with extensive blur usage)

Create a single modifier so you don't duplicate the environment check across every view:

```swift
struct AdaptiveBackground: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency

    let material: Material
    let fallback: Color

    func body(content: Content) -> some View {
        content.background(
            reduceTransparency
                ? AnyShapeStyle(fallback)
                : AnyShapeStyle(material)
        )
    }
}

extension View {
    func adaptiveBackground(
        _ material: Material = .ultraThinMaterial,
        fallback: Color = Color(.systemBackground)
    ) -> some View {
        modifier(AdaptiveBackground(material: material, fallback: fallback))
    }
}

// Usage — replaces every raw .background(.ultraThinMaterial) in the app:
Text("Account Balance")
    .padding()
    .adaptiveBackground()
    .clipShape(.rect(cornerRadius: 12))
```

### UIKit

```swift
final class FrostedCardView: UIView {
    private let blurView = UIVisualEffectView(effect: UIBlurEffect(style: .systemUltraThinMaterial))
    private let solidView = UIView()

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupViews()
        applyAccessibilityState()
    }

    private func setupViews() {
        solidView.backgroundColor = .systemBackground
        addSubview(blurView)
        addSubview(solidView)
        // Pin both to edges via Auto Layout...
    }

    // Called when trait collection changes (e.g., user toggles setting without relaunch)
    override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
        super.traitCollectionDidChange(previousTraitCollection)
        applyAccessibilityState()
    }

    private func applyAccessibilityState() {
        let reduce = UIAccessibility.isReduceTransparencyEnabled
        blurView.isHidden = reduce
        solidView.isHidden = !reduce
    }
}
```

For UIKit you can also observe the notification to update live:

```swift
NotificationCenter.default.addObserver(
    self,
    selector: #selector(reduceTransparencyChanged),
    name: UIAccessibility.reduceTransparencyStatusDidChangeNotification,
    object: nil
)

@objc private func reduceTransparencyChanged() {
    applyAccessibilityState()
}
```

## What to Replace

| Original usage | Opaque fallback |
|---|---|
| `.ultraThinMaterial` | `Color(.systemBackground)` |
| `.thinMaterial` | `Color(.systemBackground)` |
| `.regularMaterial` | `Color(.secondarySystemBackground)` |
| `.thickMaterial` | `Color(.secondarySystemBackground)` |
| `.blur(radius:)` modifier | Remove the modifier; use a solid tinted background |
| `UIVisualEffectView` (any blur style) | Swap for a `UIView` with `.systemBackground` fill |

Always use **semantic system colors** (`Color(.systemBackground)`, `Color(.secondarySystemBackground)`) as the fallback — never hardcoded `.white` or `.black`, which break in dark mode.

## Confidence Checklist

After applying the fix, verify:

- [ ] Every `.background(.ultraThinMaterial)` and similar usages now branch on `reduceTransparency`
- [ ] Fallback colors use semantic system colors, not hardcoded values
- [ ] UIKit views respond to `UIAccessibility.reduceTransparencyStatusDidChangeNotification` so live-toggling the setting works without relaunch
- [ ] The replacement background provides sufficient contrast (WCAG AA: 4.5:1 for normal text, 3:1 for large text)
- [ ] Tested in both light and dark modes with Reduce Transparency enabled

## WCAG Mapping

| Criterion | Requirement |
|---|---|
| 1.4.3 Contrast (Minimum) — AA | Text over blurred areas must meet 4.5:1; replacing blur with a solid background makes this measurable and achievable |
| 1.4.11 Non-text Contrast — AA | UI component boundaries must remain visible at 3:1 |

Apple HIG guidance: apps should always honor the Reduce Transparency preference. Ignoring it violates the principle that users can override display preferences when needed for legibility.
