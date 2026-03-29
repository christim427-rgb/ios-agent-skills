# Reducing VoiceOver Swipe Count with Custom Actions

## The Problem

Your current layout creates **4 separate VoiceOver focus stops per cell** (the title + 3 buttons). For a list of 10 items, that is 40 swipes just to reach the bottom. VoiceOver users rightfully find this exhausting.

```swift
// Current: 4 swipes per cell (title, Like, Share, Delete)
ForEach(items) { item in
    HStack {
        Text(item.title)
        Spacer()
        Button("Like") { like(item) }
        Button("Share") { share(item) }
        Button("Delete") { delete(item) }
    }
}
```

**VoiceOver experience today:**
- Swipe right: "Item title"
- Swipe right: "Like, Button"
- Swipe right: "Share, Button"
- Swipe right: "Delete, Button"
- (repeat for every cell)

## The Fix: Custom Actions

Use `.accessibilityElement(children: .combine)` to collapse each cell into a single focus stop, then attach the buttons as `.accessibilityCustomAction` entries. VoiceOver users swipe up/down to cycle through actions on the focused element instead of swiping right through separate buttons.

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
    .accessibilityCustomAction(named: "Like") {
        like(item)
        return true
    }
    .accessibilityCustomAction(named: "Share") {
        share(item)
        return true
    }
    .accessibilityCustomAction(named: "Delete") {
        delete(item)
        return true
    }
}
```

**VoiceOver experience after the fix:**
- Swipe right: "Item title, Like, Share, Delete" (single element, one swipe)
- Swipe up/down: cycles through "Like", "Share", "Delete" actions
- Double-tap: activates the selected action
- Swipe right again: moves to the next item

This takes the per-cell cost from **4 swipes down to 1 swipe**, with actions accessible via the vertical swipe gesture.

## Why This Works

- **`.accessibilityElement(children: .combine)`** merges all child labels into one VoiceOver element. The title and button labels are read together as a single announcement.
- **`.accessibilityCustomAction`** registers each action in VoiceOver's "Actions" rotor. Users swipe up or down to pick an action, then double-tap to execute it. This is the standard iOS pattern for list cells with multiple operations (Mail uses it for flag/archive/delete, Messages uses it for pin/mute/delete).
- The return value `true` tells VoiceOver the action succeeded. Return `false` if the action fails so VoiceOver can announce the failure.

## Alternative: `.ignore` + Explicit Label

If `.combine` produces an awkward reading (e.g., "Buy milk, Like, Share, Delete" with pauses between each word), use `.ignore` with a hand-written label for a more natural sentence:

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
    .accessibilityCustomAction(named: "Like") {
        like(item)
        return true
    }
    .accessibilityCustomAction(named: "Share") {
        share(item)
        return true
    }
    .accessibilityCustomAction(named: "Delete") {
        delete(item)
        return true
    }
}
```

**VoiceOver reads:** "Buy milk" (clean, no button names appended). Actions are still available via swipe up/down.

Use `.combine` when the merged reading sounds natural. Use `.ignore` + explicit label when you want full control over what VoiceOver announces.

## Adding a Hint for Discoverability

New VoiceOver users may not know about custom actions. Add a hint on the first cell to teach the gesture:

```swift
.accessibilityHint("Swipe up or down for actions")
```

Only add this to the first item or use it sparingly -- hints repeat on every focus and can become annoying if applied to every cell.

## WCAG Mapping

| Criterion | Status |
|---|---|
| **1.3.1 Info and Relationships** | Custom actions preserve the relationship between the item and its operations |
| **2.1.1 Keyboard** | All actions remain operable via VoiceOver, Switch Control, and Full Keyboard Access |
| **2.4.3 Focus Order** | One logical focus stop per item instead of fragmented buttons |
| **4.1.2 Name, Role, Value** | Each custom action has a clear name; the cell has a clear label |
