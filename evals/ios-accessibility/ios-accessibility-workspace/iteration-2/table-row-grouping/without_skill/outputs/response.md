## Fixing VoiceOver Reading Order in a Comparison Table

### The Problem

VoiceOver follows the **view hierarchy order**, which for a grid or table built with nested `HStack`/`VStack` may be column-by-column rather than row-by-row. Users hear all values in column 1, then all values in column 2, making it impossible to compare a single row's data.

Example of wrong order with two columns:
> "Feature A" → "Feature B" → "Feature C" → "Yes" → "No" → "Yes"

Expected (row-by-row):
> "Feature A, Yes" → "Feature B, No" → "Feature C, Yes"

---

### Fix 1: Group Each Row as a Single Accessible Element

The most robust fix is to make each **row** a single focus stop with a combined label:

```swift
// SwiftUI
ForEach(features) { feature in
    HStack {
        Text(feature.name)
        Spacer()
        Text(feature.supported ? "Yes" : "No")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("\(feature.name): \(feature.supported ? "Supported" : "Not supported")")
}
```

VoiceOver now reads one element per row, in the correct order.

---

### Fix 2: Use `accessibilitySortPriority` to Reorder Focus

If you need cells to remain individually focusable, assign sort priorities so VoiceOver traverses row-by-row:

```swift
// Row 0, Column 0 gets highest priority for that row
Text(feature.name)
    .accessibilitySortPriority(Double(rowIndex * 10 + 1))
Text(feature.value)
    .accessibilitySortPriority(Double(rowIndex * 10))
```

Higher `accessibilitySortPriority` values are read first. Assign priorities that encode the row-then-column order.

---

### Fix 3: UIKit — `shouldGroupAccessibilityChildren`

In UIKit, set `shouldGroupAccessibilityChildren = true` on the row container:

```swift
rowView.shouldGroupAccessibilityChildren = true
```

This tells UIKit to treat all children of `rowView` as a group and traverse them together before moving to the next group.

---

### Fix 4: Restructure the View Hierarchy

If using a grid layout (e.g., `LazyVGrid`), restructure to a `List` of row views. A `List` whose cells represent rows naturally produces correct VoiceOver order because each cell is one accessible unit.

---

### Recommended Approach

For comparison tables, **Fix 1 (row grouping with explicit labels)** is best:
- Single swipe per row
- Full control over what is spoken
- No dependency on layout order tricks

Use a label format like:
```
"<Feature name>: <Plan A value>, <Plan B value>"
// e.g. "Offline access: Included in Pro, Not included in Free"
```
