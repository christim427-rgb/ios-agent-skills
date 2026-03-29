# Fixing VoiceOver Reading Order in a Comparison Table

## The Problem

Your comparison table has no accessibility grouping, so VoiceOver treats every `Text` element as a separate, independent focus target. With 3 columns and 5 rows, that is 15 individual swipes. Worse, depending on the layout engine's frame calculations, VoiceOver may not follow the visual left-to-right, top-to-bottom order you expect -- it can jump between columns because its default sort is based on the geometric center of each element, and narrow columns can produce unpredictable ordering.

## Why This Happens

VoiceOver determines reading order from the accessibility element tree. Without explicit grouping, each `Text` inside each `HStack` is an independent element. VoiceOver sorts these by screen position (top-left to bottom-right), but when elements in different rows have similar vertical positions or when row heights vary slightly, the sort becomes unreliable and elements from different rows can interleave.

## The Fix: Group Each Row

You have two strategies depending on the reading experience you want.

### Option 1: `.combine` -- Quick Fix, Comma-Separated Reading

Apply `.accessibilityElement(children: .combine)` to each `HStack`. VoiceOver merges all children into one element and joins their labels with pauses.

```swift
VStack {
    // Header row -- also mark as header for rotor navigation
    HStack {
        Text("Feature")
        Text("Basic")
        Text("Pro")
    }
    .accessibilityElement(children: .combine)
    .accessibilityAddTraits(.isHeader)

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

    // ... remaining rows follow the same pattern
}
```

**VoiceOver reads:**
- "Feature, Basic, Pro -- heading"
- "Storage, 5GB, 100GB"
- "Users, 1, Unlimited"

This works, but the comma-separated reading does not tell the user which value belongs to which plan.

### Option 2: `.ignore` + Custom Label -- Natural Sentence Reading (Recommended)

Use `.accessibilityElement(children: .ignore)` on each row and provide a custom `accessibilityLabel` that reads as a natural sentence, explicitly mapping values to column headers.

```swift
VStack {
    // Header row
    HStack {
        Text("Feature")
        Text("Basic")
        Text("Pro")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Comparison table: Feature, Basic plan, Pro plan")
    .accessibilityAddTraits(.isHeader)

    HStack {
        Text("Storage")
        Text("5GB")
        Text("100GB")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Storage: 5 gigabytes for Basic, 100 gigabytes for Pro")

    HStack {
        Text("Users")
        Text("1")
        Text("Unlimited")
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Users: 1 for Basic, unlimited for Pro")

    // ... remaining rows
}
```

**VoiceOver reads:**
- "Comparison table: Feature, Basic plan, Pro plan -- heading"
- "Storage: 5 gigabytes for Basic, 100 gigabytes for Pro"
- "Users: 1 for Basic, unlimited for Pro"

This is significantly better because:
1. The user immediately understands which value belongs to which plan.
2. Abbreviations are expanded ("GB" to "gigabytes") so VoiceOver pronounces them correctly instead of spelling them out.
3. Each row is a single swipe -- 5 swipes total instead of 15.
4. Reading order is guaranteed because each row is one atomic element.

### Option 3: Data-Driven Approach for Maintainability

If your table data comes from a model, generate the labels programmatically:

```swift
struct ComparisonRow: Identifiable {
    let id = UUID()
    let feature: String
    let basic: String
    let pro: String

    var accessibilityDescription: String {
        "\(feature): \(basic) for Basic, \(pro) for Pro"
    }
}

let rows = [
    ComparisonRow(feature: "Storage", basic: "5 GB", pro: "100 GB"),
    ComparisonRow(feature: "Users", basic: "1", pro: "Unlimited"),
    ComparisonRow(feature: "Support", basic: "Email", pro: "24/7 phone"),
    ComparisonRow(feature: "API access", basic: "None", pro: "Full"),
    ComparisonRow(feature: "Price", basic: "$9/month", pro: "$29/month"),
]

VStack(spacing: 12) {
    // Header
    HStack {
        Text("Feature")
            .frame(maxWidth: .infinity, alignment: .leading)
        Text("Basic")
            .frame(maxWidth: .infinity, alignment: .leading)
        Text("Pro")
            .frame(maxWidth: .infinity, alignment: .leading)
    }
    .font(.headline)
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Comparison table: Feature, Basic plan, Pro plan")
    .accessibilityAddTraits(.isHeader)

    ForEach(rows) { row in
        HStack {
            Text(row.feature)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text(row.basic)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text(row.pro)
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .font(.body)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(row.accessibilityDescription)
    }
}
```

## If Reading Order Is Still Wrong After Grouping

In rare cases where the row order itself is incorrect (for example, VoiceOver reads row 3 before row 2), use `.accessibilitySortPriority()` to enforce explicit ordering. Higher values are read first:

```swift
VStack {
    headerRow
        .accessibilitySortPriority(5)
    storageRow
        .accessibilitySortPriority(4)
    usersRow
        .accessibilitySortPriority(3)
    supportRow
        .accessibilitySortPriority(2)
    priceRow
        .accessibilitySortPriority(1)
}
```

You should only need this as a last resort -- grouping each row into a single element almost always fixes the ordering problem on its own.

## Additional Considerations

- **Dynamic Type:** Use `.font(.body)` and `.font(.headline)` (not `.system(size:)`) so the table scales with the user's text size preference.
- **Layout adaptation:** At large accessibility text sizes, the 3-column layout may overflow. Consider using `ViewThatFits` to switch to a vertical layout at accessibility sizes, or wrap each row in a `ScrollView(.horizontal)`.
- **Semantic colors:** Use `.foregroundStyle(.primary)` and `.foregroundStyle(.secondary)` rather than hardcoded colors so the table remains legible in dark mode and high-contrast mode.

## Summary

| Approach | Swipes | Reading quality | Effort |
|---|---|---|---|
| No grouping (current) | 15 | Poor -- jumps between columns | -- |
| `.combine` | 5 | OK -- comma-separated, no column context | Low |
| `.ignore` + custom label | 5 | Best -- natural sentences with column mapping | Medium |
| Data-driven + `.ignore` | 5 | Best -- auto-generated, maintainable | Medium |

The recommended fix is Option 2 or 3: `.accessibilityElement(children: .ignore)` with a custom `accessibilityLabel` on each row that maps values to their column headers in a natural sentence.
