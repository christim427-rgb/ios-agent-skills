## Making Canvas-Based Chart Data Accessible to VoiceOver

### The Problem

`Canvas` (SwiftUI) and `CALayer`/`CGContext` drawing (UIKit) produce purely visual output. VoiceOver has no knowledge of what is drawn — there are no accessibility elements in the view hierarchy corresponding to data points.

---

### Solution 1: Overlay Invisible Accessibility Elements (Recommended)

Place transparent, zero-opacity views — or use `accessibilityChildren` — positioned over each data point. These carry the accessible label without affecting the visual rendering.

#### SwiftUI with `accessibilityChildren`

```swift
Canvas { context, size in
    // draw chart here
    for point in dataPoints {
        let position = chartPosition(for: point, in: size)
        context.fill(Path(ellipseIn: CGRect(x: position.x - 4, y: position.y - 4, width: 8, height: 8)), with: .color(.blue))
    }
}
.accessibilityLabel("Sales chart")
.accessibilityChildren {
    ForEach(dataPoints) { point in
        Color.clear
            .accessibilityLabel("\(point.label): \(point.value)")
            .accessibilityAddTraits(.isStaticText)
    }
}
```

`accessibilityChildren` injects elements into the accessibility tree without rendering them. VoiceOver can swipe between data points.

#### SwiftUI — Overlay Approach

```swift
ZStack {
    Canvas { context, size in
        // draw chart
    }
    // Invisible tappable overlay elements
    ForEach(Array(dataPoints.enumerated()), id: \.offset) { index, point in
        Color.clear
            .frame(width: 44, height: 44)
            .position(chartPosition(for: point, in: geometry.size))
            .accessibilityLabel("\(point.label): \(point.value)")
            .accessibilityAddTraits(.isStaticText)
    }
}
```

---

### Solution 2: UIKit — Custom Accessibility Elements

Override `accessibilityElements` on the drawing view to return virtual `UIAccessibilityElement` objects:

```swift
class ChartView: UIView {
    var dataPoints: [DataPoint] = []

    override var accessibilityElements: [Any]? {
        get {
            dataPoints.map { point in
                let element = UIAccessibilityElement(accessibilityContainer: self)
                element.accessibilityLabel = "\(point.label): \(point.value)"
                element.accessibilityFrameInContainerSpace = frameInView(for: point)
                element.accessibilityTraits = .staticText
                return element
            }
        }
        set { }
    }
}
```

`accessibilityFrameInContainerSpace` maps to the actual visual position so VoiceOver's focus ring appears in the right place.

---

### Solution 3: Provide a Data Table Alternative

For complex charts, supplement the visual with a hidden (but accessible) data table that VoiceOver users can read:

```swift
VStack {
    Canvas { /* chart */ }
        .accessibilityHidden(true)   // hide canvas from VoiceOver

    // Accessible data table — visually hidden but in the a11y tree
    VStack {
        ForEach(dataPoints) { point in
            HStack {
                Text(point.label)
                Text("\(point.value)")
            }
        }
    }
    .accessibilityLabel("Chart data")
}
```

This pattern is common in web accessibility (visually-hidden tables) and works equally well on iOS.

---

### Best Practices

- Announce the chart type and overall summary as the canvas's own label: `"Line chart, sales January through June"`.
- For large datasets, expose summary statistics (min, max, average) rather than every single point.
- Add a rotor action or custom action so users can navigate by data series if there are multiple lines.
- Always test with VoiceOver enabled to verify focus order and frame placement.
