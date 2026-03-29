# Making Custom Fonts Respect Dynamic Type in UIKit

The problem with your current code is that `UIFont(name:size:)` creates a font with a fixed size that never changes, even when the user adjusts their preferred text size in Settings.

## The Solution: `UIFontMetrics`

`UIFontMetrics` (available since iOS 11) is the correct way to scale a custom font alongside Dynamic Type. It takes a base font at a specific size and scales it proportionally based on the user's content size category.

```swift
// 1. Create your custom font at the base size
let baseFont = UIFont(name: "Avenir-Medium", size: 17)!

// 2. Scale it using UIFontMetrics, tied to a text style
let scaledFont = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)

// 3. Assign to the label and enable automatic adjustment
label.font = scaledFont
label.adjustsFontForContentSizeCategory = true
```

### Why each part matters

- **`UIFontMetrics(forTextStyle:)`** — ties the scaling curve to a semantic text style (`.body`, `.headline`, `.caption1`, etc.). The system uses the same scaling curve it uses for the built-in San Francisco text style, so your custom font grows and shrinks at the same rate as system text.
- **`scaledFont(for:)`** — returns a new font descriptor that the system can dynamically resize. The `17` pt you pass in is the size at the default (Large) content size category.
- **`adjustsFontForContentSizeCategory = true`** — tells the label to automatically re-query its font when the user changes their preferred text size. Without this, the font is only scaled once at creation time; changes made while the app is running won't be reflected.

## Choosing the Right Text Style

Match the text style to the role of the label in your UI:

| Text Style | Typical Use |
|---|---|
| `.largeTitle` | Large display headers |
| `.title1` / `.title2` / `.title3` | Section headers |
| `.headline` | Primary emphasized body text |
| `.body` | Standard body copy |
| `.callout` | Slightly smaller body copy |
| `.subheadline` | Supporting detail text |
| `.footnote` | Fine print, timestamps |
| `.caption1` / `.caption2` | Image captions, smallest text |

A 17 pt font using `.body` is a natural fit since 17 pt is the default size of `.body` in the system.

## Respecting the "Accessibility Sizes" (Optional but Recommended)

By default, `UIFontMetrics` will scale up to the largest non-accessibility size. To also support the five extra-large accessibility sizes (when the user has enabled larger accessibility sizes in Settings), pass a `maximumPointSize` or simply omit the cap:

```swift
// No cap — font scales all the way through accessibility sizes
let scaledFont = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)

// With a cap — font stops growing at 28 pt regardless of setting
let cappedFont = UIFontMetrics(forTextStyle: .body)
    .scaledFont(for: baseFont, maximumPointSize: 28)
```

Most apps should avoid the cap unless a layout genuinely cannot accommodate larger text.

## Complete Example

```swift
import UIKit

class MyViewController: UIViewController {

    private let label: UILabel = {
        let label = UILabel()
        label.numberOfLines = 0

        let baseFont = UIFont(name: "Avenir-Medium", size: 17) ?? UIFont.systemFont(ofSize: 17, weight: .medium)
        label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)
        label.adjustsFontForContentSizeCategory = true

        return label
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        label.text = "Hello, Dynamic Type!"
        view.addSubview(label)
        // ... layout constraints
    }
}
```

The `?? UIFont.systemFont(ofSize:weight:)` fallback is good practice in case the font name is mistyped or the font is not bundled — it prevents a crash and degrades gracefully to the system font.

## Testing

Test Dynamic Type in the Simulator via **Features > Toggle Increased Contrast** and the **Accessibility Inspector** (`Xcode > Open Developer Tool > Accessibility Inspector`). On device, go to **Settings > Accessibility > Display & Text Size > Larger Text** and drag the slider.

You can also test in code:

```swift
// Force a specific content size category for UI testing
label.overrideUserInterfaceStyle = .unspecified
// or at the view controller level:
// overridePreferredContentSizeCategory = .accessibilityExtraExtraExtraLarge
```
