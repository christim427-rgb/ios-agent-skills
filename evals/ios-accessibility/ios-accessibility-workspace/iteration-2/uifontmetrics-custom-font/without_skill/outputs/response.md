## Adding Dynamic Type Support to a Custom UIKit Font (Avenir)

### The Problem

A raw `UIFont(name:size:)` call creates a font at a fixed size that never scales with the user's Dynamic Type setting.

### Solution: `UIFontMetrics`

`UIFontMetrics` (available since iOS 11) scales a custom font proportionally using the same scaling curve as a named text style. You pair your custom font with a semantic style to determine how aggressively it scales.

### Step-by-Step Implementation

#### 1. Create the base font at its default (medium) size

```swift
guard let avenirFont = UIFont(name: "Avenir-Medium", size: 17) else {
    // Fallback to system font if Avenir is unavailable
    return UIFont.preferredFont(forTextStyle: .body)
}
```

#### 2. Scale it with `UIFontMetrics`

```swift
let scaledFont = UIFontMetrics(forTextStyle: .body).scaledFont(for: avenirFont)
```

The `forTextStyle:` parameter tells `UIFontMetrics` which scaling curve to use. Match it to the visual role of the text:

| Visual Role | Text Style |
|------------|------------|
| Body copy | `.body` |
| Large title | `.largeTitle` |
| Section heading | `.headline` |
| Small caption | `.caption1` |
| Footnote | `.footnote` |

#### 3. Enable automatic font adjustment on the label

```swift
label.font = scaledFont
label.adjustsFontForContentSizeCategory = true
```

Without `adjustsFontForContentSizeCategory = true`, the font is scaled once at creation time but does **not** update live when the user changes their text size preference.

---

### Full Helper Function

```swift
func avenirFont(ofSize baseSize: CGFloat, style: UIFont.TextStyle = .body) -> UIFont {
    let font = UIFont(name: "Avenir-Medium", size: baseSize)
              ?? UIFont.systemFont(ofSize: baseSize)
    return UIFontMetrics(forTextStyle: style).scaledFont(for: font)
}

// Usage:
titleLabel.font = avenirFont(ofSize: 28, style: .title1)
titleLabel.adjustsFontForContentSizeCategory = true

bodyLabel.font = avenirFont(ofSize: 17, style: .body)
bodyLabel.adjustsFontForContentSizeCategory = true
```

---

### Capping Maximum Size (Optional)

If the layout breaks at the largest accessibility sizes, you can set a maximum scaled value:

```swift
let scaledFont = UIFontMetrics(forTextStyle: .body)
    .scaledFont(for: avenirFont, maximumPointSize: 28)
```

Use this sparingly — capping the size means the user's preference is partially ignored. Prefer redesigning the layout to accommodate larger text.

---

### SwiftUI Equivalent

In SwiftUI, `.custom(_:size:relativeTo:)` achieves the same result:

```swift
Text("Hello")
    .font(.custom("Avenir-Medium", size: 17, relativeTo: .body))
```

SwiftUI handles scaling automatically when using `relativeTo:`.
