The accessibility label `"Heart icon button"` has several problems:

## 1. It describes the visual appearance, not the action

The label says "Heart icon button," which tells a VoiceOver user what the element looks like. A blind or low-vision user does not benefit from knowing it is a heart-shaped icon. Accessibility labels should communicate the **purpose** or **action** of the control, not its visual appearance.

## 2. It includes the word "button" (redundant role information)

VoiceOver already announces the element's **trait** (role) automatically. Because this is a `Button`, VoiceOver will say "button" on its own. Including "button" in the label causes VoiceOver to read something like *"Heart icon button, button"*, which is redundant and confusing.

## 3. It includes the word "icon" (unnecessary implementation detail)

The fact that the control is rendered using an icon is a visual implementation detail. VoiceOver users do not need to know the UI is represented by an icon. This adds noise without conveying meaning.

## How to fix it

The label should describe **what the button does** in concise, action-oriented language:

```swift
Button(action: toggleFavorite) {
    Image(systemName: "heart.fill")
}
.accessibilityLabel("Remove from favorites")
```

Or, if the item is not yet favorited:

```swift
.accessibilityLabel("Add to favorites")
```

You can make this dynamic based on state:

```swift
.accessibilityLabel(isFavorite ? "Remove from favorites" : "Add to favorites")
```

## Summary of principles

- **Do** describe the action or purpose (e.g., "Add to favorites").
- **Do not** describe the visual appearance (e.g., "heart," "icon").
- **Do not** include the element's role (e.g., "button") -- VoiceOver provides this automatically.
- **Do** reflect the current state when the control is a toggle.
