# Making a Custom drawRect Graph Accessible in UIKit

## The Problem

A view that uses `drawRect(_:)` renders pixels directly to a bitmap. There are no subviews, no accessibility elements, and no UIKit controls — VoiceOver has nothing to read. The entire graph is invisible to assistive technology.

```swift
// ❌ VoiceOver: complete silence on this view
class BarChartView: UIView {
    var dataPoints: [DataPoint] = []

    override func draw(_ rect: CGRect) {
        // Draws bars directly to context — no accessibility elements
        for point in dataPoints {
            // ... Core Graphics drawing code
        }
    }
}
```

## The Fix: UIAccessibilityElement Array

Override `isAccessibilityElement` and `accessibilityElements` on the container view. Each bar becomes a virtual `UIAccessibilityElement` with a label, value, and screen-coordinate frame.

```swift
class BarChartView: UIView {

    var dataPoints: [DataPoint] = []

    // Step 1: Container is NOT itself an element
    override var isAccessibilityElement: Bool {
        get { false }
        set { }
    }

    // Step 2: Provide virtual elements for each data point
    override var accessibilityElements: [Any]? {
        get {
            return dataPoints.enumerated().map { index, point in
                let element = UIAccessibilityElement(accessibilityContainer: self)

                // Human-readable label — identifies what this bar represents
                element.accessibilityLabel = point.label  // e.g. "January"

                // The data value for this bar
                element.accessibilityValue = "\(point.value) units"  // e.g. "142 units"

                // Accessibility hint (optional but helpful)
                element.accessibilityHint = "Bar \(index + 1) of \(dataPoints.count)"

                // Trait — staticText for read-only data; use .adjustable if interactive
                element.accessibilityTraits = .staticText

                // Step 3: Convert the bar's frame to screen coordinates
                element.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(
                    barFrame(for: point, at: index),
                    in: self
                )

                return element
            }
        }
        set { }
    }

    // Helper: compute the CGRect for a specific bar
    private func barFrame(for point: DataPoint, at index: Int) -> CGRect {
        let barWidth: CGFloat = bounds.width / CGFloat(dataPoints.count)
        let maxValue = dataPoints.map(\.value).max() ?? 1
        let barHeight = CGFloat(point.value) / CGFloat(maxValue) * bounds.height
        let x = CGFloat(index) * barWidth
        let y = bounds.height - barHeight
        return CGRect(x: x, y: y, width: barWidth, height: barHeight)
    }

    override func draw(_ rect: CGRect) {
        // ... existing Core Graphics drawing
    }
}
```

## Key Steps Explained

### Step 1: `isAccessibilityElement = false` on Container

The container view itself should not be an element — if it were, VoiceOver would focus the whole chart as one opaque blob. Setting this to `false` tells VoiceOver to look at `accessibilityElements` instead.

### Step 2: `accessibilityElements` Returns Virtual Elements

`UIAccessibilityElement` is a lightweight proxy that represents a region of the screen. It carries:
- `accessibilityLabel` — what the element is ("January")
- `accessibilityValue` — the current data ("142 units")
- `accessibilityFrame` — where on screen to focus the VoiceOver cursor
- `accessibilityTraits` — the role (`.staticText` for read-only; `.adjustable` for interactive)

### Step 3: `UIAccessibility.convertToScreenCoordinates(_:in:)`

The `accessibilityFrame` must be in **screen coordinates** (not view-local coordinates). `convertToScreenCoordinates` performs this conversion accounting for scroll offsets, transforms, and screen scale.

```swift
element.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(
    barFrame(for: point, at: index),
    in: self
)
```

## Invalidating Elements After Layout Changes

If the view re-draws (e.g., after data updates or rotation), the frames change. Notify VoiceOver:

```swift
override func layoutSubviews() {
    super.layoutSubviews()
    UIAccessibility.post(notification: .layoutChanged, argument: nil)
}
```

## Complete DataPoint Model Example

```swift
struct DataPoint {
    let label: String   // "January", "February", ...
    let value: Int      // 142, 89, ...
}
```

VoiceOver navigation: swipe right through each bar, hearing e.g.:
> "January. 142 units. Bar 1 of 12."
> "February. 89 units. Bar 2 of 12."

## SwiftUI Alternative

In SwiftUI, use `.accessibilityChildren` on a `Canvas` view instead of UIAccessibilityElement:

```swift
Canvas { context, size in
    // Custom drawing
}
.accessibilityLabel("Monthly sales chart")
.accessibilityChildren {
    ForEach(dataPoints) { point in
        Rectangle()
            .accessibilityLabel(point.label)
            .accessibilityValue("\(point.value) units")
    }
}
```
