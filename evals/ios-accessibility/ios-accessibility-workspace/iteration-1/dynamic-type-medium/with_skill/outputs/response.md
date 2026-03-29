# Making Custom Fonts Respect Dynamic Type in UIKit

Your current code sets a fixed font size that never scales, regardless of the user's text size preference:

```swift
// ❌ No Dynamic Type support — fixed at 17pt forever
label.font = UIFont(name: "Avenir-Medium", size: 17)
```

Over 25% of iOS users change their text size setting. This hardcoded approach breaks for all of them and fails WCAG 1.4.4 (Resize Text).

## The Fix: UIFontMetrics

Use `UIFontMetrics` to wrap your custom font and make it scale proportionally with the user's chosen text size:

```swift
// ✅ Scales with Dynamic Type
let customFont = UIFont(name: "Avenir-Medium", size: 17)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
label.numberOfLines = 0
```

### What each line does

**`UIFontMetrics(forTextStyle: .body)`**
Creates a metrics object tied to the `.body` text style. This determines the scaling curve — when the user increases their text size, your 17pt Avenir font scales by the same ratio that `.body` would. Using `.body` for 17pt body text is the correct choice here because `.body` defaults to 17pt at the system default size.

**`.scaledFont(for: customFont)`**
Returns a new `UIFont` that is the scaled version of your custom font at the current content size category. This is recalculated automatically when the user changes their text size, provided the next property is set.

**`adjustsFontForContentSizeCategory = true`**
This is the critical flag. Without it, the font is scaled once at creation time and never updated again — the label will not respond to live changes while your app is running. This property only works on `UILabel`, `UITextField`, and `UITextView`.

**`numberOfLines = 0`**
At accessibility text sizes (the five largest categories), text can be 2–3x its default size. A label capped at one line will truncate most of its content. Set `numberOfLines = 0` so the label wraps naturally.

## Choosing the right text style

The `forTextStyle:` parameter controls the scaling curve. Match it to the semantic role of your label:

| Your label's purpose | Text style to use |
|---|---|
| Main body content | `.body` |
| Primary headline | `.headline` |
| Screen/section title | `.title1` |
| Secondary heading | `.title2` |
| Small captions or metadata | `.caption1` |
| Footnotes, fine print | `.footnote` |

For a 17pt label that functions as body text, `.body` is correct. If this label is actually a heading, switch to `.headline` (also 17pt by default, but semibold and on a different scaling curve).

## Complete example in context

```swift
final class ProfileViewController: UIViewController {

    private let nameLabel: UILabel = {
        let label = UILabel()

        // Custom font with Dynamic Type scaling
        let customFont = UIFont(name: "Avenir-Medium", size: 17)!
        label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)

        // Enable live updates when user changes text size
        label.adjustsFontForContentSizeCategory = true

        // Allow wrapping at large text sizes
        label.numberOfLines = 0

        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
}
```

## Handling layout at accessibility sizes

At the five accessibility text size categories (`accessibilityMedium` through `accessibilityExtraExtraExtraLarge`), your label may expand significantly. If it sits inside an `HStack`-style horizontal layout alongside an image or another label, switch the stack axis:

```swift
override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
    super.traitCollectionDidChange(previousTraitCollection)

    let isAccessibilitySize = traitCollection.preferredContentSizeCategory.isAccessibilityCategory
    contentStackView.axis = isAccessibilitySize ? .vertical : .horizontal
}
```

`isAccessibilityCategory` returns `true` for the five largest size categories and is the correct threshold for layout adaptation.

## Verifying it works

1. Open **Settings > Accessibility > Display & Text Size > Larger Text**
2. Enable **Larger Accessibility Sizes** and drag the slider to maximum
3. Return to your app — the label should grow noticeably and wrap if needed

Alternatively, in Xcode's simulator, use **Features > Toggle Increased Contrast** and the Environment Overrides panel (**Debug > View Debugging > Environment Overrides**) to change the text size without leaving the simulator.

## Summary

| Property | Required | What breaks without it |
|---|---|---|
| `UIFontMetrics.scaledFont(for:)` | Yes | Font stays at its hardcoded size |
| `adjustsFontForContentSizeCategory = true` | Yes | Font only scales at launch, ignores live changes |
| `numberOfLines = 0` | Strongly recommended | Text truncates at accessibility sizes |
