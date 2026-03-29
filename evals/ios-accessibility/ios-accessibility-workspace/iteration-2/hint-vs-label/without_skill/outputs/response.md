## `accessibilityHint` vs `accessibilityLabel` — When to Use Each

### `accessibilityLabel`

**What it is:** The primary name of the element. VoiceOver reads it every time the user focuses the element.

**Rule:** Concisely identifies **what** the element is or represents. Should make sense without any context.

```swift
Button(action: deleteMessage) {
    Image(systemName: "trash")
}
.accessibilityLabel("Delete message")
```

- Keep it short (1–4 words where possible).
- Do not include the role (VoiceOver appends "button" automatically).
- Use action-oriented language for buttons ("Add to cart", not "Shopping cart icon").
- Must be present on every interactive element.

---

### `accessibilityHint`

**What it is:** Additional context about **what will happen** when the user interacts with the element. VoiceOver reads it after a brief pause following the label and trait.

**Rule:** Describes the **result** of the action in a way that is not obvious from the label alone.

```swift
Button(action: deleteMessage) {
    Image(systemName: "trash")
}
.accessibilityLabel("Delete message")
.accessibilityHint("Moves this message to the Trash folder")
```

VoiceOver reads: _"Delete message, button. Moves this message to the Trash folder."_

---

### Key Differences

| Aspect | `accessibilityLabel` | `accessibilityHint` |
|--------|---------------------|---------------------|
| Purpose | Names / identifies the element | Explains the outcome of interaction |
| Required? | Yes, for all interactive elements | Optional |
| Read frequency | Every focus | After label, can be disabled by user |
| Length | Short (1–4 words) | One sentence, imperative voice |
| Voice setting | Always on | User can turn off hints in VoiceOver settings |

---

### When NOT to Use a Hint

- When the result is obvious from the label: `"Send"` does not need a hint saying "Sends the message."
- When the label already covers the action completely.
- Never put information that is **essential** to understanding the element in the hint — some users disable hints.

---

### Hint Writing Guidelines (Apple HIG)

- Begin with a **verb**: "Opens…", "Adds…", "Removes…", "Saves…"
- Do not start with "Tap to…" or "Double-tap to…" — VoiceOver already tells users how to activate elements.
- Use third-person present tense: "Opens the photo library."
- Keep it to one sentence.

```swift
// Good
.accessibilityHint("Opens your saved addresses")

// Bad — redundant instruction
.accessibilityHint("Double-tap to open your saved addresses")

// Bad — too vague
.accessibilityHint("Does something with addresses")
```
