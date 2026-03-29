# Making VoiceOver Announce Section Headings + Rotor Navigation

## The `.isHeader` Trait

To make VoiceOver announce a view as a section heading, add the `.isHeader` accessibility trait. VoiceOver appends "Heading" after the label, and — critically — the element becomes navigable via the VoiceOver Rotor's **Headings** category.

### SwiftUI

```swift
// ❌ Plain text — no heading announcement, no rotor navigation
Text("Recent Activity")
    .font(.title2)

// ✅ Heading — VoiceOver says "Recent Activity, Heading"
Text("Recent Activity")
    .font(.title2)
    .accessibilityAddTraits(.isHeader)
```

**VoiceOver reads:** "Recent Activity, Heading"

### UIKit

```swift
// UIKit — set on the label directly
sectionHeaderLabel.accessibilityTraits = .header
// or combined with other traits:
sectionHeaderLabel.accessibilityTraits = [.header, .staticText]
```

---

## Rotor Heading Navigation

The VoiceOver Rotor is a virtual dial that lets users quickly jump between elements of the same type. When elements have the `.isHeader` trait, the **Headings** rotor category becomes available.

### How Users Access Headings via the Rotor

1. Rotate two fingers on the screen (like turning a dial) to open the Rotor
2. Rotate to the **Headings** option
3. Swipe up or down to jump directly to the previous or next heading

This is the equivalent of pressing H in a browser with a screen reader — it lets users skim a long screen by jumping from section to section without reading every element in between.

---

## Custom Rotor for Finer Control (SwiftUI)

For more advanced navigation, create a custom rotor that filters to only specific elements:

```swift
struct ContentView: View {
    @Namespace private var rotorNamespace

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                ForEach(sections) { section in
                    // Mark each heading
                    Text(section.title)
                        .font(.title2)
                        .bold()
                        .accessibilityAddTraits(.isHeader)
                        .accessibilityRotorEntry(id: section.id, in: rotorNamespace)

                    ForEach(section.items) { item in
                        ItemRow(item: item)
                    }
                }
            }
        }
        // Custom rotor that surfaces only section headings
        .accessibilityRotor("Sections") {
            ForEach(sections) { section in
                AccessibilityRotorEntry(section.title, section.id, in: rotorNamespace)
            }
        }
    }
}
```

### UIKit Custom Rotor

```swift
let headingsRotor = UIAccessibilityCustomRotor(name: "Sections") { predicate in
    let direction = predicate.searchDirection
    // Find the next/previous heading element based on direction
    let headings = self.view.subviews.filter { $0.accessibilityTraits.contains(.header) }
    // Return the next/previous heading
    guard let current = predicate.currentItem.targetElement as? UIView,
          let currentIndex = headings.firstIndex(of: current) else {
        return UIAccessibilityCustomRotorItemResult(targetElement: headings.first, targetRange: nil)
    }
    let nextIndex = direction == .next ? currentIndex + 1 : currentIndex - 1
    guard nextIndex >= 0 && nextIndex < headings.count else { return nil }
    return UIAccessibilityCustomRotorItemResult(targetElement: headings[nextIndex], targetRange: nil)
}
view.accessibilityCustomRotors = [headingsRotor]
```

**Note:** Custom rotors must handle both `.next` and `.previous` search directions.

---

## Summary

| API | Effect | User Experience |
|---|---|---|
| `.accessibilityAddTraits(.isHeader)` | VoiceOver announces "Heading" | Heading appears in built-in Headings rotor |
| `.accessibilityRotorEntry(id:in:)` + `.accessibilityRotor(...)` | Custom rotor category | Users can jump to named sections via rotor |

Always apply `.isHeader` to every section title, navigation bar heading, and grouping label. It costs one line of code and dramatically improves navigation efficiency on long screens.
