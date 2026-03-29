# Fixing VoiceOver Reading Order in a SwiftUI Comparison Table

## The Problem

With your current layout, VoiceOver navigates the accessibility tree in the order elements appear in the view hierarchy. Since each `HStack` is independent, VoiceOver may jump between columns unpredictably, especially when the user swipes to move between elements. The default behavior reads each `Text` as a separate, ungrouped element, producing a sequence like: "Feature", "Basic", "Pro", "Storage", "5GB", "100GB"... which reads column-by-column within each row but gives no context about which row or column a value belongs to.

The real usability problem is that a screenreader user hearing "5GB" has no idea whether that belongs to "Basic" or "Pro" without memorizing column positions.

## Solution 1: Combine Each Row into a Single Accessible Element

The most effective fix is to make each row a single accessibility element with a meaningful label that provides full context:

```swift
VStack {
    // Header row
    HStack {
        Text("Feature")
        Text("Basic")
        Text("Pro")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Feature comparison: Basic and Pro plans")

    // Data rows
    HStack {
        Text("Storage")
        Text("5GB")
        Text("100GB")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Storage: Basic 5GB, Pro 100GB")

    HStack {
        Text("Users")
        Text("1")
        Text("Unlimited")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Users: Basic 1, Pro Unlimited")
}
```

**Why this works:** `.accessibilityElement(children: .ignore)` collapses the entire `HStack` into one focusable element. VoiceOver reads the custom `.accessibilityLabel` which gives full row context in a single swipe. The user hears "Storage: Basic 5GB, Pro 100GB" -- immediately clear and unambiguous.

## Solution 2: Use `.accessibilityElement(children: .combine)` for Automatic Labels

If you want to avoid writing custom labels for every row, you can combine children automatically:

```swift
VStack {
    HStack {
        Text("Feature")
        Text("Basic")
        Text("Pro")
    }
    .accessibilityElement(children: .combine)

    HStack {
        Text("Storage")
        Text("5GB")
        Text("100GB")
    }
    .accessibilityElement(children: .combine)

    HStack {
        Text("Users")
        Text("1")
        Text("Unlimited")
    }
    .accessibilityElement(children: .combine)
}
```

**How it differs:** `.combine` merges all child labels into one string (e.g., "Storage, 5GB, 100GB"). This is simpler but less informative since VoiceOver won't announce which column each value belongs to. It does solve the navigation order problem though -- each row becomes one stop.

## Solution 3: Data-Driven Approach with Dynamic Labels (Recommended for Larger Tables)

For tables with more rows, build labels programmatically:

```swift
struct PlanFeature {
    let name: String
    let basic: String
    let pro: String
}

let features = [
    PlanFeature(name: "Storage", basic: "5GB", pro: "100GB"),
    PlanFeature(name: "Users", basic: "1", pro: "Unlimited"),
    PlanFeature(name: "Support", basic: "Email", pro: "24/7 Phone"),
]

VStack {
    // Header
    HStack {
        Text("Feature")
        Text("Basic")
        Text("Pro")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Feature comparison: Basic and Pro plans")

    ForEach(features, id: \.name) { feature in
        HStack {
            Text(feature.name)
            Text(feature.basic)
            Text(feature.pro)
        }
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(feature.name): Basic \(feature.basic), Pro \(feature.pro)")
    }
}
```

## Additional Improvements

### Add Traits for the Header Row

Mark the header row so VoiceOver conveys its role:

```swift
HStack {
    Text("Feature")
    Text("Basic")
    Text("Pro")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("Feature comparison: Basic and Pro plans")
.accessibilityAddTraits(.isHeader)
```

### Consider Using `.accessibilitySortPriority` If Order Still Drifts

If for some reason you need to keep individual elements focusable (e.g., each cell is independently tappable), you can enforce reading order explicitly:

```swift
HStack {
    Text("Storage").accessibilitySortPriority(3)
    Text("5GB").accessibilitySortPriority(2)
    Text("100GB").accessibilitySortPriority(1)
}
```

Higher values are read first. This ensures left-to-right order within a row. However, grouping rows (Solution 1) is almost always the better approach for comparison tables.

## Summary

| Approach | Pros | Cons |
|----------|------|------|
| `.ignore` + custom label | Best UX, full context per row | Requires writing labels |
| `.combine` | Simple, no custom labels | Less informative (no column context) |
| Data-driven + custom label | Scales well, labels auto-generated | Requires data model refactor |
| `.accessibilitySortPriority` | Keeps cells individually focusable | More swipes, less context per element |

**Recommendation:** Use Solution 1 or Solution 3. Collapsing each row into a single element with a descriptive label ("Storage: Basic 5GB, Pro 100GB") gives VoiceOver users the fastest, most comprehensible experience for a comparison table.
