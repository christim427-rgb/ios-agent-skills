# Disabled Controls Must Remain Visible to VoiceOver

## The Problem

Setting `isAccessibilityElement = false` on a disabled button removes it from the accessibility tree entirely. VoiceOver users have no way to discover that the control exists at all.

```swift
// ❌ CRITICAL — disabled button disappears from VoiceOver
let saveButton = UIButton(type: .system)
saveButton.setTitle("Save", for: .normal)
saveButton.isEnabled = false
saveButton.isAccessibilityElement = false  // WRONG — hides it completely
```

VoiceOver: silent — as if the button does not exist. The user cannot learn why the button is unavailable or what action it would perform when enabled.

## Why Users Need to Know Disabled Controls Exist

Accessibility guidelines require that disabled controls remain perceivable:

1. Users need to know a "Save" button exists so they understand what they need to fill in to enable it
2. Screen reader users navigating a form need to understand the complete set of available actions
3. The dimmed/unavailable state communicates context: "this action is possible, but not right now"

WCAG 1.3.1 (Info and Relationships) — all controls and their states must be communicable to assistive technology.

## The Fix — UIKit

Use the `.notEnabled` accessibility trait. VoiceOver announces "dimmed" to indicate the control is unavailable.

```swift
// ✅ Disabled button remains visible with .notEnabled trait
let saveButton = UIButton(type: .system)
saveButton.setTitle("Save", for: .normal)
saveButton.isEnabled = false
saveButton.isAccessibilityElement = true   // Always true for interactive controls
saveButton.accessibilityTraits.insert(.notEnabled)  // Announces as "dimmed"
```

VoiceOver reads: "Save. Button. Dimmed."

When the button becomes enabled, remove the trait:

```swift
// Re-enable: remove .notEnabled, restore enabled state
saveButton.isEnabled = true
saveButton.accessibilityTraits.remove(.notEnabled)
```

Use `.insert()` / `.remove()` — never assign directly (`=`), which destroys all other existing traits like `.isButton`.

## The Fix — SwiftUI

SwiftUI's `.disabled()` modifier automatically applies the `.notEnabled` trait. You do not need to add it manually.

```swift
// ✅ SwiftUI — .disabled() handles trait automatically
Button("Save") { saveAction() }
    .disabled(!isFormValid)
```

VoiceOver reads: "Save. Button. Dimmed."

Never hide a disabled control in SwiftUI either:

```swift
// ❌ Control disappears entirely
Button("Save") { saveAction() }
    .opacity(isFormValid ? 1.0 : 0.0)
    .accessibilityHidden(!isFormValid)

// ✅ Control remains visible with dimmed state
Button("Save") { saveAction() }
    .disabled(!isFormValid)
    .opacity(isFormValid ? 1.0 : 0.5)  // Visual hint, but AT still reads it
```

## Optional: Add a Hint Explaining Why

For better UX, add an accessibility hint explaining what is needed to enable the control:

```swift
Button("Save") { saveAction() }
    .disabled(!isFormValid)
    .accessibilityHint(isFormValid ? "" : "Complete all required fields to save")
```

VoiceOver reads: "Save. Button. Dimmed. Complete all required fields to save."

## Summary

| Approach | VoiceOver | Recommendation |
|---|---|---|
| `isAccessibilityElement = false` | Silent — element does not exist | Never do this for controls |
| `.accessibilityHidden(true)` | Silent — element does not exist | Never for controls |
| `.notEnabled` trait | "Dimmed" — element exists but unavailable | Correct pattern in UIKit |
| `.disabled()` in SwiftUI | "Dimmed" — automatic | Correct pattern in SwiftUI |
