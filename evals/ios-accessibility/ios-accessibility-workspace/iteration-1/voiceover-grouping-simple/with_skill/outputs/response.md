# `.accessibilityElement(children: .combine)` vs `.accessibilityElement(children: .ignore)`

These two modifiers both turn a container into a single VoiceOver element, but they differ in how the label for that element is constructed.

## `.combine` -- Automatic Label from Children

`.combine` merges all children into one accessibility element and **joins their labels with pauses** (announced as comma-separated).

```swift
HStack {
    Text("Price")
    Text("$9.99")
}
.accessibilityElement(children: .combine)
// VoiceOver reads: "Price, $9.99"
```

You get a single swipe target and VoiceOver concatenates the children's labels automatically. This is the right choice when the children's existing labels, read sequentially, already make sense together.

**Use `.combine` when:**
- The container is a single conceptual item (product card, list cell, table row).
- The children's labels read naturally when joined: "Inbox, 3 unread messages" or "Price, $9.99".
- You don't need to rewrite or reformat what VoiceOver says.

## `.ignore` -- Custom Label You Write Yourself

`.ignore` hides all children from VoiceOver entirely and requires you to provide a custom `accessibilityLabel` on the parent. This gives you full control over what VoiceOver reads.

```swift
HStack {
    Text("4")
    Image(systemName: "star.fill")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("4 out of 5 stars")
// VoiceOver reads: "4 out of 5 stars"
```

Without the custom label, VoiceOver would read nothing -- the children are hidden and the parent has no label of its own.

**Use `.ignore` when:**
- Joining the children's labels would sound awkward or confusing (e.g., "4, star.fill" is not useful).
- You need a natural sentence rather than a comma-separated list of fragments.
- The visual layout uses icons, symbols, or formatting that doesn't translate well to speech.
- You want to add context that isn't present in any single child (e.g., "Storage: 5 gigabytes for Basic, 100 gigabytes for Pro").

## Side-by-Side Comparison

| Aspect | `.combine` | `.ignore` |
|---|---|---|
| Label source | Auto-joined from children | You provide it manually |
| Reading style | Comma-separated pause between each child | Single natural sentence |
| Effort | Zero -- just apply the modifier | Must write an `accessibilityLabel` |
| Risk | Awkward if children have poor labels | Silent if you forget the label |
| Interactive children | Buttons inside `.combine` lose individual identity -- they get merged | Same -- all children are hidden |

## When `.combine` Produces Awkward Results

If `.combine` reads badly, switch to `.ignore`:

```swift
// .combine reads: "4, star.fill, filled"  -- not helpful
HStack {
    Text("4")
    Image(systemName: "star.fill")
}
.accessibilityElement(children: .combine)

// .ignore + custom label reads: "4 out of 5 stars"  -- clear
HStack {
    Text("4")
    Image(systemName: "star.fill")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("4 out of 5 stars")
```

## Important Warning for Both

If your container has interactive children (buttons, toggles), both `.combine` and `.ignore` will absorb those children into a single element. The individual buttons become unreachable. If children need to remain independently tappable, use `.accessibilityElement(children: .contain)` instead, or use `.accessibilityCustomActions` to expose the actions through VoiceOver's swipe-up/swipe-down gesture:

```swift
HStack {
    Text(item.name)
    // These buttons would be lost with .combine or .ignore
}
.accessibilityElement(children: .combine)
.accessibilityCustomActions([
    .init(named: "Like") { likeItem(); return true },
    .init(named: "Share") { shareItem(); return true },
])
```

## Quick Decision Rule

- Children's labels read fine when joined? Use **`.combine`**.
- Need to rewrite what VoiceOver says? Use **`.ignore`** + custom label.
- Children are independently interactive? Use **`.contain`** (or don't group at all).
