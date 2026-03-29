# `accessibilityLabel` vs `accessibilityHint` -- When to Use Each

These two modifiers serve fundamentally different purposes in VoiceOver, and understanding the distinction is critical for a good experience.

## `accessibilityLabel` -- What the element IS

The label is the **identity** of the element. VoiceOver reads it immediately when the user focuses on an element. It answers: "What is this?"

**Rules for labels:**

| Rule | Bad | Good |
|---|---|---|
| Don't include the element type | `"Play button"` | `"Play"` (VoiceOver adds "button" from the trait automatically) |
| Don't describe appearance | `"Red warning triangle"` | `"Warning"` |
| Keep it short | `"Press this button to add item to your cart"` | `"Add to cart"` |
| No image filenames | `"plus_icon_outline_#999"` | `"Add"` |
| Update when state changes | Static `"Add"` | `"Add"` / `"Remove"` (toggled based on state) |
| Provide context for identical actions | `"Add"` (which item?) | `"Add peanut butter"` |
| Capitalize naturally | `"ADD TO CART"` | `"Add to cart"` |

Every interactive element and every meaningful image **must** have a label. This is non-negotiable.

## `accessibilityHint` -- What the element DOES

The hint describes the **result** of activating the element. VoiceOver reads it **after a short delay**, and users can disable hints entirely in Settings. It answers: "What will happen if I activate this?"

**Rules for hints:**

- Begin with a third-person verb ("Opens...", "Removes...", "Navigates to...")
- Describe the **result**, not the gesture
- Only add one when the label alone is not sufficient to understand the consequence

## When You Need a Hint (and When You Don't)

**You DO NOT need a hint when the label is self-explanatory:**

```swift
// No hint needed -- "Sign Out" is unambiguous
Button("Sign Out") { ... }

// No hint needed -- "Add to cart" clearly describes the result
Button("Add to cart") { ... }
```

**You DO need a hint when the action has a non-obvious consequence:**

```swift
// "Delete" is clear, but WHAT happens isn't obvious
Button("Delete")
    .accessibilityHint("Permanently removes this message")

// "More" tells you nothing about the result
Button("More")
    .accessibilityHint("Opens additional sharing options")
```

## Common Mistakes

### Redundant hints that repeat the label

```swift
// BAD -- the hint just restates what the label already says
Button("Delete")
    .accessibilityHint("Tap to delete")

// GOOD -- the hint adds NEW information about the consequence
Button("Delete")
    .accessibilityHint("Permanently removes this message")
```

### Hints that describe the gesture instead of the result

```swift
// BAD -- describes the gesture
Button("Delete")
    .accessibilityHint("Double tap this button")

// GOOD -- describes the result
Button("Delete")
    .accessibilityHint("Permanently removes this message")
```

### Confusing `accessibilityIdentifier` with `accessibilityLabel`

This is a separate but related pitfall. `accessibilityIdentifier` is for **UI testing only** and is invisible to VoiceOver. Never use it as a substitute for `accessibilityLabel`:

```swift
// BAD -- user hears nothing useful; identifier is for tests only
Image(systemName: "trash")
    .accessibilityIdentifier("deleteButton")

// GOOD -- user hears "Delete, button"
Image(systemName: "trash")
    .accessibilityLabel("Delete")
```

## What VoiceOver Actually Reads

When a user focuses on an element, VoiceOver reads in this order:

1. **Label** (immediately)
2. **Value** (if present, e.g., "50%" on a slider)
3. **Traits** (e.g., "button", "heading", "dimmed")
4. **Hint** (after a pause, if enabled by the user)

So for this code:

```swift
Button("Delete")
    .accessibilityHint("Permanently removes this message")
```

VoiceOver reads: **"Delete. Button."** ... *(pause)* ... **"Permanently removes this message."**

## Summary

| Property | Purpose | When Read | Required? |
|---|---|---|---|
| `accessibilityLabel` | Identity -- what the element is | Immediately on focus | Yes, always on interactive elements and meaningful images |
| `accessibilityHint` | Consequence -- what happens on activation | After a delay (user can disable) | Only when the label alone does not convey the result |

The rule of thumb: if you removed the hint entirely and a VoiceOver user could still understand and use the control correctly, you do not need the hint. If the consequence of activation is surprising, destructive, or non-obvious from the label, add a hint.
