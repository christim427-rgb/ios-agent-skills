# Making a Canvas-Based Chart Accessible to VoiceOver

## The Problem

SwiftUI's `Canvas` API draws directly to a graphics context. It produces no view hierarchy that VoiceOver can traverse — the entire canvas is a single opaque drawing. Without explicit accessibility work, users with VoiceOver hear only silence (or nothing at all) when focusing on a chart.

---

## Solution: `accessibilityChildren` for Virtual Elements

SwiftUI provides `.accessibilityChildren { }` specifically for this use case. It lets you declare a set of virtual child elements that exist **only in the accessibility tree** — not in the visual hierarchy. VoiceOver navigates these virtual elements as if they were real views.

```swift
struct LineChartView: View {
    let dataPoints: [(label: String, value: Double)]

    var body: some View {
        Canvas { context, size in
            // Draw the chart visually
            drawChart(context: context, size: size, data: dataPoints)
        }
        // Provide a summary label for the entire canvas
        .accessibilityLabel("Monthly revenue chart")
        // Provide virtual child elements — one per data point
        .accessibilityChildren {
            ForEach(dataPoints, id: \.label) { point in
                // Each virtual element is a Text view (never rendered visually)
                Text(point.label)
                    .accessibilityLabel("\(point.label): \(formattedValue(point.value))")
            }
        }
    }

    private func formattedValue(_ value: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .currency
        return formatter.string(from: NSNumber(value: value)) ?? "\(value)"
    }

    private func drawChart(context: GraphicsContext, size: CGSize, data: [(label: String, value: Double)]) {
        // ... drawing code
    }
}
```

**VoiceOver behavior:**
- Focus on canvas: "Monthly revenue chart"
- Swipe into children: "January: $12,400", "February: $15,800", ...

---

## UIKit Equivalent: `accessibilityElements` with `UIAccessibilityElement`

In UIKit, custom drawing views expose virtual elements by overriding `accessibilityElements`:

```swift
class BarChartView: UIView {
    var dataPoints: [(label: String, value: Double)] = []

    // The chart view itself is NOT an accessibility element
    override var isAccessibilityElement: Bool {
        get { false }
        set { }
    }

    // Virtual elements for each bar
    override var accessibilityElements: [Any]? {
        get {
            return dataPoints.enumerated().map { index, point in
                let element = UIAccessibilityElement(accessibilityContainer: self)
                // Each virtual element gets its own label
                element.accessibilityLabel = "\(point.label)"
                element.accessibilityValue = formattedValue(point.value)
                element.accessibilityTraits = .staticText
                // Position the virtual element over the corresponding bar
                element.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(
                    frameForBar(at: index),
                    in: self
                )
                return element
            }
        }
        set { }
    }

    private func frameForBar(at index: Int) -> CGRect {
        // Calculate the frame of bar at this index
        let barWidth = bounds.width / CGFloat(dataPoints.count)
        let x = barWidth * CGFloat(index)
        return CGRect(x: x, y: 0, width: barWidth, height: bounds.height)
    }

    private func formattedValue(_ value: Double) -> String {
        "\(Int(value)) units"
    }
}
```

---

## Adding Chart Summary as a Heading

A good pattern is to pair the canvas with a visible (or accessibility-only) summary that gives context before users explore individual data points:

```swift
VStack(alignment: .leading) {
    // Chart title — marked as heading for rotor navigation
    Text("Monthly Revenue")
        .font(.headline)
        .accessibilityAddTraits(.isHeader)

    // Optional summary for quick context
    Text("Total: $128,400 — up 14% from last period")
        .font(.subheadline)
        .foregroundStyle(.secondary)

    // The canvas with virtual data points
    Canvas { context, size in
        drawChart(context: context, size: size, data: dataPoints)
    }
    .frame(height: 200)
    .accessibilityLabel("Monthly revenue chart, 12 data points")
    .accessibilityChildren {
        ForEach(dataPoints, id: \.label) { point in
            Text(point.label)
                .accessibilityLabel("\(point.label): \(formattedValue(point.value))")
        }
    }
}
```

---

## Accessibility Checklist for Canvas Charts

- [x] `.accessibilityLabel` on the `Canvas` describes the chart type and context
- [x] `.accessibilityChildren` provides one virtual element per meaningful data point
- [x] Each virtual element's label includes both the axis label and the value
- [x] Chart title is present and marked with `.isHeader` for rotor navigation
- [x] Summary text (total, trend) is available for quick overview
- [x] UIKit: `isAccessibilityElement = false` on the chart view itself; `accessibilityElements` returns virtual elements with `accessibilityFrame` values
- [x] Consider `.accessibilityElement(children: .contain)` on the parent to keep summary and chart grouped

---

## `.accessibilityRepresentation` — Alternative for Simple Cases

For simpler charts, use `.accessibilityRepresentation` to substitute the entire Canvas with an accessible standard control:

```swift
Canvas { context, size in
    drawPieChart(context: context, size: size, data: segments)
}
.accessibilityRepresentation {
    // Replace the canvas with a list of text labels for VoiceOver
    VStack(alignment: .leading) {
        ForEach(segments, id: \.label) { segment in
            Text("\(segment.label): \(segment.percentage)%")
        }
    }
}
```

This is the simplest approach when you don't need VoiceOver to navigate within the chart — VoiceOver users see the accessible representation, sighted users see the canvas.
