There are two problems with this label.

## 1. The label describes appearance, not purpose

`"Heart icon button"` tells the VoiceOver user what the element *looks like*, not what it *does*. A blind user does not benefit from knowing the icon is a heart shape. The label should communicate the action or meaning — in this case, that it toggles a favorite.

Additionally, because this is a stateful toggle (`toggleFavorite`), the label should change dynamically to reflect the current state. A static label leaves the user unsure whether the item is already favorited or not.

## 2. The label includes the element type

VoiceOver automatically announces "button" based on the `Button` control's built-in `.button` trait. Writing "button" inside the `accessibilityLabel` causes VoiceOver to read "Heart icon button — button", which is redundant and confusing. Labels should never include the element type.

## What VoiceOver reads today

> "Heart icon button — button"

## Corrected code

```swift
Button(action: toggleFavorite) {
    Image(systemName: isFavorite ? "heart.fill" : "heart")
}
.accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")
```

**VoiceOver now reads:**

- When not favorited: "Add to favorites — button"
- When favorited: "Remove from favorites — button"

## Why this matters

- **WCAG 1.1.1 (Non-text Content)** requires a text alternative that serves the equivalent purpose, not a description of the visual.
- **WCAG 4.1.2 (Name, Role, Value)** requires that the name and state of controls are programmatically determinable. A static label on a toggle fails this.
- The Apple Human Interface Guidelines state that accessibility labels should describe what an element does, not what it looks like.

## Rules applied

| Rule | Violation in original |
|---|---|
| Don't describe appearance | "Heart icon" describes the visual |
| Don't include element type | "button" is redundant with the `.button` trait |
| Update label when state changes | Static label on a toggle action |
| Keep labels short and action-oriented | "Heart icon button" is neither short nor action-oriented |
