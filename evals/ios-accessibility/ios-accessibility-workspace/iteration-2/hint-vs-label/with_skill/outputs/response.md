# `accessibilityHint` vs `accessibilityLabel`: When to Use Each

## The Fundamental Distinction

| Property | Answers | Timing | Example |
|---|---|---|---|
| `accessibilityLabel` | **What is this?** | Read immediately when focused | "Add to favorites" |
| `accessibilityHint` | **What will happen?** | Read after a short delay | "Adds this item to your saved list" |

The **label** identifies the element. The **hint** describes the result of activating it.

---

## `accessibilityLabel` Rules

The label is the element's name. It must be:
- **Short and purposeful** — describes what the control does, not what it looks like
- **Unique in context** — differentiates identical controls (e.g., multiple "Delete" buttons)
- **Updated on state change** — if the action changes when toggled, so should the label
- **Free of element type** — VoiceOver adds "button", "toggle", etc. from the trait; don't repeat it in the label

```swift
// ❌ Label describes appearance
Image(systemName: "heart.fill")
    .accessibilityLabel("Red heart icon")

// ❌ Label includes element type
Button("Delete item") { }
    .accessibilityLabel("Delete button")

// ✅ Label describes purpose
Button(action: toggleFavorite) {
    Image(systemName: isFavorited ? "heart.fill" : "heart")
}
.accessibilityLabel(isFavorited ? "Remove from favorites" : "Add to favorites")
// VoiceOver: "Add to favorites, button" — type added automatically
```

---

## `accessibilityHint` Rules

Hints provide supplemental context when the label alone isn't enough to describe the result. The VoiceOver user hears the label first, pauses, then (after a delay) hears the hint.

### Rules for Writing Hints

1. **Begin with a verb in third person** — "Opens...", "Saves...", "Deletes...", "Marks..."
2. **Describe the result** — not the gesture, not the label
3. **Only add when necessary** — if the label already makes the result obvious, a hint is noise
4. **Never repeat the label** — redundant hints frustrate users who have hints enabled

```swift
// ❌ Redundant — repeats the label
Button("Delete")
    .accessibilityHint("Deletes this item")

// ❌ Describes gesture, not result
Button("Archive")
    .accessibilityHint("Swipe or double-tap to archive")

// ❌ Describes action instead of result
Button("Share")
    .accessibilityHint("Tap to share")  // This is what ALL buttons do — useless

// ✅ Describes result when it isn't obvious from label alone
Button("Archive")
    .accessibilityHint("Moves the message out of your inbox")

// ✅ Clarifies destructive consequence
Button("Delete Account")
    .accessibilityHint("Permanently removes your account and all associated data")

// ✅ No hint needed — label is self-explanatory
Button("Sign Out") { }
// The result is obvious — don't add a hint
```

---

## Decision Tree: Do I Need a Hint?

```
Is the action result already obvious from the label?
├── YES → Do NOT add a hint (e.g., "Sign Out", "Cancel", "Save")
└── NO  → Would a hint clarify the consequence?
    ├── YES → Add a hint beginning with a verb describing the result
    └── Is the consequence non-obvious or potentially destructive?
        ├── YES → Hint is strongly recommended
        └── NO  → Hint is optional — use judgment
```

---

## VoiceOver Announcement Timeline

```
[Focus on element]
→ Immediately: "Add to favorites, button"
→ After short delay: "Adds this song to your favorites playlist"
                      ↑ this is the hint
```

Users can disable hints in VoiceOver settings (Settings → Accessibility → VoiceOver → Verbosity → Hints). Well-written labels ensure the app is usable even with hints off.

---

## Common Mistakes

| Mistake | Why It's Wrong |
|---|---|
| `hint: "Tap to delete"` | Describes gesture, not result; also, ALL buttons require a tap — this is noise |
| `hint: "This is the delete button"` | Repeats role information VoiceOver already provides |
| `hint: "Deletes"` | Doesn't begin with a verb in third-person form describing the full result |
| Long multi-sentence hint | Hints should be one sentence; longer hints are ignored before they finish |
| Hint when label is self-explanatory | Adds delay and noise for users who have hints enabled |

---

## Summary

- **Label** = the name (required for every interactive element)
- **Hint** = the consequence (optional, only when the label isn't enough)
- Begin hints with a third-person verb: "Opens", "Saves", "Removes", "Sends"
- Hints describe **results**, not gestures or appearances
- Warn of destructive consequences in hints when appropriate
- Do not add hints just because you can — they add cognitive load
