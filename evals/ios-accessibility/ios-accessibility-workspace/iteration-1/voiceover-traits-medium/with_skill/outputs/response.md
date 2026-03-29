## The Problem: Trait Assignment Destroys Existing Traits

This is a classic UIKit pitfall. When you write:

```swift
myToggle.accessibilityTraits = .selected
```

You are **replacing** the entire trait set with only `.selected`. Whatever traits the control had before -- `.button`, `.link`, `.adjustable`, or anything else -- are gone. VoiceOver uses the `.button` trait to announce "button" after the label, so once you overwrite it, VoiceOver no longer knows this element is a button. The user hears the label and "selected" but has no idea the element is interactive.

This is the `=` (assignment) vs `.insert()` distinction. Assignment is a full replacement. Insert is additive.

## The Fix: Use `.insert()` to Add Traits

```swift
// WRONG -- destroys all existing traits including .button
myToggle.accessibilityTraits = .selected

// CORRECT -- adds .selected while preserving .button and any other existing traits
myToggle.accessibilityTraits.insert(.selected)
```

When the toggle is deselected, remove the trait the same way:

```swift
myToggle.accessibilityTraits.remove(.selected)
```

With this fix, VoiceOver will announce something like: **"My Toggle, selected, button"** -- the user knows what the element is, that it is interactive, and what its current state is.

## Full Pattern for a Custom Toggle

Here is a complete pattern for managing selection state on a custom toggle in UIKit:

```swift
func updateToggleAccessibility(isSelected: Bool) {
    if isSelected {
        myToggle.accessibilityTraits.insert(.selected)
    } else {
        myToggle.accessibilityTraits.remove(.selected)
    }
}
```

Make sure the base traits are set up correctly when you first configure the control. If your custom toggle is a `UIControl` subclass, it already has `.button` by default. If it is a plain `UIView`, you need to set the initial traits explicitly:

```swift
// Initial setup (assignment is fine here because you're defining the full initial set)
myToggle.isAccessibilityElement = true
myToggle.accessibilityLabel = "Dark mode"
myToggle.accessibilityTraits = [.button]

// Later, when state changes -- always insert/remove
myToggle.accessibilityTraits.insert(.selected)
```

## When Assignment Is Safe

Assignment (`=`) is only safe when you are defining the **complete initial trait set** and you know exactly which traits should be present:

```swift
// OK at initial setup -- you're explicitly listing everything
myToggle.accessibilityTraits = [.button, .selected]
```

For any **state change** after setup, always use `.insert()` and `.remove()`. This ensures you never accidentally destroy traits that were added by UIKit, by a superclass, or by other parts of your code.

## VoiceOver Announcement Reference

| Code | VoiceOver Reads |
|---|---|
| `traits = .selected` | "My Toggle, selected" (no "button" -- user does not know it is tappable) |
| `traits.insert(.selected)` | "My Toggle, selected, button" (user knows it is tappable and currently selected) |
| `traits.remove(.selected)` | "My Toggle, button" (user knows it is tappable and not selected) |

## Also Consider: accessibilityValue

For a toggle, you can also communicate state through `accessibilityValue` instead of or in addition to the `.selected` trait. This gives you more control over the exact wording:

```swift
myToggle.accessibilityValue = isOn ? "On" : "Off"
```

VoiceOver would then read: **"Dark mode, On, button"** which can be clearer than "selected" depending on the context.
