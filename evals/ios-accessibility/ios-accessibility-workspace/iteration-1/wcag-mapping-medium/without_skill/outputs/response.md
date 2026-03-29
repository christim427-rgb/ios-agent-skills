# Drag-and-Drop Reordering: WCAG Criteria and iOS Accessibility Fix

## The Problem

Drag-and-drop is a pointer-gesture interaction that requires fine motor control — holding, dragging, and releasing with precision. Users with motor impairments (tremors, limited dexterity, paralysis, switch access users) cannot reliably perform this gesture. They need a keyboard-equivalent or touch-alternative mechanism to accomplish the same reordering task.

---

## Applicable WCAG Criteria

### 1. WCAG 2.1 SC 2.1.1 — Keyboard (Level A)
**"All functionality of the content is operable through a keyboard interface without requiring specific timings for individual keystrokes."**

Drag-and-drop reordering is a function of the interface. If the only way to reorder items is via drag gesture, keyboard/switch users are entirely locked out. You must provide a non-gesture alternative for every action achievable by dragging.

### 2. WCAG 2.1 SC 2.5.1 — Pointer Gestures (Level A)
**"All functionality that uses multipoint or path-based gestures for operation can be operated with a single pointer without a path-based gesture."**

Drag is a path-based gesture (press, move along a path, release). This criterion requires that an alternative single-tap/single-pointer mechanism exist for the same function.

### 3. WCAG 2.1 SC 1.3.1 — Info and Relationships (Level A)
The order/position of items in a list is often meaningful (ranked list, priority queue, playlist). The list order must be programmatically determinable so assistive technologies can convey it correctly.

### 4. WCAG 2.1 SC 4.1.2 — Name, Role, Value (Level A)
Each list item must expose its role, current position in the list, and available actions (e.g., "Move up", "Move down") to assistive technologies via accessibility APIs.

### 5. WCAG 2.1 SC 3.3.2 — Labels or Instructions (Level A)
Users need to know that reordering is possible and how to do it through the alternative mechanism. If there is no visible affordance or instruction for the accessible alternative, this criterion is violated.

### 6. WCAG 2.2 SC 2.5.7 — Dragging Movements (Level AA) *(WCAG 2.2 addition)*
**"All functionality that uses a dragging movement for operation can be achieved by a single pointer without dragging."**

This is the most direct criterion. It explicitly targets drag interactions and requires a single-tap alternative (e.g., a "Move up"/"Move down" button, or a two-step tap-to-select-then-tap-to-place mechanism).

---

## How to Fix It for iOS

### Strategy: Provide an Edit Mode with Move Controls

The iOS pattern for accessible reordering in lists (used by Apple in Settings, Music, Reminders, etc.) is an **edit mode with a reorder handle** that can be activated via VoiceOver's custom actions, plus **"Move Up" / "Move Down"** accessibility actions on each item.

---

### Implementation with UIKit (UITableView)

#### Step 1: Enable the reorder control in the data source

```swift
override func tableView(_ tableView: UITableView, canMoveRowAt indexPath: IndexPath) -> Bool {
    return true
}

override func tableView(_ tableView: UITableView,
                        moveRowAt sourceIndexPath: IndexPath,
                        to destinationIndexPath: IndexPath) {
    // Update your data model
    let item = items.remove(at: sourceIndexPath.row)
    items.insert(item, at: destinationIndexPath.row)
}
```

When `setEditing(true, animated: true)` is called, UITableView automatically shows the three-line drag handle. VoiceOver already knows how to activate this handle using its built-in "Activate" gesture — it announces the row's position and lets users move it up/down with swipe gestures in editing mode.

#### Step 2: Add explicit accessibility custom actions to each cell

For users who cannot use the reorder handle even in edit mode (e.g., Switch Control users), add "Move Up" and "Move Down" as `UIAccessibilityCustomAction` on the cell:

```swift
class ReorderableCell: UITableViewCell {

    var onMoveUp: (() -> Void)?
    var onMoveDown: (() -> Void)?

    override func awakeFromNib() {
        super.awakeFromNib()
        setupAccessibilityActions()
    }

    private func setupAccessibilityActions() {
        let moveUp = UIAccessibilityCustomAction(
            name: "Move Up",
            target: self,
            selector: #selector(handleMoveUp)
        )
        let moveDown = UIAccessibilityCustomAction(
            name: "Move Down",
            target: self,
            selector: #selector(handleMoveDown)
        )
        accessibilityCustomActions = [moveUp, moveDown]
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
```

Wire the closures in `cellForRowAt`:

```swift
cell.onMoveUp = { [weak self] in
    guard let self, indexPath.row > 0 else { return }
    let dest = IndexPath(row: indexPath.row - 1, section: indexPath.section)
    self.tableView(tableView, moveRowAt: indexPath, to: dest)
    tableView.moveRow(at: indexPath, to: dest)
    UIAccessibility.post(notification: .announcement,
                         argument: "Moved to position \(dest.row + 1)")
}
```

#### Step 3: Announce position changes

After a move, post a VoiceOver announcement so the user receives confirmation:

```swift
UIAccessibility.post(
    notification: .announcement,
    argument: "\(item.title) moved to position \(newIndex + 1) of \(items.count)"
)
```

---

### Implementation with SwiftUI (List + .onMove)

SwiftUI's `List` with `.onMove` automatically integrates with VoiceOver's built-in reorder support when edit mode is active:

```swift
struct ReorderableList: View {
    @State private var items = ["First", "Second", "Third", "Fourth"]
    @State private var editMode: EditMode = .inactive

    var body: some View {
        NavigationView {
            List {
                ForEach(items, id: \.self) { item in
                    Text(item)
                        .accessibilityLabel(item)
                        // Custom actions for switch/keyboard users
                        .accessibilityAction(named: "Move Up") {
                            moveItem(item, direction: -1)
                        }
                        .accessibilityAction(named: "Move Down") {
                            moveItem(item, direction: 1)
                        }
                }
                .onMove(perform: move)
            }
            .environment(\.editMode, $editMode)
            .toolbar {
                EditButton()
            }
        }
    }

    private func move(from source: IndexSet, to destination: Int) {
        items.move(fromOffsets: source, toOffset: destination)
    }

    private func moveItem(_ item: String, direction: Int) {
        guard let index = items.firstIndex(of: item) else { return }
        let newIndex = index + direction
        guard newIndex >= 0, newIndex < items.count else { return }
        items.swapAt(index, newIndex)
        UIAccessibility.post(
            notification: .announcement,
            argument: "\(item) moved to position \(newIndex + 1)"
        )
    }
}
```

---

### Additional Considerations

| Consideration | Guidance |
|---|---|
| **Switch Control** | The custom actions (`accessibilityCustomActions`) are surfaced in Switch Control's action menu. Ensure "Move Up" / "Move Down" are always available when the list can be reordered. |
| **VoiceOver position announcement** | Always announce the new position after a move. Include both ordinal position and total count: "Item moved to position 3 of 7." |
| **Visible affordance** | Provide a non-gesture way to enter edit/reorder mode that is reachable without drag (e.g., an "Edit" button in the navigation bar). |
| **Focus management** | After a move, VoiceOver focus should remain on the moved item at its new position. SwiftUI handles this reasonably; UIKit may require manual `UIAccessibility.post(notification: .layoutChanged, argument: movedCell)`. |
| **Reduced Motion** | If your drag animation is elaborate, respect `UIAccessibility.isReduceMotionEnabled` and skip or simplify it. |
| **accessibilityValue** | Set `accessibilityValue` on each cell to its current position ("3 of 7") so the user always knows where an item sits without having to trigger a custom action. |

---

## Summary Table

| WCAG SC | Level | What It Requires | Status Without Fix |
|---|---|---|---|
| 2.1.1 Keyboard | A | All functionality operable without path gesture | Fails — reorder only via drag |
| 2.5.1 Pointer Gestures | A | Path-based gestures must have single-pointer alternative | Fails |
| 1.3.1 Info and Relationships | A | List order programmatically determinable | At risk |
| 4.1.2 Name, Role, Value | A | Position and reorder actions exposed to AT | Fails without custom actions |
| 3.3.2 Labels or Instructions | A | Instructions for accessible reorder mechanism | Fails if no visible affordance |
| 2.5.7 Dragging Movements | AA (2.2) | Drag must have single-pointer non-drag alternative | Fails |

Implementing UITableView edit mode with `UIAccessibilityCustomAction` move-up/move-down actions, paired with position announcements and a visible Edit button, satisfies all six criteria and covers VoiceOver, Switch Control, and full keyboard/hardware-keyboard users.
