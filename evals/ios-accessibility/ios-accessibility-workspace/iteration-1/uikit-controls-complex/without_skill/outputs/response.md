# Making a Custom UIKit Graph Accessible with VoiceOver

Custom views that use `drawRect` (or `draw(_:)`) render purely as pixels — UIKit's accessibility system has no knowledge of the shapes, bars, or data points inside them. You must manually build an accessibility representation on top of the visual drawing. There are two main approaches: **UIAccessibilityElement objects** and **accessibilityElements on the view itself**.

---

## Approach 1: UIAccessibilityElement (Recommended for Data Points)

Create one `UIAccessibilityElement` per data point and add them to the graph view. VoiceOver will iterate through them in order.

```swift
import UIKit

struct DataPoint {
    let label: String
    let value: Double
    let barRect: CGRect   // the frame of the bar/point in the view's coordinate space
}

class GraphView: UIView {
    var dataPoints: [DataPoint] = [] {
        didSet { buildAccessibilityElements() }
    }

    private var _accessibilityElements: [UIAccessibilityElement] = []

    // MARK: - Drawing
    override func draw(_ rect: CGRect) {
        // Your existing custom drawing code…
    }

    // MARK: - Accessibility

    /// Rebuild accessibility elements whenever data changes or layout changes.
    private func buildAccessibilityElements() {
        _accessibilityElements = dataPoints.map { point in
            let element = UIAccessibilityElement(accessibilityContainer: self)

            // What VoiceOver announces when this element is focused.
            element.accessibilityLabel = point.label
            element.accessibilityValue = String(format: "%.1f", point.value)

            // Optional: tell VoiceOver this is a static data item.
            element.accessibilityTraits = .staticText

            // The tappable / focusable rectangle in *screen* coordinates.
            // UIAccessibilityElement.accessibilityFrame is in screen coords,
            // so convert from the view's local coordinate space.
            element.accessibilityFrameInContainerSpace = point.barRect

            return element
        }
    }

    // Rebuild after layout so frames are up to date.
    override func layoutSubviews() {
        super.layoutSubviews()
        buildAccessibilityElements()
    }

    // MARK: - UIAccessibilityContainer protocol

    override var accessibilityElementCount: Int {
        return _accessibilityElements.count
    }

    override func accessibilityElement(at index: Int) -> Any? {
        return _accessibilityElements[index]
    }

    override func index(ofAccessibilityElement element: Any) -> Int {
        guard let el = element as? UIAccessibilityElement else { return NSNotFound }
        return _accessibilityElements.firstIndex(of: el) ?? NSNotFound
    }

    // Mark the container view itself as NOT an accessibility element so
    // VoiceOver goes straight to the children.
    override var isAccessibilityElement: Bool {
        get { return false }
        set { }
    }
}
```

### Key Points

| Property | Purpose |
|---|---|
| `accessibilityLabel` | The name VoiceOver reads (e.g. "January") |
| `accessibilityValue` | The current value (e.g. "42.0") |
| `accessibilityHint` | Optional extra context (e.g. "Double-tap to see details") |
| `accessibilityTraits` | Role/state (.staticText, .button, .selected, etc.) |
| `accessibilityFrameInContainerSpace` | Rect in the *container view's* coordinate space — iOS converts it to screen coordinates automatically |

---

## Approach 2: accessibilityElements Array (Simpler Alternative)

If all your elements live in the same view, you can assign an array directly:

```swift
override func layoutSubviews() {
    super.layoutSubviews()

    accessibilityElements = dataPoints.map { point in
        let el = UIAccessibilityElement(accessibilityContainer: self)
        el.accessibilityLabel = point.label
        el.accessibilityValue = "\(point.value)"
        el.accessibilityFrameInContainerSpace = point.barRect
        return el
    }
}
```

Setting `accessibilityElements` automatically makes `isAccessibilityElement` return `false` for the container, so VoiceOver skips it and navigates directly to the children.

---

## Approach 3: Invisible Overlay Subviews

If calculating `barRect` is complex, another option is to add transparent `UIView` subviews on top of the drawn content and set accessibility properties on those views directly:

```swift
private func addAccessibilityOverlays() {
    // Remove old overlays
    subviews.filter { $0.tag == 999 }.forEach { $0.removeFromSuperview() }

    for point in dataPoints {
        let overlay = UIView(frame: point.barRect)
        overlay.tag = 999
        overlay.isAccessibilityElement = true
        overlay.accessibilityLabel = point.label
        overlay.accessibilityValue = "\(point.value)"
        overlay.accessibilityTraits = .staticText
        overlay.backgroundColor = .clear
        // Prevent the overlay from intercepting touches if needed:
        overlay.isUserInteractionEnabled = false
        addSubview(overlay)
    }
}
```

This avoids implementing the UIAccessibilityContainer protocol but adds invisible views to the hierarchy.

---

## Providing a Summary for the Whole Graph

It is good practice to give the graph itself a meaningful label so users understand what they are navigating before entering it:

```swift
override func awakeFromNib() {
    super.awakeFromNib()
    accessibilityLabel = "Monthly Sales Bar Chart"
}
```

Or set it in the initializer / storyboard's Identity Inspector > Accessibility section.

---

## Posting Notifications When Data Updates

If the graph data updates dynamically, notify VoiceOver so it re-reads the content:

```swift
func updateData(_ newPoints: [DataPoint]) {
    dataPoints = newPoints
    setNeedsDisplay()

    // Announce the update to VoiceOver users.
    UIAccessibility.post(
        notification: .screenChanged,
        argument: "Graph updated with new data"
    )
}
```

Use `.layoutChanged` for partial updates and `.screenChanged` for full refreshes.

---

## Checklist

- [ ] `isAccessibilityElement = false` on the container `GraphView`
- [ ] One `UIAccessibilityElement` per data point with a descriptive `accessibilityLabel` and `accessibilityValue`
- [ ] `accessibilityFrameInContainerSpace` set to the correct bar/point rectangle
- [ ] Rebuild accessibility elements in `layoutSubviews()` (frames change on rotation)
- [ ] Post `.layoutChanged` or `.screenChanged` when data updates at runtime
- [ ] Test with VoiceOver enabled: swipe right to move between data points and confirm labels/values are read correctly
- [ ] Consider adding an `accessibilityHint` if the data point is interactive (tappable)
