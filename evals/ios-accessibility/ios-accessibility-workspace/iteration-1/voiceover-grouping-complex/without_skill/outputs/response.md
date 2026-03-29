# Making Canvas-Based Charts Accessible to VoiceOver

## The Problem

SwiftUI's `Canvas` view is a purely visual drawing surface. It renders pixels directly and produces no accessibility tree nodes, which means VoiceOver has absolutely nothing to announce. The ellipses you draw are invisible to assistive technology.

## Solution: Add an Accessibility Overlay

The standard approach is to layer invisible accessibility elements on top of (or alongside) the `Canvas` using `.accessibilityChildren` or an overlay with `AccessibilityElement` representations. Here are two approaches:

### Approach 1: Using `.accessibilityChildren` (Recommended)

Wrap the `Canvas` and provide accessibility children that correspond to each data point:

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
.accessibilityElement(children: .contain)
.accessibilityLabel("Chart")
.accessibilityChildren {
    ForEach(Array(dataPoints.enumerated()), id: \.offset) { index, point in
        Rectangle()
            .accessibilityLabel("Data point \(index + 1)")
            .accessibilityValue("X: \(point.x, specifier: "%.1f"), Y: \(point.y, specifier: "%.1f")")
    }
}
```

With `.accessibilityChildren`, VoiceOver treats the `Canvas` as a container with individual focusable children -- one per data point. The `Rectangle()` views inside the closure are never rendered; they exist solely to generate accessibility tree nodes.

### Approach 2: Using an Overlay with Explicit Accessibility Elements

If you need precise hit-testing or spatial positioning of the accessibility focus regions (so that VoiceOver highlights the correct area on screen), use an overlay with `GeometryReader`:

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
.accessibilityElement(children: .ignore)
.overlay {
    GeometryReader { geometry in
        ForEach(Array(dataPoints.enumerated()), id: \.offset) { index, point in
            let x = point.x * geometry.size.width
            let y = (1 - point.y) * geometry.size.height

            Color.clear
                .frame(width: 44, height: 44) // Minimum touch target size
                .position(x: x + 5, y: y + 5)
                .accessibilityElement()
                .accessibilityLabel("Data point \(index + 1)")
                .accessibilityValue("X: \(point.x, specifier: "%.1f"), Y: \(point.y, specifier: "%.1f")")
                .accessibilityAddTraits(.isButton) // If tappable
        }
    }
}
```

This approach gives VoiceOver spatially accurate focus rects that match the visual positions of the dots.

## Additional Considerations

### Group the Chart as a Container

Add a high-level label so users understand what they are navigating into:

```swift
.accessibilityElement(children: .contain)
.accessibilityLabel("Sales data chart, \(dataPoints.count) data points")
```

### Use Rotor Actions for Navigation

For charts with many data points, implement `accessibilityAdjustableAction` so users can swipe up/down to move between points without tabbing through every element:

```swift
@State private var selectedIndex = 0

// ...
.accessibilityElement()
.accessibilityLabel("Chart data point")
.accessibilityValue("Point \(selectedIndex + 1) of \(dataPoints.count): X \(dataPoints[selectedIndex].x, specifier: "%.1f"), Y \(dataPoints[selectedIndex].y, specifier: "%.1f")")
.accessibilityAdjustableAction { direction in
    switch direction {
    case .increment:
        selectedIndex = min(selectedIndex + 1, dataPoints.count - 1)
    case .decrement:
        selectedIndex = max(selectedIndex - 1, 0)
    @unknown default:
        break
    }
}
```

### Provide Meaningful Labels

Instead of raw coordinates, translate values into domain-specific language:

```swift
.accessibilityLabel("January")
.accessibilityValue("Revenue: $14,500")
```

### Consider Audio Graphs (iOS 15+)

For system-level sonification, conform your data to `AXChartDescriptor` by implementing the `AXChartDescriptorRepresentable` protocol. This lets VoiceOver play an audio representation of the chart:

```swift
struct ChartView: View {
    let dataPoints: [DataPoint]

    var body: some View {
        Canvas { context, size in
            // ... drawing code ...
        }
        .accessibilityChartDescriptor(self)
    }
}

extension ChartView: AXChartDescriptorRepresentable {
    func makeChartDescriptor() -> AXChartDescriptor {
        let xAxis = AXNumericDataAxisDescriptor(
            title: "Month",
            range: 0...Double(dataPoints.count - 1),
            gridlinePositions: []
        ) { value in
            "Month \(Int(value) + 1)"
        }

        let yAxis = AXNumericDataAxisDescriptor(
            title: "Value",
            range: 0...1,
            gridlinePositions: []
        ) { value in
            String(format: "%.1f", value)
        }

        let series = AXDataSeriesDescriptor(
            name: "Data",
            isContinuous: true,
            dataPoints: dataPoints.enumerated().map { index, point in
                AXDataPoint(x: Double(index), y: point.y)
            }
        )

        return AXChartDescriptor(
            title: "Data Chart",
            summary: "Shows \(dataPoints.count) data points",
            xAxis: xAxis,
            yAxis: yAxis,
            additionalAxes: [],
            series: [series]
        )
    }
}
```

## Summary

| Technique | Best For |
|---|---|
| `.accessibilityChildren` | Simple list of data points without spatial positioning needs |
| Overlay with positioned `Color.clear` | Spatially accurate VoiceOver focus rects |
| `accessibilityAdjustableAction` | Charts with many points where sequential swiping is tedious |
| `AXChartDescriptorRepresentable` | Audio graph sonification for full chart comprehension |

The key principle: since `Canvas` draws raw pixels with no view hierarchy, you must explicitly construct a parallel accessibility tree that represents your data in a meaningful way for VoiceOver users.
