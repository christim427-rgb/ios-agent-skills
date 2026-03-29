# VoiceOver Label Quality: What's Wrong With "Heart icon button"

## Severity: 🔴 CRITICAL

The label `"Heart icon button"` violates two fundamental VoiceOver labeling rules simultaneously.

### Problem 1: Label Describes Appearance, Not Purpose

`"Heart icon"` describes what the image looks like, not what it does. VoiceOver users need to understand the **purpose** of a control, not its visual form. A user hears "Heart icon button, button" and has no idea whether tapping it saves an item, sends a like, toggles a favorite, or does something else entirely.

### Problem 2: Label Includes the Element Type

`"button"` is redundant in the label. VoiceOver automatically appends the element type based on traits — since this is a `Button`, VoiceOver already announces "button" after the label. Including it in the label causes VoiceOver to say **"Heart icon button, button"** — the word "button" is spoken twice.

### The Rule

> Don't include element type in `accessibilityLabel`. Say "Play" not "Play button". VoiceOver adds "button" from the trait.

> Don't describe appearance. Say "Add to favorites" not "Red heart icon".

---

## Corrected Code

```swift
// ❌ Current — appearance-based label, includes element type
Button(action: toggleFavorite) {
    Image(systemName: "heart.fill")
}
.accessibilityLabel("Heart icon button")

// ✅ Corrected — purpose-based label, no type in label
Button(action: toggleFavorite) {
    Image(systemName: "heart.fill")
}
.accessibilityLabel("Add to favorites")
```

**VoiceOver reads:** "Add to favorites, button"

If the button is stateful (favorited vs. not favorited), update the label to reflect current state:

```swift
Button(action: toggleFavorite) {
    Image(systemName: isFavorited ? "heart.fill" : "heart")
}
.accessibilityLabel(isFavorited ? "Remove from favorites" : "Add to favorites")
```

**VoiceOver reads (when favorited):** "Remove from favorites, button"

---

## Checklist Summary

| Issue | Rule Violated | Fix |
|---|---|---|
| `"Heart icon"` — describes appearance | Labels must describe purpose | `"Add to favorites"` |
| `"button"` in label text | Don't include element type — VoiceOver adds it | Remove "button" from label |

The label should answer the question: **"What happens when I activate this?"** — not "What does this look like?"
