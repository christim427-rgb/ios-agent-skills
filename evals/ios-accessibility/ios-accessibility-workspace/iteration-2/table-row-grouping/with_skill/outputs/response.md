# Comparison Table VoiceOver Grouping and Reading Order

## The Problem

A comparison table without grouping forces VoiceOver to read elements in layout order across the entire table — often left-to-right, row-by-row. For a table like:

```
Feature    | Basic   | Pro
-----------+---------+---------
Storage    | 5 GB    | 100 GB
Users      | 1       | 10
Support    | Email   | Phone
```

VoiceOver might read: "Feature, Basic, Pro, Storage, 5 GB, 100 GB, Users, 1, 10, Support, Email, Phone" — which is correct layout order but completely strips the relational meaning. A user navigating fast has no idea whether "100 GB" refers to Storage or Users.

---

## Solution 1: Group Each Row with `.accessibilityElement(children: .ignore)` + Natural Label

Each row should be one VoiceOver element with a label that reads as a complete sentence:

```swift
struct ComparisonRow: View {
    let feature: String
    let basicValue: String
    let proValue: String

    var body: some View {
        HStack {
            Text(feature)
                .frame(maxWidth: .infinity, alignment: .leading)
            Text(basicValue)
                .frame(maxWidth: .infinity, alignment: .center)
            Text(proValue)
                .frame(maxWidth: .infinity, alignment: .center)
        }
        // Collapse the row into one element
        .accessibilityElement(children: .ignore)
        // Natural sentence that restores the relational context
        .accessibilityLabel("\(feature): Basic plan \(basicValue), Pro plan \(proValue)")
    }
}
```

**VoiceOver reads per row:** "Storage: Basic plan 5 GB, Pro plan 100 GB"

The sighted layout (columns) does not translate well to linear audio. The label reformats the data for listening.

---

## Solution 2: `shouldGroupAccessibilityChildren` (UIKit)

In UIKit, apply `shouldGroupAccessibilityChildren` to each row container to prevent VoiceOver from interleaving elements from adjacent rows:

```swift
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "ComparisonCell", for: indexPath)
    let row = comparisonData[indexPath.row]

    // Ensure children are read as a group, not interleaved
    cell.contentView.shouldGroupAccessibilityChildren = true

    // Provide a natural label for the entire row
    cell.isAccessibilityElement = true
    cell.accessibilityLabel = "\(row.feature): Basic plan \(row.basicValue), Pro plan \(row.proValue)"

    return cell
}
```

---

## Solution 3: `accessibilitySortPriority` for Fine-Grained Order Control

When elements cannot be structurally regrouped, use `accessibilitySortPriority` to establish explicit reading order. Higher numbers are read first.

```swift
HStack {
    Text("Storage")
        .accessibilitySortPriority(3)    // Read first
    Text("5 GB")
        .accessibilitySortPriority(2)    // Read second
    Text("100 GB")
        .accessibilitySortPriority(1)    // Read third
}
```

**Note:** `.accessibilitySortPriority` works within a container; it does not override grouping across containers. Prefer structural grouping (`.accessibilityElement(children:)`) over sort priority when possible.

---

## UIKit: Override `accessibilityElements` for Explicit Row Order

When the table uses custom layout that breaks normal VoiceOver traversal order:

```swift
class ComparisonCell: UITableViewCell {
    override var accessibilityElements: [Any]? {
        get {
            // Explicitly define reading order for this row
            return [featureLabel, basicValueLabel, proValueLabel]
        }
        set { }
    }
}
```

**Warning:** Setting `accessibilityElements` completely replaces the default ordering. You take responsibility for every element in the container. Any element not included becomes unreachable via VoiceOver.

---

## Header Row

Don't forget the header row — mark column headers with the `.isHeader` trait:

```swift
HStack {
    Text("Feature")
        .accessibilityAddTraits(.isHeader)
    Text("Basic")
        .accessibilityAddTraits(.isHeader)
    Text("Pro")
        .accessibilityAddTraits(.isHeader)
}
```

Or group the header row and provide a label:

```swift
HStack { /* header content */ }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel("Plan comparison table: Feature, Basic plan, Pro plan")
    .accessibilityAddTraits(.isHeader)
```

---

## Complete SwiftUI Table

```swift
struct ComparisonTableView: View {
    let rows: [(feature: String, basic: String, pro: String)]

    var body: some View {
        VStack(spacing: 0) {
            // Header row
            HStack {
                Text("Feature").frame(maxWidth: .infinity, alignment: .leading)
                Text("Basic").frame(maxWidth: .infinity, alignment: .center)
                Text("Pro").frame(maxWidth: .infinity, alignment: .center)
            }
            .padding()
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("Comparison table: Feature, Basic plan, Pro plan")
            .accessibilityAddTraits(.isHeader)

            Divider()

            // Data rows
            ForEach(rows, id: \.feature) { row in
                HStack {
                    Text(row.feature).frame(maxWidth: .infinity, alignment: .leading)
                    Text(row.basic).frame(maxWidth: .infinity, alignment: .center)
                    Text(row.pro).frame(maxWidth: .infinity, alignment: .center)
                }
                .padding()
                .accessibilityElement(children: .ignore)
                .accessibilityLabel("\(row.feature): Basic \(row.basic), Pro \(row.pro)")

                Divider()
            }
        }
    }
}
```

**VoiceOver reads:**
- "Comparison table: Feature, Basic plan, Pro plan, Heading"
- "Storage: Basic 5 GB, Pro 100 GB"
- "Users: Basic 1, Pro 10"
- "Support: Basic Email, Pro Phone"
