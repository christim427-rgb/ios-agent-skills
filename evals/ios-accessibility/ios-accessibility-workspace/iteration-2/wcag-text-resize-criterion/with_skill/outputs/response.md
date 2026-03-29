# WCAG Criterion for Text Resizing

## The Criterion: WCAG 1.4.4 Resize Text (Level AA)

**Full requirement:** Text can be resized without assistive technology up to 200 percent without loss of content or functionality.

This is a **Level AA** criterion — required for standard WCAG 2.2 AA compliance, which maps to ADA, EAA, and Section 508 obligations.

The criterion applies at the operating-system level on iOS: users resize text in **Settings > Accessibility > Display & Text Size > Larger Text**, which can scale text from ~80% to 310% of the default size. Apps must respond to this setting without breaking layout, truncating content, or hiding functionality.

## iOS Dynamic Type API Mapping

| WCAG Requirement | iOS API | Notes |
|---|---|---|
| Text scales to 200%+ | Dynamic Type text styles | `.title`, `.body`, `.caption`, etc. auto-scale |
| No loss of content | `numberOfLines = 0` (UIKit) | Prevents truncation |
| No loss of functionality | Layout adapts at large sizes | HStack → VStack switchover |
| Works without AT | System text size setting | No VoiceOver required |

## SwiftUI Implementation

```swift
// ❌ Violates 1.4.4 — fixed size does not respond to user's text size setting
Text("Account Balance")
    .font(.system(size: 17))

// ✅ Satisfies 1.4.4 — scales with Dynamic Type
Text("Account Balance")
    .font(.body)

// ✅ Custom font — scaled relative to a text style
Text("Brand Headline")
    .font(.custom("Roboto-Regular", size: 17, relativeTo: .body))
```

## UIKit Implementation

```swift
// ❌ Violates 1.4.4 — fixed, non-scaling font
label.font = UIFont.systemFont(ofSize: 17)

// ✅ Satisfies 1.4.4 — scales automatically
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true
label.numberOfLines = 0  // Required — prevents truncation at large sizes

// ✅ Custom font scaled with UIFontMetrics
let customFont = UIFont(name: "Roboto-Regular", size: 17)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: customFont)
label.adjustsFontForContentSizeCategory = true
label.numberOfLines = 0
```

## Layout Adaptation at Large Sizes

At accessibility text sizes (xLarge through xxxLarge), horizontal layouts often overflow. Check `dynamicTypeSize` to switch layout direction:

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    // Switches to VStack at accessibility text sizes
    if dynamicTypeSize.isAccessibilitySize {
        VStack(alignment: .leading) {
            Label("Price")
            Text("$9.99")
        }
    } else {
        HStack {
            Label("Price")
            Spacer()
            Text("$9.99")
        }
    }
}
```

Or use `ViewThatFits` (iOS 16+) for automatic switching:

```swift
ViewThatFits {
    HStack { LabelView(); ValueView() }   // Tried first
    VStack { LabelView(); ValueView() }   // Fallback at large sizes
}
```

## Text Style Reference

| `.font(...)` | Default size | Scales to ~310% at xxxLarge |
|---|---|---|
| `.largeTitle` | 34pt | ~105pt |
| `.title` | 28pt | ~88pt |
| `.title2` | 22pt | ~68pt |
| `.title3` | 20pt | ~62pt |
| `.headline` | 17pt bold | ~53pt |
| `.body` | 17pt | ~53pt |
| `.callout` | 16pt | ~50pt |
| `.subheadline` | 15pt | ~47pt |
| `.footnote` | 13pt | ~40pt |
| `.caption` | 12pt | ~37pt |
| `.caption2` | 11pt | ~34pt |

## Related WCAG Criteria

- **1.4.10 Reflow (AA)** — Content must reflow at 320px equivalent width without horizontal scrolling. On iOS: wrap HStack content in VStack at accessibility sizes.
- **1.4.12 Text Spacing** — Does NOT apply to native iOS apps; applies only to markup-based (WebView) content.
