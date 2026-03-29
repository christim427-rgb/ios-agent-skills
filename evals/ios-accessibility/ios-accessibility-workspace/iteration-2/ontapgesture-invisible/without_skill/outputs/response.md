# Accessibility Issue with Image(systemName: "plus").onTapGesture { addItem() }

## Problems

### 1. No Accessibility Label
`Image(systemName:)` in SwiftUI does attempt to derive a label from the SF Symbol name (e.g., "plus" becomes "Add"), but this is not always accurate or meaningful in context. VoiceOver might announce "plus" rather than something actionable like "Add item."

### 2. No Accessibility Trait
The view has no `.button` trait. VoiceOver will not announce it as interactive. Users will not know they can activate it.

### 3. Tap Gesture vs. Button Semantics
`onTapGesture` attaches a gesture recognizer but does not make the view a semantic button. VoiceOver users navigating by swipe will encounter it as a static image, not a control. It will also not respond correctly to double-tap activation in VoiceOver.

### 4. Hit Area May Be Too Small
A bare `Image` icon is typically 20–30 pt — smaller than Apple's recommended minimum 44×44 pt touch target.

## Fix

Replace with a `Button`, which provides all the correct semantics automatically:

```swift
Button(action: addItem) {
    Image(systemName: "plus")
        .frame(minWidth: 44, minHeight: 44) // ensure adequate hit area
}
.accessibilityLabel("Add item")
```

Or, if you must keep the `Image` + gesture pattern:

```swift
Image(systemName: "plus")
    .onTapGesture { addItem() }
    .accessibilityLabel("Add item")
    .accessibilityAddTraits(.isButton)
    .accessibilityAction { addItem() }  // lets VoiceOver double-tap activate it
    .frame(minWidth: 44, minHeight: 44)
    .contentShape(Rectangle())          // makes full frame tappable
```

## Why `Button` Is Preferred

- Automatically gets `.isButton` trait.
- Supports keyboard navigation (iPadOS, external keyboard).
- Supports Switch Control.
- Respects `buttonStyle` and focus rings.
- No extra accessibility modifiers needed.
