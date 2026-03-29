# When to Use `accessibilityHint` vs `accessibilityLabel`

## `accessibilityLabel`

The `accessibilityLabel` is the **primary identifier** for an accessibility element. It tells VoiceOver users **what** the element is. It should be a short, concise description of the element's purpose or content.

**When to use it:**

- On every interactive element (buttons, links, text fields, switches, sliders, etc.)
- On images that convey meaning
- When the default label derived from the element's title or text is missing, unclear, or insufficient

**Guidelines:**

- Keep it short and descriptive (e.g., "Play", "Delete", "Search")
- Do not include the element's type/role (e.g., say "Play" not "Play button" -- VoiceOver announces the trait automatically)
- Start with a capitalized word
- Do not end with a period
- Localize it

**Examples:**

```swift
playButton.accessibilityLabel = "Play"
trashIcon.accessibilityLabel = "Delete"
searchField.accessibilityLabel = "Search"
```

## `accessibilityHint`

The `accessibilityHint` provides **additional context** about what happens when the user interacts with the element. It tells VoiceOver users the **result** of performing an action. VoiceOver reads the hint after a brief pause following the label, and users can disable hints in their VoiceOver settings.

**When to use it:**

- When the result of an action is not obvious from the label alone
- When extra context helps the user decide whether to activate the element
- When the element's behavior might be unexpected or needs clarification

**When NOT to use it:**

- When the action is already obvious from the label (e.g., a "Delete" button that deletes something does not need a hint saying "Deletes the item")
- Do not use it to duplicate or rephrase the label

**Guidelines:**

- Describe the result of the action, not the action itself
- Begin with a verb in third person (e.g., "Opens...", "Plays...", "Removes...")
- End with a period
- Keep it brief -- one sentence
- Localize it

**Examples:**

```swift
playButton.accessibilityLabel = "Play"
playButton.accessibilityHint = "Plays the current track."

favoriteButton.accessibilityLabel = "Favorite"
favoriteButton.accessibilityHint = "Adds this item to your favorites list."

sortButton.accessibilityLabel = "Sort"
sortButton.accessibilityHint = "Changes the order of the displayed results."
```

## Summary

| Aspect | `accessibilityLabel` | `accessibilityHint` |
|---|---|---|
| **Purpose** | Identifies **what** the element is | Describes the **result** of interacting |
| **Required?** | Yes, for all meaningful UI elements | No, only when the outcome is not obvious |
| **Read by VoiceOver** | Immediately | After a short delay; can be turned off by the user |
| **Tone** | Noun or short phrase (no period) | Sentence starting with a third-person verb (with period) |
| **Example** | "Play" | "Plays the selected podcast episode." |

A good rule of thumb: if the label alone makes it clear what will happen, skip the hint. If a user might wonder "what happens when I tap this?", add a hint.
