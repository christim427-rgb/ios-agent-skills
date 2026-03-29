# UIKit Custom Font (Avenir) with Dynamic Type via `UIFontMetrics`

## The Problem

Custom fonts in UIKit do not automatically scale with Dynamic Type. Setting `label.font = UIFont(name: "Avenir-Medium", size: 17)` creates a fixed-size font that ignores the user's text size preference. Additionally, UIKit labels default to a single line, clipping content when the font size grows.

---

## The Solution: `UIFontMetrics.scaledFont(for:)`

`UIFontMetrics` acts as a bridge between a custom font and the Dynamic Type size system. You provide a base font at the default size, and `UIFontMetrics` returns a version of that font scaled to match the user's current text size preference.

```swift
// ❌ Fixed size — never scales
let label = UILabel()
label.font = UIFont(name: "Avenir-Medium", size: 17)
```

```swift
// ✅ Scales with Dynamic Type
let label = UILabel()

// 1. Create the base custom font at its default size
let baseFont = UIFont(name: "Avenir-Medium", size: 17)!

// 2. Wrap it with UIFontMetrics tied to a text style
//    This defines the scaling curve — .body scales proportionally to system body text
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)

// 3. Enable live updating when the user changes text size (CRITICAL)
label.adjustsFontForContentSizeCategory = true

// 4. Allow text to wrap at larger sizes
label.numberOfLines = 0
```

**VoiceOver / Accessibility behavior:** When the user changes text size in Settings, UIKit sends `UIContentSizeCategoryDidChangeNotification`. `adjustsFontForContentSizeCategory = true` listens for this notification and re-queries the scaled font automatically. Without it, the label won't update until the view is recreated.

---

## Why Each Line Matters

### `UIFontMetrics(forTextStyle: .body)`

The `forTextStyle:` parameter determines **which scaling curve** your custom font follows. Choose the style that matches the semantic role of this text:

| Your text role | Use style |
|---|---|
| Screen title | `.largeTitle` |
| Section heading | `.title1`, `.title2`, `.title3` |
| Main content | `.body` |
| Supporting text | `.subheadline`, `.callout` |
| Small labels | `.caption1`, `.caption2` |
| Footnotes | `.footnote` |

Tying body text to `.body` means it scales at the same rate as iOS system body text — users get a consistent size relationship between your custom font and the rest of the UI.

### `adjustsFontForContentSizeCategory = true`

Without this, the scaled font is calculated once at view creation. If the user changes text size (Settings → Accessibility → Display & Text Size → Larger Text), the label's font **does not update**. Only views that re-render (e.g., after a navigation push) would pick up the new size.

With `adjustsFontForContentSizeCategory = true`, UIKit automatically re-scales the font when the size category changes — no notification handling needed.

**Important:** This property only works on `UILabel`, `UITextField`, and `UITextView`. It has no effect on arbitrary `UIView` subclasses.

### `numberOfLines = 0`

This allows the label to use as many lines as needed. At large accessibility text sizes, even short phrases may need to wrap. A label with `numberOfLines = 1` (the default) clips or truncates content — breaking WCAG 1.4.4 (Resize Text).

---

## Complete Implementation

```swift
class ProfileHeaderView: UIView {

    private let nameLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false

        // Dynamic Type with custom Avenir font
        guard let baseFont = UIFont(name: "Avenir-Heavy", size: 22) else {
            // Fallback to system font if custom font not available
            label.font = UIFontMetrics(forTextStyle: .title2).scaledFont(
                for: .systemFont(ofSize: 22, weight: .heavy)
            )
            label.adjustsFontForContentSizeCategory = true
            label.numberOfLines = 0
            return label
        }

        label.font = UIFontMetrics(forTextStyle: .title2).scaledFont(for: baseFont)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        return label
    }()

    private let bioLabel: UILabel = {
        let label = UILabel()
        label.translatesAutoresizingMaskIntoConstraints = false

        let baseFont = UIFont(name: "Avenir-Book", size: 15) ?? .systemFont(ofSize: 15)
        label.font = UIFontMetrics(forTextStyle: .subheadline).scaledFont(for: baseFont)
        label.adjustsFontForContentSizeCategory = true
        label.numberOfLines = 0
        label.textColor = .secondaryLabel  // Semantic color — adapts to dark mode
        return label
    }()
}
```

---

## SwiftUI Equivalent

In SwiftUI, use `.custom(_:size:relativeTo:)`:

```swift
// ✅ SwiftUI — custom font with Dynamic Type scaling
Text("John Appleseed")
    .font(.custom("Avenir-Heavy", size: 22, relativeTo: .title2))
```

The `relativeTo:` parameter is the equivalent of `UIFontMetrics(forTextStyle:)`. SwiftUI handles re-scaling automatically — no `adjustsFontForContentSizeCategory` needed.

---

## Testing

1. **Simulator:** Settings → Accessibility → Display & Text Size → Larger Text — drag slider to maximum
2. **Xcode Canvas:** Use the Dynamic Type preview size slider
3. **Accessibility Inspector:** View hierarchy with all 12 text size categories
4. Verify the label wraps gracefully and does not truncate at `accessibilityExtraExtraExtraLarge`
