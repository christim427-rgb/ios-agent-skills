# `.accessibilityElement(children: .combine)` vs `.ignore`

## Overview

Both `.combine` and `.ignore` collapse child elements into a single VoiceOver element on the parent container. The difference is in **how the label is generated** and **what VoiceOver announces**.

---

## `.combine` — Merge Children's Labels

`children: .combine` takes each child element's accessibility label and **joins them with brief pauses**, in layout order.

```swift
// ❌ No grouping — 3 separate swipes
HStack {
    Text("Noise-Cancelling Headphones")
    Text("$79.99")
    Text("In stock")
}

// ✅ .combine — merges children's labels automatically
HStack {
    Text("Noise-Cancelling Headphones")
    Text("$79.99")
    Text("In stock")
}
.accessibilityElement(children: .combine)
```

**VoiceOver reads:** "Noise-Cancelling Headphones, $79.99, In stock" (with short pauses between each part)

### When to use `.combine`

- The children's labels are already meaningful on their own
- The default join order (top-to-bottom, left-to-right) produces a readable result
- You don't need to rewrite or reframe the content
- Simple cards, list cell rows, label/value pairs

---

## `.ignore` — Provide a Custom Label

`children: .ignore` **hides all children from VoiceOver** and requires you to set a custom `accessibilityLabel` on the parent. You write exactly what VoiceOver says.

```swift
// ✅ .ignore + custom label — natural sentence
HStack {
    Text("4")
        .font(.largeTitle)
        .bold()
    Text("out of")
    Text("5")
    Image(systemName: "star.fill")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("Rated 4 out of 5 stars")
```

**VoiceOver reads:** "Rated 4 out of 5 stars" (single, smooth sentence — no pauses)

### When to use `.ignore`

- `.combine` produces an awkward or unnatural result (e.g., joining "4", "out of", "5", "star fill")
- You need to add context not present in any individual child ("Rated" in the example above)
- The reading order of joined labels would be confusing
- Content requires a natural language sentence rather than a list of values
- Star ratings, score displays, complex status indicators

---

## `.contain` — Keep Children Separate (Default Behavior)

For completeness: `children: .contain` keeps each child as an independent VoiceOver element grouped under this container — this is essentially the default behavior.

```swift
// Use .contain for forms with multiple independent inputs
VStack {
    TextField("First name", text: $firstName)
    TextField("Last name", text: $lastName)
    Toggle("Subscribe", isOn: $subscribe)
}
.accessibilityElement(children: .contain)
```

---

## Decision Guide

```
Are children independently interactive (buttons, toggles, text fields)?
├── YES → .contain (or default — keep them separate)
└── NO  → Should be a single VoiceOver element
    ├── Do children's labels read naturally when joined with pauses?
    │   ├── YES → .combine
    │   └── NO  → .ignore + custom accessibilityLabel
```

---

## Side-by-Side Comparison

| | `.combine` | `.ignore` |
|---|---|---|
| Label source | Joined children's labels | Your custom `accessibilityLabel` |
| Pauses between parts | Yes — comma-like pauses | No — reads as one sentence |
| Effort | Zero — automatic | Manual — you write the label |
| Best for | Simple, already-readable children | Complex content needing natural language |
| Interactive children | Combined (buttons lose interactivity) | All children hidden — custom actions needed |

---

## Gotcha: Buttons Inside `.combine`

When you use `.combine` on a container that includes `Button` views, those buttons are merged into the combined element. Their tap actions are **lost** — users cannot activate them individually. If the container needs to be tappable, wrap the whole container in a `Button` instead.

```swift
// ❌ Button inside .combine — button action is lost
HStack {
    Text("Item name")
    Button("Delete") { deleteItem() }  // VoiceOver cannot activate this
}
.accessibilityElement(children: .combine)

// ✅ Either use custom actions, or don't combine
HStack { Text("Item name") }
    .accessibilityElement(children: .combine)
    .accessibilityCustomActions([
        .init(named: "Delete") { deleteItem(); return true }
    ])
```
