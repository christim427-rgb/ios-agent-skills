# Accessibility Issues with `Image(systemName: "plus").onTapGesture`

## The Code

```swift
Image(systemName: "plus")
    .onTapGesture { addItem() }
```

## Issues

### 1. No Accessibility Label
`Image(systemName: "plus")` will be announced by VoiceOver as "plus" (the raw SF Symbol name). This is not descriptive enough for users to understand the purpose or action. It should convey the intent, such as "Add item".

### 2. Not a Proper Interactive Element
Using `.onTapGesture` on an `Image` does not register the view as an interactive button in the accessibility tree. VoiceOver users will not know the element is tappable. A proper `Button` communicates its role — VoiceOver announces it as "button" — and automatically supports keyboard navigation, Switch Control, and Full Keyboard Access.

### 3. No Accessibility Hint
There is no `.accessibilityHint` to describe what will happen when the element is activated (e.g., "Adds a new item to the list").

### 4. Missing Accessibility Trait
Without `.accessibilityAddTraits(.isButton)`, assistive technologies do not know this element is interactive, so Switch Control and Full Keyboard Access users may be unable to trigger the action at all.

## Recommended Fix

**Preferred approach — use `Button`:**

```swift
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

**Alternative — if keeping the tap gesture:**

```swift
Image(systemName: "plus")
    .onTapGesture { addItem() }
    .accessibilityLabel("Add item")
    .accessibilityAddTraits(.isButton)
```

Using `Button` is strongly preferred because it correctly conveys the interactive role and integrates natively with all assistive technologies (VoiceOver, Switch Control, Full Keyboard Access, Voice Control).
