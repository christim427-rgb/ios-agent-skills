# Disabled Button with isAccessibilityElement = false Disappears from VoiceOver — Fix

## The Problem

Setting `isAccessibilityElement = false` removes the element entirely from the VoiceOver accessibility tree. This is the wrong approach for disabled controls. Users who rely on VoiceOver need to know that a button exists, that it is disabled, and ideally why — so they understand the context of the UI.

## Why It Matters

WCAG 1.3.1 (Info and Relationships) and 4.1.2 (Name, Role, Value) require that the state of controls be programmatically determinable. Hiding a disabled button from VoiceOver violates these criteria.

## Fix

Keep `isAccessibilityElement = true` (the default) and set the disabled trait instead:

### UIKit

```swift
button.isEnabled = false
button.isAccessibilityElement = true  // do NOT set to false
// UIAccessibility automatically adds the "dimmed" trait when isEnabled = false
// but you can also set it explicitly:
button.accessibilityTraits = [.button, .notEnabled]
```

### SwiftUI

```swift
Button("Save") { save() }
    .disabled(true)
// SwiftUI's .disabled() modifier automatically:
// - Prevents the action from firing
// - Adds the .notEnabled accessibility trait
// - Keeps the element in the accessibility tree
```

Do NOT add `.accessibilityHidden(true)` or set `.accessibilityElement(children: .ignore)` on disabled controls.

## Optional: Explain Why It's Disabled

Providing a hint improves the user experience significantly:

```swift
Button("Save") { save() }
    .disabled(!formIsValid)
    .accessibilityHint(formIsValid ? "" : "Fill in all required fields to enable saving")
```

## Summary

| Approach | VoiceOver behavior | Correct? |
|---|---|---|
| `isAccessibilityElement = false` | Element hidden | No |
| `.accessibilityHidden(true)` | Element hidden | No |
| `isEnabled = false` (default) | Announced as "dimmed" | Yes |
| `.disabled(true)` in SwiftUI | Announced correctly | Yes |
| Add `.notEnabled` trait | Announced as not enabled | Yes |
