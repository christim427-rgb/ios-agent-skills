## `.accessibilityElement(children: .combine)` vs `.ignore`

Both modifiers collapse a container's children into a single accessible element, but they differ in **how the label is produced**.

---

### `.accessibilityElement(children: .combine)`

- Keeps all child accessibility labels and **concatenates** them (with a space or comma depending on iOS version).
- The resulting label is auto-generated from the child views' own labels.
- Good when the children already have sensible labels and you just want to merge them into one focus stop.

```swift
VStack {
    Image(systemName: "clock")
        .accessibilityLabel("Clock")
    Text("9:41 AM")
}
.accessibilityElement(children: .combine)
// VoiceOver reads: "Clock, 9:41 AM"
```

**Limitation:** The concatenation order follows the view hierarchy and can produce awkward strings (e.g., star symbols from rating views). You cannot control the exact wording.

---

### `.accessibilityElement(children: .ignore)`

- **Hides all children** from the accessibility tree entirely.
- The container itself becomes the single accessible element with **no label by default** — you must supply one explicitly.
- Use when you want full control over the label, value, hint, and traits.

```swift
VStack {
    Image(systemName: "heart.fill")
    Text("Favorites")
    Text("12 items")
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("Favorites, 12 items")
// VoiceOver reads exactly: "Favorites, 12 items"
```

---

### Comparison Table

| Aspect | `.combine` | `.ignore` |
|--------|-----------|-----------|
| Child labels | Concatenated automatically | Discarded — must set manually |
| Control over wording | Limited | Full |
| Effort | Low | Medium |
| Best for | Simple containers with good child labels | Complex cards, custom formatting needed |
| Risk | Awkward auto-generated strings | Forgetting to set a label (silent accessibility bug) |

---

### Third Option: `.contain`

There is also `.accessibilityElement(children: .contain)` — the default. It keeps children as **individual** accessible elements. Use this when you want separate focus stops for each child (e.g., interactive items like buttons inside a card).

---

### Decision Guide

1. Children have simple text labels and you want one swipe stop → **`.combine`**
2. You need exact wording, a rating "4 out of 5 stars", or a mixed content card → **`.ignore` + explicit label**
3. Children are individually interactive (buttons, toggles) → **`.contain`** (default)
