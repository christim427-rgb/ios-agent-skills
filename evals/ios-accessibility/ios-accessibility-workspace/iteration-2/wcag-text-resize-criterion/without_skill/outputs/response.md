# WCAG Criterion Covering Text Resizing on iOS

## Primary Criterion: 1.4.4 Resize Text (Level AA)

> "Except for captions and images of text, text can be resized without assistive technology up to 200 percent without loss of content or functionality."

On iOS, this maps to **Dynamic Type** support. The user can change the system text size in Settings > Display & Brightness > Text Size (or Accessibility > Larger Text for even larger sizes), and apps must adapt their layouts to accommodate this without truncating content, overlapping elements, or breaking functionality.

### What This Requires from iOS Developers

- Use `UIFont.preferredFont(forTextStyle:)` or `.font(.body)` / `.font(.headline)` in SwiftUI rather than fixed point sizes.
- Enable `adjustsFontForContentSizeCategory = true` on UILabel/UITextField in UIKit.
- Ensure layouts scroll or wrap rather than clipping content at large sizes.
- Test at the largest accessibility text sizes (AX1–AX5).

## Related Criterion: 1.4.12 Text Spacing (Level AA, WCAG 2.1)

> "No loss of content or functionality occurs when letter spacing, word spacing, line height, or paragraph spacing is increased."

While this is more commonly a web concern, it applies to custom text rendering in iOS apps.

## Related Criterion: 1.4.10 Reflow (Level AA, WCAG 2.1)

> "Content can be presented without loss of information or functionality, and without requiring scrolling in two dimensions."

On iOS, this means that at large text sizes, content should reflow vertically (scrollable in one direction) rather than requiring horizontal scrolling as well.

## iOS-Specific Notes

- Apple's **Accessibility Text Sizes** (the 5 extra-large sizes beyond the standard 7) go well beyond WCAG's 200% requirement. Supporting them fully is best practice.
- `UIContentSizeCategory.accessibilityExtraExtraExtraLarge` is the largest size.
- Use `UIContentSizeCategoryAdjusting` protocol methods and Auto Layout constraints that allow height to grow.
- In SwiftUI, prefer `@ScaledMetric` for non-text dimensions (icon sizes, spacing) that should scale alongside text.

```swift
@ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 24
```

## Testing

- Accessibility Inspector (Xcode) can simulate all Dynamic Type sizes.
- Test by going to Settings > Accessibility > Display & Text Size > Larger Text on a real device.
