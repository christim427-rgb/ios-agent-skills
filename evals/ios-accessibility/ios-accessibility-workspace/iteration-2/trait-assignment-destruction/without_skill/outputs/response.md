## Why `myToggle.accessibilityTraits = .selected` Removes "button"

### Root Cause: Assignment Replaces All Traits

The `=` operator on `accessibilityTraits` is a **full replacement**, not an addition. It discards every trait the view previously had — including the `.button` trait that UIKit automatically sets on `UIButton` and interactive controls — and replaces the entire set with only `.selected`.

```swift
// This REPLACES all traits with just .selected
myToggle.accessibilityTraits = .selected   // ❌
```

Since `.button` is no longer in the trait set, VoiceOver no longer announces "button", and the element may also lose its activatable behaviour.

### Fix: Use `insert(_:)` to Add Traits Additively

```swift
// Preserves existing traits, adds .selected on top
myToggle.accessibilityTraits.insert(.selected)  // ✅
```

To remove it again when deselected:

```swift
myToggle.accessibilityTraits.remove(.selected)
```

### For a Toggle / On–Off State

For a control that switches between on and off, `.selected` is not the right trait. Use the correct semantic traits instead:

```swift
// Better approach for toggle state
myToggle.accessibilityTraits = [.button, .selected]   // when ON
myToggle.accessibilityTraits = .button                 // when OFF
```

Or use `accessibilityValue` to convey state without altering traits:

```swift
myToggle.accessibilityValue = isOn ? "on" : "off"
```

VoiceOver then reads: _"Notifications, button, on"_ — which is the correct pattern matching how `UISwitch` behaves natively.

### SwiftUI Equivalent

In SwiftUI, `.accessibilityAddTraits()` is always additive:

```swift
Toggle("Notifications", isOn: $isOn)
    .accessibilityAddTraits(isOn ? .isSelected : [])
```

### Summary

| Code | Effect |
|------|--------|
| `traits = .selected` | Replaces all traits — `.button` is lost |
| `traits.insert(.selected)` | Adds `.selected` — `.button` is preserved |
| `traits = [.button, .selected]` | Explicit set — both traits present |
