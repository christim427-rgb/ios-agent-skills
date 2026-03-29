## Reducing VoiceOver Swipes in List Cells with Action Buttons

### The Problem

When each cell has a title plus 3 action buttons, VoiceOver users must swipe through 4 elements per cell. In a long list this is exhausting and slow.

### Solution: Custom Accessibility Actions

Collapse the entire cell into **one focus element** and expose the action buttons as custom accessibility actions. The user can then flick up/down to cycle through available actions and double-tap to invoke one — all from a single focus stop.

#### SwiftUI

```swift
HStack {
    Text(item.title)
    Spacer()
    Button("Delete") { deleteItem(item) }
    Button("Share") { shareItem(item) }
    Button("Archive") { archiveItem(item) }
}
.accessibilityElement(children: .ignore)          // merge into one element
.accessibilityLabel(item.title)
.accessibilityAddTraits(.isButton)                 // optional, if the cell itself is tappable
.accessibilityAction(named: "Delete") { deleteItem(item) }
.accessibilityAction(named: "Share")  { shareItem(item) }
.accessibilityAction(named: "Archive") { archiveItem(item) }
```

VoiceOver announces: _"Item title, actions available"_. The user flicks up or down to hear "Delete", "Share", "Archive", then double-taps to invoke.

#### UIKit

```swift
cell.accessibilityCustomActions = [
    UIAccessibilityCustomAction(name: "Delete",  target: self, selector: #selector(deleteAction(_:))),
    UIAccessibilityCustomAction(name: "Share",   target: self, selector: #selector(shareAction(_:))),
    UIAccessibilityCustomAction(name: "Archive", target: self, selector: #selector(archiveAction(_:))),
]
```

Make the cell itself the single accessible element by setting `accessibilityLabel` on the cell and marking the child buttons `isAccessibilityElement = false`.

### Result

| Before | After |
|--------|-------|
| 4 swipes per cell (title + 3 buttons) | 1 swipe per cell |
| Actions triggered by navigating to button then double-tapping | Actions triggered by flick up/down + double-tap from the cell |

### Additional Tips

- Name actions as **verbs** ("Delete", "Mark as read") — not nouns.
- If an action is destructive, you can still name it clearly; VoiceOver will not add extra warnings automatically, so be descriptive ("Delete conversation" rather than just "Delete").
- Consider a default action for the most common tap (`.accessibilityAction(.default) { openItem(item) }`) so a simple double-tap opens the item.
