# Drag-and-Drop Reorder Accessibility

## WCAG Criteria

Two WCAG 2.2 criteria apply directly:

**2.5.7 Dragging Movements (Level AA, NEW in 2.2)**
All functionality that uses a dragging movement must also be operable with a single pointer without dragging. On iOS, this means drag-to-reorder must have an alternative single-tap mechanism.

**2.5.8 Target Size Minimum (Level AA, NEW in 2.2)**
Touch targets must be at least 24×24pt (WCAG minimum). Apple's Human Interface Guidelines are stricter: **44×44pt** is the recommended minimum. Drag handles that are too small violate both.

## The Problem

```swift
// ❌ Drag-only reorder — inaccessible to VoiceOver, Switch Control, motor impairments
List {
    ForEach(items, id: \.id) { item in
        Text(item.title)
    }
    .onMove { source, destination in
        items.move(fromOffsets: source, toOffset: destination)
    }
}
.toolbar {
    EditButton()
}
```

`onMove` with edit mode only works visually. VoiceOver users, Switch Control users, and users with motor impairments who cannot perform drag gestures have no alternative.

## The Fix: accessibilityCustomActions for Reorder

Provide `accessibilityCustomActions` with explicit "Move Up" / "Move Down" actions. These appear in VoiceOver's action menu (swipe up/down to cycle), in Switch Control's menu, and are activatable by Voice Control.

```swift
struct ReorderableList: View {
    @State private var items: [ListItem]

    var body: some View {
        List {
            ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
                Text(item.title)
                    .accessibilityCustomActions {
                        // Move Up — available for all items except the first
                        if index > 0 {
                            AccessibilityCustomAction(named: "Move Up") {
                                withAnimation {
                                    items.move(fromOffsets: IndexSet(integer: index),
                                               toOffset: index - 1)
                                }
                                return true
                            }
                        }
                        // Move Down — available for all items except the last
                        if index < items.count - 1 {
                            AccessibilityCustomAction(named: "Move Down") {
                                withAnimation {
                                    items.move(fromOffsets: IndexSet(integer: index),
                                               toOffset: index + 2)
                                }
                                return true
                            }
                        }
                        // Move to specific position
                        AccessibilityCustomAction(named: "Move to Top") {
                            withAnimation {
                                items.move(fromOffsets: IndexSet(integer: index),
                                           toOffset: 0)
                            }
                            return true
                        }
                        return []
                    }
            }
            .onMove { source, destination in
                items.move(fromOffsets: source, toOffset: destination)
            }
        }
    }
}
```

VoiceOver interaction: focus item → swipe up → hear "Move Up, Move Down, Move to Top" → double-tap to activate.

## UIKit Pattern

```swift
// In UITableViewCell or UICollectionViewCell
override var accessibilityCustomActions: [UIAccessibilityCustomAction]? {
    get {
        var actions: [UIAccessibilityCustomAction] = []

        if canMoveUp {
            actions.append(UIAccessibilityCustomAction(
                name: "Move Up",
                target: self,
                selector: #selector(moveItemUp)
            ))
        }
        if canMoveDown {
            actions.append(UIAccessibilityCustomAction(
                name: "Move Down",
                target: self,
                selector: #selector(moveItemDown)
            ))
        }
        return actions
    }
    set { }
}
```

## Touch Target Size (WCAG 2.5.8 and Apple HIG)

Drag handles and reorder controls must meet minimum touch target requirements:

| Standard | Minimum |
|---|---|
| WCAG 2.5.8 (AA) | 24×24pt |
| Apple HIG | 44×44pt (recommended) |

```swift
// ❌ Too small — 20×20pt drag handle
Image(systemName: "line.3.horizontal")
    .frame(width: 20, height: 20)

// ✅ Meets Apple HIG
Image(systemName: "line.3.horizontal")
    .frame(width: 44, height: 44)
    .contentShape(Rectangle())  // Ensures full frame is tappable
```

For items smaller than 44pt visually, use `.frame(minWidth: 44, minHeight: 44)` or increase the content shape without changing the visual size:

```swift
Image(systemName: "line.3.horizontal")
    .font(.body)
    .frame(width: 44, height: 44)
    .contentShape(Rectangle())
    .accessibilityLabel("Drag to reorder")
```

## Announcement After Reorder

Post a VoiceOver announcement after completing a move so the user gets confirmation:

```swift
AccessibilityCustomAction(named: "Move Up") {
    items.move(fromOffsets: IndexSet(integer: index), toOffset: index - 1)
    UIAccessibility.post(
        notification: .announcement,
        argument: "\(item.title) moved to position \(index)"
    )
    return true
}
```
