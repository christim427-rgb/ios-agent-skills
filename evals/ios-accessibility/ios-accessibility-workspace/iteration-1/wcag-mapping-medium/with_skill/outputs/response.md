# Drag-and-Drop Reordering: WCAG Criteria and iOS Fix

## Applicable WCAG Criteria

### Primary Criterion: WCAG 2.5.7 — Dragging Movements (NEW in WCAG 2.2)

**Level:** AA
**Requirement:** All functionality that uses a dragging movement for operation must be achievable by a single pointer without dragging, unless dragging is essential or the function is determined by the user agent and not modified by the author.

This is the direct criterion. A user with motor impairment cannot reliably perform the sustained press-hold-drag gesture required for touch-based reordering. The criterion requires a non-drag alternative for the same operation.

**iOS API:** `accessibilityCustomActions`

---

### Supporting Criterion: WCAG 2.1.1 — Keyboard (Level A)

**Requirement:** All functionality must be operable via a keyboard interface (which on iOS maps to Switch Control, Full Keyboard Access, and VoiceOver).

A drag-only reorder is not operable by Switch Control users (who cannot perform complex drag gestures) or Full Keyboard Access users (external keyboard). Custom actions satisfy this criterion by providing keyboard-accessible alternatives.

---

### Supporting Criterion: WCAG 4.1.2 — Name, Role, Value (Level A)

**Requirement:** For all user interface components, the name and role can be programmatically determined; states, properties, and changes can be set and notified.

A custom drag handle or draggable row without accessibility attributes has no programmatic role or interaction model. Assistive technology cannot discover that the element is reorderable, nor announce position changes.

---

## How to Fix It for iOS

### The Core Pattern: `accessibilityCustomActions`

Add custom actions to each reorderable row/cell that let the user move the item up or down without dragging. VoiceOver exposes these via a swipe-up/swipe-down gesture on the focused element. Switch Control and Full Keyboard Access users access them via the actions menu.

---

### SwiftUI Fix

```swift
// ❌ Current — drag-only, invisible to assistive technology
List {
    ForEach(items) { item in
        Text(item.title)
    }
    .onMove { source, destination in
        items.move(fromOffsets: source, toOffset: destination)
    }
}

// ✅ Corrected — drag still works, but non-drag alternatives added
List {
    ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
        Text(item.title)
            .accessibilityLabel(item.title)
            .accessibilityValue("Position \(index + 1) of \(items.count)")
            .accessibilityCustomActions {
                if index > 0 {
                    AccessibilityCustomAction(name: "Move up") { _ in
                        items.move(fromOffsets: IndexSet(integer: index),
                                   toOffset: index - 1)
                        return true
                    }
                }
                if index < items.count - 1 {
                    AccessibilityCustomAction(name: "Move down") { _ in
                        items.move(fromOffsets: IndexSet(integer: index),
                                   toOffset: index + 2)
                        return true
                    }
                }
                return []
            }
    }
    .onMove { source, destination in
        items.move(fromOffsets: source, toOffset: destination)
    }
}
.environment(\.editMode, .constant(.active))
```

**VoiceOver announces:**
- On focus: "Task name. Position 2 of 5."
- After activating "Move up": "Task name. Position 1 of 5." (position value updates)

---

### UIKit Fix

```swift
// ❌ Current — UITableView with drag reorder, no accessibility alternative
// tableView.dragInteractionEnabled = true

// ✅ Corrected — override accessibilityCustomActions on each cell
class ReorderableCell: UITableViewCell {

    var onMoveUp: (() -> Void)?
    var onMoveDown: (() -> Void)?
    var positionLabel: String = ""

    override var accessibilityValue: String? {
        get { return positionLabel }
        set { super.accessibilityValue = newValue }
    }

    override var accessibilityCustomActions: [UIAccessibilityCustomAction]? {
        get {
            var actions: [UIAccessibilityCustomAction] = []
            if let moveUp = onMoveUp {
                actions.append(UIAccessibilityCustomAction(
                    name: "Move up",
                    target: self,
                    selector: #selector(handleMoveUp)
                ))
            }
            if let moveDown = onMoveDown {
                actions.append(UIAccessibilityCustomAction(
                    name: "Move down",
                    target: self,
                    selector: #selector(handleMoveDown)
                ))
            }
            return actions.isEmpty ? nil : actions
        }
        set { super.accessibilityCustomActions = newValue }
    }

    @objc private func handleMoveUp() -> Bool {
        onMoveUp?()
        return true
    }

    @objc private func handleMoveDown() -> Bool {
        onMoveDown?()
        return true
    }
}

// In UITableViewDataSource / ViewModel, wire up the closures and position labels:
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "cell",
                                             for: indexPath) as! ReorderableCell
    let item = items[indexPath.row]
    cell.textLabel?.text = item.title
    cell.positionLabel = "Position \(indexPath.row + 1) of \(items.count)"

    cell.onMoveUp = indexPath.row > 0 ? { [weak self] in
        self?.moveItem(from: indexPath.row, to: indexPath.row - 1)
        // Post announcement after move:
        UIAccessibility.post(notification: .announcement,
                             argument: "\(item.title). Position \(indexPath.row) of \(self?.items.count ?? 0).")
    } : nil

    cell.onMoveDown = indexPath.row < items.count - 1 ? { [weak self] in
        self?.moveItem(from: indexPath.row, to: indexPath.row + 1)
        UIAccessibility.post(notification: .announcement,
                             argument: "\(item.title). Position \(indexPath.row + 2) of \(self?.items.count ?? 0).")
    } : nil

    return cell
}
```

---

## Announcement Strategy

After a move completes, announce the new position so the user gets confirmation without having to navigate away and back:

```swift
// SwiftUI — post after state change
AccessibilityCustomAction(name: "Move up") { _ in
    items.move(fromOffsets: IndexSet(integer: index), toOffset: index - 1)
    // accessibilityValue update triggers announcement automatically in SwiftUI
    // If not, post explicitly:
    UIAccessibility.post(notification: .announcement,
                         argument: "\(item.title) moved to position \(index).")
    return true
}
```

---

## Checklist: What to Verify

| Check | Criterion Satisfied |
|---|---|
| Each row has `accessibilityCustomActions` with "Move up" / "Move down" | WCAG 2.5.7, 2.1.1 |
| "Move up" hidden/absent for first item; "Move down" absent for last item | Prevents meaningless actions |
| `accessibilityValue` reflects current position ("Position 2 of 5") | WCAG 4.1.2 |
| Position announced after move completes | WCAG 4.1.3 (Status Messages) |
| Drag reorder still works for users who can perform it | Non-regression |
| Row has `accessibilityLabel` (item name) | WCAG 1.1.1, 4.1.2 |

---

## Assistive Technology User Experience

| Technology | How They Reorder |
|---|---|
| VoiceOver | Focus the row. Swipe up/down to browse custom actions. Double-tap "Move up" or "Move down." |
| Switch Control | Focus the row. Open actions menu via switch. Select "Move up" or "Move down." |
| Full Keyboard Access | Tab to the row. Open the accessibility actions menu. Activate move action. |
| Voice Control | Say "Show actions" or "Move up" / "Move down" (if label matches). |
| Touch (no impairment) | Long-press drag handle as before — no regression. |

---

## Severity Summary

| Issue | Severity | Criterion |
|---|---|---|
| No non-drag reorder alternative | 🔴 CRITICAL | WCAG 2.5.7 (AA), 2.1.1 (A) |
| Missing `accessibilityValue` (no position announced) | 🟡 HIGH | WCAG 4.1.2 (A) |
| No post-move announcement | 🟢 MEDIUM | WCAG 4.1.3 (AA) |
