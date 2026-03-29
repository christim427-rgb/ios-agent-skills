# Making Canvas Data Points Accessible to VoiceOver

## The Problem

`Canvas` is a pixel-drawing view -- it produces raw graphics with zero accessibility tree output. VoiceOver cannot see, navigate, or describe anything drawn inside a `Canvas` block. This is a **CRITICAL** accessibility issue (AI Failure Pattern F7: no accessibility on custom controls).

**WCAG:** 1.1.1 Non-text Content (Level A) | **HIG:** Accessibility > VoiceOver

## The Fix

Use `.accessibilityChildren` to provide a virtual accessibility tree that mirrors your drawn data points. This modifier lets you define child accessibility elements that VoiceOver can navigate, even though those elements are not visually rendered -- they exist purely for assistive technology.

```swift
Canvas { context, size in
    for point in dataPoints {
        let rect = CGRect(
            x: point.x * size.width,
            y: (1 - point.y) * size.height,
            width: 10,
            height: 10
        )
        context.fill(Path(ellipseIn: rect), with: .color(.blue))
    }
}
.accessibilityLabel("Data chart with \(dataPoints.count) points")
.accessibilityChildren {
    ForEach(dataPoints) { point in
        Rectangle()
            .accessibilityLabel(point.label)
            .accessibilityValue("x: \(point.x, format: .number), y: \(point.y, format: .number)")
    }
}
```

## Why This Works

- `.accessibilityLabel` on the `Canvas` itself gives VoiceOver a top-level description of what the chart is. Without it, VoiceOver either skips the entire view or announces nothing meaningful.
- `.accessibilityChildren` injects virtual child elements into the accessibility tree. Each `Rectangle()` inside the closure is never rendered on screen -- it only exists as an accessibility element. VoiceOver treats each one as a navigable item within the chart container.
- Each child gets its own `.accessibilityLabel` describing what the data point represents (e.g., "January sales") and `.accessibilityValue` for the numeric data.

## Full Example With Rich Labels

For a real chart, your data points likely have meaningful names and values. Here is a more complete pattern:

```swift
struct DataPoint: Identifiable {
    let id = UUID()
    let month: String
    let value: Double
}

struct AccessibleChartView: View {
    let dataPoints: [DataPoint]

    var body: some View {
        Canvas { context, size in
            let maxValue = dataPoints.map(\.value).max() ?? 1
            for (index, point) in dataPoints.enumerated() {
                let x = CGFloat(index) / CGFloat(dataPoints.count - 1) * size.width
                let y = (1 - point.value / maxValue) * size.height
                let rect = CGRect(x: x - 5, y: y - 5, width: 10, height: 10)
                context.fill(Path(ellipseIn: rect), with: .color(.blue))
            }
        }
        .accessibilityLabel("Sales chart, \(dataPoints.count) months")
        .accessibilityChildren {
            ForEach(dataPoints) { point in
                Rectangle()
                    .accessibilityLabel("\(point.month): \(point.value, format: .number) units")
            }
        }
    }
}
```

**VoiceOver reads (navigating through):**
- Container: "Sales chart, 12 months"
- Swiping right: "January: 150 units"
- Swiping right: "February: 230 units"
- Swiping right: "March: 180 units"
- ... and so on for each data point.

## Adding Custom Actions for Interactivity

If tapping a data point triggers an action (like showing a detail popover), add custom actions so VoiceOver users have the same capability:

```swift
.accessibilityChildren {
    ForEach(dataPoints) { point in
        Rectangle()
            .accessibilityLabel("\(point.month): \(point.value, format: .number) units")
            .accessibilityCustomActions([
                .init(named: "Show details") {
                    selectedPoint = point
                    return true
                }
            ])
    }
}
```

## Consider Swift Charts Instead

If you are building a new chart, strongly consider using the `Charts` framework instead of `Canvas`. Swift Charts provides built-in accessibility out of the box, including:

- Automatic data point labels
- Audio Graphs (VoiceOver users can "play" the chart as sound)
- Axis descriptions and chart summaries

```swift
import Charts

Chart(dataPoints) { point in
    PointMark(
        x: .value("Month", point.month),
        y: .value("Value", point.value)
    )
}
.accessibilityChartDescriptor(self) // For custom descriptions
```

If `Canvas` is required (custom drawing, performance with thousands of points, or a visual style Charts cannot produce), then `.accessibilityChildren` is the correct approach.

## Key Takeaways

1. `Canvas` produces zero accessibility output by default -- always pair it with `.accessibilityLabel` and `.accessibilityChildren`.
2. The views inside `.accessibilityChildren` are never rendered; they exist solely for the accessibility tree.
3. Each virtual child should have a descriptive `.accessibilityLabel` that conveys the meaning of the data point, not its visual appearance.
4. For interactive charts, use `.accessibilityCustomActions` on each child element.
5. Prefer Swift Charts for new chart implementations -- its built-in accessibility (including Audio Graphs) is significantly richer than what you can achieve manually.
