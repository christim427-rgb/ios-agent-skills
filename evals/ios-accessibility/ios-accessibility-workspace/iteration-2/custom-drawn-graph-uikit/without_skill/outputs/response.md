# Custom drawRect Graph — Making Data Points Accessible to VoiceOver

## The Problem

A view that overrides `draw(_:)` (or `drawRect:` in Objective-C) produces a single bitmap. VoiceOver sees one element — the entire view — with no knowledge of individual data points, bars, or lines within it.

## Solution: UIAccessibilityElement

Create `UIAccessibilityElement` objects programmatically and return them via the `accessibilityElements` array. These virtual elements have frames that map to positions within your custom view.

```swift
class GraphView: UIView {

    var dataPoints: [(label: String, value: Double, frame: CGRect)] = []

    override var isAccessibilityElement: Bool {
        get { false }  // the container itself is not the element
        set { }
    }

    override var accessibilityElements: [Any]? {
        get { buildAccessibilityElements() }
        set { }
    }

    private func buildAccessibilityElements() -> [UIAccessibilityElement] {
        dataPoints.map { point in
            let element = UIAccessibilityElement(accessibilityContainer: self)
            element.accessibilityLabel = point.label
            element.accessibilityValue = String(format: "%.1f", point.value)
            element.accessibilityTraits = .staticText

            // Convert the point's frame from view coordinates to screen coordinates
            element.accessibilityFrameInContainerSpace = point.frame
            return element
        }
    }

    override func draw(_ rect: CGRect) {
        // Your existing drawing code
    }
}
```

### Key Points

- Set `isAccessibilityElement = false` on the container so VoiceOver doesn't treat the whole view as a single opaque element.
- Populate `accessibilityElements` with one `UIAccessibilityElement` per data point.
- Use `accessibilityFrameInContainerSpace` (iOS 10+) — it's in the view's own coordinate space, so you don't need to convert to screen coordinates manually.
- Provide meaningful labels: "January, 42 units" is more useful than "Bar 1".

## Optional: Grouping with Accessibility Container Type

For charts with many data points, consider grouping:

```swift
// iOS 13+
element.accessibilityContainerType = .semanticGroup
```

## SwiftUI Charts (iOS 16+)

If you can migrate to Swift Charts, accessibility is handled automatically — each mark gets an accessible representation. You can customize with `.accessibilityLabel` and `.accessibilityValue` on each `Mark`:

```swift
Chart(data) { item in
    BarMark(x: .value("Month", item.month), y: .value("Sales", item.sales))
        .accessibilityLabel(item.month)
        .accessibilityValue("\(item.sales) units")
}
```

## Notify VoiceOver of Layout Changes

If the data updates after the view draws, post a notification so VoiceOver refreshes its element cache:

```swift
UIAccessibility.post(notification: .layoutChanged, argument: nil)
```
