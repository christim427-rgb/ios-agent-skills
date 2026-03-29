# Fixing VoiceOver Access to Custom-Drawn GraphView (UIKit)

## Issue Diagnosis

**Severity: 🔴 CRITICAL — F7: No accessibility on custom controls**

Your `GraphView` uses `drawRect` (custom Core Graphics drawing), which produces a flat bitmap from UIKit's perspective. VoiceOver sees a single opaque view with no semantic structure, so it either skips the entire graph or announces it as an unlabeled image. None of the individual data points are reachable.

**VoiceOver Impact:** User hears nothing, or a generic "GraphView" with no data. They cannot navigate between bars/lines, hear values, or understand trends.

**WCAG:** 1.1.1 Non-text Content (Level A), 1.3.1 Info and Relationships (Level A)

---

## Root Cause

`draw(_ rect:)` renders pixels — UIKit has no knowledge of the logical objects inside. Unlike subviews, drawn elements have no `isAccessibilityElement`, no `accessibilityLabel`, and no `accessibilityFrame`. VoiceOver cannot discover what doesn't exist in the view hierarchy.

---

## Fix: UIAccessibilityElement with accessibilityElements

The correct UIKit pattern is to:

1. Mark the container view as **not** an accessibility element itself (`isAccessibilityElement = false`)
2. Override `accessibilityElements` to return one `UIAccessibilityElement` per data point
3. Set `accessibilityFrame` using `UIAccessibility.convertToScreenCoordinates(_:in:)` to map each bar/point's CGRect to screen coordinates
4. Invalidate the cache whenever `dataPoints` changes

```swift
// ❌ Current — VoiceOver sees nothing inside the graph
class GraphView: UIView {
    var dataPoints: [DataPoint] = []

    override func draw(_ rect: CGRect) {
        // Custom drawing of bars/lines...
    }
}
```

```swift
// ✅ Corrected — each data point becomes an independent VoiceOver element

struct DataPoint {
    let label: String   // e.g. "January", "Week 3"
    let value: Double   // e.g. 42.5
    let frame: CGRect   // the CGRect of this bar/point in the view's coordinate space
    let unit: String    // e.g. "units", "%", "km"
}

class GraphView: UIView {

    var dataPoints: [DataPoint] = [] {
        didSet {
            // Invalidate cached elements whenever data changes
            _accessibilityElements = nil
            UIAccessibility.post(notification: .layoutChanged, argument: nil)
        }
    }

    // MARK: - Custom drawing (unchanged)

    override func draw(_ rect: CGRect) {
        // Your existing Core Graphics drawing code here...
    }

    // MARK: - Accessibility

    // The view itself is a container, not a focusable element
    override var isAccessibilityElement: Bool {
        get { false }
        set { }
    }

    // Optional: tells VoiceOver this is a data table or list
    override var accessibilityContainerType: UIAccessibilityContainerType {
        get { .list }
        set { }
    }

    // Cache for performance — invalidated on data change or layout change
    private var _accessibilityElements: [UIAccessibilityElement]?

    override var accessibilityElements: [Any]? {
        get {
            if let cached = _accessibilityElements { return cached }

            let elements = dataPoints.enumerated().map { index, point -> UIAccessibilityElement in
                let element = UIAccessibilityElement(accessibilityContainer: self)

                // Label: the name/category of this data point
                element.accessibilityLabel = point.label

                // Value: the numeric reading with units
                element.accessibilityValue = "\(point.value) \(point.unit)"

                // Hint: optional context for the user
                element.accessibilityHint = "Data point \(index + 1) of \(dataPoints.count)"

                // Trait: static text (non-interactive); use .button if tappable
                element.accessibilityTraits = .staticText

                // Frame: MUST be converted from view coordinates to screen coordinates
                element.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(
                    point.frame, in: self
                )

                return element
            }

            _accessibilityElements = elements
            return elements
        }
        set { }
    }

    // Invalidate cached frames on layout changes (rotation, size class changes)
    override func layoutSubviews() {
        super.layoutSubviews()
        _accessibilityElements = nil
    }
}
```

**VoiceOver reads (per element):**
> "January" — "42 units" — "Data point 1 of 12"

VoiceOver users can swipe right/left to move between each bar or data point in order.

---

## If Data Points Are Also Tappable

If users can tap a bar to see a detail view, change the trait to `.button` and post a layout notification after selection:

```swift
element.accessibilityTraits = .button
element.accessibilityHint = "Double tap to view details"

// After handling a tap on this element:
UIAccessibility.post(notification: .screenChanged, argument: detailView)
```

---

## If You Want Summary-Level Access + Detail Navigation

Expose a summary element first, then individual points — useful for charts where a high-level reading ("Revenue chart, 12 months, range $40K to $95K") is meaningful before drilling into each bar:

```swift
override var accessibilityElements: [Any]? {
    get {
        var elements: [UIAccessibilityElement] = []

        // 1. Summary element covering the entire graph
        let summary = UIAccessibilityElement(accessibilityContainer: self)
        summary.accessibilityLabel = "Revenue chart"
        summary.accessibilityValue = "12 months, \(minValue) to \(maxValue)"
        summary.accessibilityTraits = .staticText
        summary.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(bounds, in: self)
        elements.append(summary)

        // 2. Individual data points
        let points = dataPoints.enumerated().map { index, point -> UIAccessibilityElement in
            let el = UIAccessibilityElement(accessibilityContainer: self)
            el.accessibilityLabel = point.label
            el.accessibilityValue = "\(point.value) \(point.unit)"
            el.accessibilityTraits = .staticText
            el.accessibilityFrame = UIAccessibility.convertToScreenCoordinates(point.frame, in: self)
            return el
        }
        elements.append(contentsOf: points)
        return elements
    }
    set { }
}
```

---

## Adding a VoiceOver Rotor for Graph Navigation (Optional, Recommended)

For graphs with many data points, add a custom rotor so power users can jump by data point category or skip to min/max values:

```swift
// In viewDidLoad or the view's init:
func configureAccessibilityRotor() -> UIAccessibilityCustomRotor {
    UIAccessibilityCustomRotor(name: "Data Points") { [weak self] predicate -> UIAccessibilityCustomRotorItemResult? in
        guard let self = self,
              let elements = self.accessibilityElements as? [UIAccessibilityElement],
              !elements.isEmpty else { return nil }

        let currentElement = predicate.currentItem.targetElement as? UIAccessibilityElement
        let currentIndex = elements.firstIndex { $0 === currentElement } ?? -1

        let nextIndex: Int
        if predicate.searchDirection == .next {
            nextIndex = min(currentIndex + 1, elements.count - 1)
        } else {
            nextIndex = max(currentIndex - 1, 0)
        }

        return UIAccessibilityCustomRotorItemResult(targetElement: elements[nextIndex], targetRange: nil)
    }
}

// Assign to the view:
accessibilityCustomRotors = [configureAccessibilityRotor()]
```

---

## Confidence Checklist

- [x] `isAccessibilityElement = false` on the container view
- [x] `accessibilityElements` returns one element per data point
- [x] Each element has `accessibilityLabel` (name) and `accessibilityValue` (numeric value + unit)
- [x] `accessibilityFrame` uses `UIAccessibility.convertToScreenCoordinates(_:in:)` — not raw CGRect
- [x] Cache invalidated on `dataPoints` change and `layoutSubviews`
- [x] `UIAccessibility.post(notification: .layoutChanged, ...)` called when data updates
- [x] Traits are set correctly (`.staticText` for display-only, `.button` if tappable)
- [x] No `accessibilityTraits = .selected` assignment pattern (uses `.insert`/`.remove` for state changes)
- [x] `accessibilityContainerType = .list` provides semantic structure hint to VoiceOver

---

## Key Principle

`UIAccessibilityElement` is the UIKit escape hatch for any view whose visual content is not composed of subviews. Whenever you use `draw(_:)`, Core Animation layers, Metal, or SpriteKit, you are responsible for constructing the accessibility tree manually. The `accessibilityElements` array IS the accessibility tree for that container — VoiceOver uses it exclusively and ignores the drawn pixels entirely.
