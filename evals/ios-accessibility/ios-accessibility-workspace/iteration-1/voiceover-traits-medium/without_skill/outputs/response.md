# VoiceOver Stops Announcing "Button" After Setting `.selected`

## The Problem

When you write:

```swift
myToggle.accessibilityTraits = .selected
```

You are **replacing** the entire traits bitmask, not adding to it. The `=` operator overwrites whatever traits were previously set. If your control previously had `.button` (which UIKit buttons get by default), that trait is now gone -- the only trait left is `.selected`. VoiceOver reads traits to determine the element's role, so it no longer announces "button" because that trait no longer exists.

## The Fix

Use `.insert()` to add the `.selected` trait while preserving existing ones:

```swift
myToggle.accessibilityTraits.insert(.selected)
```

Or equivalently, use a union:

```swift
myToggle.accessibilityTraits = [.button, .selected]
```

To remove the selected state later (e.g., when the user toggles it off):

```swift
myToggle.accessibilityTraits.remove(.selected)
```

## Why This Happens

`UIAccessibilityTraits` is an `OptionSet` (a bitmask). Each trait is a single bit. Assigning with `=` replaces the entire set of bits. Common default traits that UIKit assigns automatically include:

- `.button` for `UIButton`
- `.image` for `UIImageView`
- `.staticText` for `UILabel`
- `.header` for labels used as section headers

When you assign `.selected` directly, all of these defaults are wiped out.

## Recommended Pattern for Custom Toggles

For a toggle-style control, the idiomatic approach is:

```swift
// Initial setup -- make sure .button is present
myToggle.accessibilityTraits = [.button]

// When toggled on
myToggle.accessibilityTraits.insert(.selected)
myToggle.accessibilityValue = "on"

// When toggled off
myToggle.accessibilityTraits.remove(.selected)
myToggle.accessibilityValue = "off"
```

Setting `accessibilityValue` to "on"/"off" gives VoiceOver users an additional audible cue about the current state. With this setup, VoiceOver will announce something like: "MyToggle, on, selected, button" -- giving the user full context about what the element is and its current state.

## Summary

| Approach | Result |
|---|---|
| `traits = .selected` | Replaces all traits; loses `.button` |
| `traits.insert(.selected)` | Adds `.selected` while keeping `.button` and any other existing traits |
| `traits = [.button, .selected]` | Explicitly sets both traits |
