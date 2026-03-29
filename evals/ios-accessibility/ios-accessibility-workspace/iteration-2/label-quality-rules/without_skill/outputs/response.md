## Problem with the VoiceOver Label

The label `"Heart icon button"` has several issues:

### Issues

1. **Redundant role announcement** — VoiceOver automatically appends the element's trait/role (e.g., "button") after the label. Writing "button" in the label causes VoiceOver to read "Heart icon button, button" — the word "button" is spoken twice.

2. **Describes appearance, not purpose** — "Heart icon" describes the visual appearance of the image, not what the action does. A blind user hears "Heart icon button" but has no idea what tapping it will accomplish.

3. **"Icon" is noise** — Saying "icon" adds no useful information. VoiceOver users do not benefit from knowing the underlying asset is an icon.

### What a good label looks like

The label should be short, action-oriented, and describe the **purpose** — not the appearance:

```swift
Button(action: toggleFavorite) {
    Image(systemName: "heart.fill")
}
.accessibilityLabel("Add to favorites")
```

Or, if the item is already favorited and the action removes it:

```swift
.accessibilityLabel(isFavorited ? "Remove from favorites" : "Add to favorites")
```

### Rules of thumb for VoiceOver labels

- **Do not include the role** (button, image, slider) — VoiceOver announces it automatically from the trait.
- **Do not say "icon", "image", "graphic"** — same reason.
- **Use the imperative or a noun phrase** that describes the purpose: "Add to favorites", "Delete item", "Profile photo".
- **Keep it concise** — ideally 1–3 words.
- **Localize** the label so it reads naturally in every supported language.
