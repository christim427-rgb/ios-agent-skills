# Reducing VoiceOver Swipes in List Rows with Action Buttons

## The Problem

In your current implementation, VoiceOver treats every element in the `HStack` as a separate accessible element. For a list with N items, a VoiceOver user must perform up to **4N swipes** (title + 3 buttons per row) just to navigate through the list. This is a poor experience.

## Solution: Use `.accessibilityElement(children: .combine)` with Custom Actions

The recommended approach is to make each row a **single** VoiceOver element and expose the buttons as **custom accessibility actions** instead of individual focusable elements. This reduces navigation to **1 swipe per row**.

### Recommended Implementation

```swift
ForEach(items) { item in
    HStack {
        Text(item.title)
        Spacer()
        Button("Like") { like(item) }
        Button("Share") { share(item) }
        Button("Delete") { delete(item) }
    }
    .accessibilityElement(children: .combine)
    .accessibilityActions {
        Button("Like") { like(item) }
        Button("Share") { share(item) }
        Button("Delete") { delete(item) }
    }
}
```

### How This Works

1. **`.accessibilityElement(children: .combine)`** collapses the entire `HStack` into a single VoiceOver focus point. VoiceOver reads the combined text content (the title) as one element.
2. **`.accessibilityActions { ... }`** registers the three actions in the VoiceOver Actions rotor. Users access them by **swiping up or down** once focused on the row, rather than swiping right through each button individually.

### VoiceOver User Experience After the Fix

- **Swipe right** moves to the next row (1 swipe per item instead of 4).
- **Swipe up/down** on a focused row cycles through the custom actions: "Like", "Share", "Delete".
- **Double-tap** activates the currently selected action.

## Alternative: `.accessibilityElement(children: .ignore)` with Manual Label

If you need more control over what VoiceOver reads, you can ignore children entirely and set the label manually:

```swift
ForEach(items) { item in
    HStack {
        Text(item.title)
        Spacer()
        Button("Like") { like(item) }
        Button("Share") { share(item) }
        Button("Delete") { delete(item) }
    }
    .accessibilityElement(children: .ignore)
    .accessibilityLabel(item.title)
    .accessibilityActions {
        Button("Like") { like(item) }
        Button("Share") { share(item) }
        Button("Delete") { delete(item) }
    }
}
```

This is useful when `.combine` produces a confusing reading order or includes unwanted text from button labels in the spoken output.

## Also Consider: SwiftUI Swipe Actions

If you are on iOS 15+ and the actions are contextual row operations, you can also use the native `.swipeActions` modifier, which automatically integrates with VoiceOver's actions rotor:

```swift
ForEach(items) { item in
    HStack {
        Text(item.title)
        Spacer()
    }
    .swipeActions(edge: .trailing) {
        Button("Delete", role: .destructive) { delete(item) }
        Button("Share") { share(item) }
    }
    .swipeActions(edge: .leading) {
        Button("Like") { like(item) }
    }
}
```

With `.swipeActions`, SwiftUI automatically exposes these as VoiceOver custom actions without needing `.accessibilityActions` at all. VoiceOver users can access them via the Actions rotor. This is the most idiomatic approach for list row actions on iOS 15+.

## Summary

| Approach | Swipes per Row | VoiceOver Action Access |
|---|---|---|
| Original (no changes) | 4 | Swipe right to each button |
| `.combine` + `.accessibilityActions` | 1 | Swipe up/down on row |
| `.ignore` + manual label + `.accessibilityActions` | 1 | Swipe up/down on row |
| `.swipeActions` (iOS 15+) | 1 | Swipe up/down on row (automatic) |

The key principle is: **collapse the row into one focusable element and move actions into the VoiceOver Actions rotor** using either `.accessibilityActions` or `.swipeActions`. This transforms the experience from O(4N) swipes to O(N) swipes for a list of N items.
