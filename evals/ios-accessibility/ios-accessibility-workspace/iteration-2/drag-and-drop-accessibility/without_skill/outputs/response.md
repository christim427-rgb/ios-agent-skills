# Drag-and-Drop Reorder Inaccessible for Motor Impaired Users

## Relevant WCAG Criteria

### 2.1.1 Keyboard (Level A)
> "All functionality of the content is operable through a keyboard interface."

On iOS, this extends to Switch Control and Full Keyboard Access. Any action achievable via drag-and-drop must also be achievable through an alternative non-drag mechanism.

### 2.5.1 Pointer Gestures (Level A, WCAG 2.1)
> "All functionality that uses multipoint or path-based gestures can also be operated with a single pointer without a path-based gesture."

Drag-and-drop is a path-based gesture. An alternative single-tap mechanism must exist.

### 2.1.3 Keyboard (No Exception) (Level AAA)
Full keyboard access for all functionality.

## iOS Fix Options

### Option 1: EditButton + Move Affordance (Easiest)

In SwiftUI `List`, use `.onMove`:

```swift
List {
    ForEach(items) { item in
        Text(item.name)
    }
    .onMove { source, destination in
        items.move(fromOffsets: source, toOffset: destination)
    }
}
.toolbar {
    EditButton() // activates the standard three-line move handle
}
```

When in edit mode, reorder handles appear. These work with VoiceOver (two-finger scrub activates reorder mode) and Switch Control.

### Option 2: Explicit Move Up / Move Down Actions

Add accessibility actions to each row so VoiceOver users can reorder without dragging:

```swift
ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
    Text(item.name)
        .accessibilityElement(children: .combine)
        .accessibilityLabel(item.name)
        .accessibilityAction(named: "Move up") {
            guard index > 0 else { return }
            items.swapAt(index, index - 1)
        }
        .accessibilityAction(named: "Move down") {
            guard index < items.count - 1 else { return }
            items.swapAt(index, index + 1)
        }
}
```

VoiceOver users can activate custom actions via the Actions rotor.

### Option 3: UIKit — UIAccessibilityCustomAction

```swift
override var accessibilityCustomActions: [UIAccessibilityCustomAction]? {
    get {
        [
            UIAccessibilityCustomAction(name: "Move up", target: self, selector: #selector(moveUp)),
            UIAccessibilityCustomAction(name: "Move down", target: self, selector: #selector(moveDown))
        ]
    }
    set { }
}
```

### Option 4: UIKit — UITableView with accessibilityActivate

Implement `accessibilityScroll(_:)` and use the built-in reorder control. When `UITableView` is in edit mode, rows expose a reorder accessibility action automatically.

## Best Practice

Combine both: keep drag-and-drop for users who can use it, and add Move Up / Move Down accessibility actions for those who cannot. The two approaches are additive.

## Testing

- VoiceOver: Navigate to a row, swipe up/down to find custom actions in the Actions rotor, double-tap to activate.
- Switch Control: Verify move actions appear in the item menu.
- Full Keyboard Access (iPadOS): Tab to a row and verify keyboard shortcuts or actions exist.
