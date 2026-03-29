# Accessibility Issues: `Image(systemName: "plus").onTapGesture { addItem() }`

## Issues Found

### [CRITICAL] Interactive element uses `onTapGesture` instead of `Button`

**WCAG:** 4.1.2 Name, Role, Value (Level A) | **HIG:** Buttons and Controls
**Issue:** `onTapGesture` is not a recognized interactive control. VoiceOver, Switch Control, Voice Control, and visionOS eye tracking all rely on the SwiftUI/UIKit accessibility element tree to discover interactive elements. Views with `onTapGesture` are plain `Image` views — they carry no button role, no activation semantic, and no focusable interactive element. The gesture handler is simply invisible to any assistive technology.
**VoiceOver Impact:** VoiceOver either skips this element entirely or reads it as a static image with no action available. The user has no way to activate "Add Item" with VoiceOver, Switch Control, or Full Keyboard Access.

**Fix:**
```swift
// ❌ Current — gesture invisible to all assistive technology
Image(systemName: "plus")
    .onTapGesture { addItem() }

// ✅ Corrected — Button provides role, focus, and activation for free
Button {
    addItem()
} label: {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

---

### [CRITICAL] No `accessibilityLabel` on icon-only button

**WCAG:** 1.1.1 Non-text Content (Level A) | **HIG:** Always label controls
**Issue:** Even after wrapping in `Button`, `Image(systemName: "plus")` has no text label. VoiceOver derives the accessible name from button content; for an SF Symbol image with no label, it reads the raw symbol name — in this case **"plus"** — which gives no meaningful context about the action. Users who rely on VoiceOver cannot tell whether this button adds an item, zooms in, creates a new record, or does something else entirely.
**VoiceOver Impact:** VoiceOver announces **"plus, button"** — a symbol name, not a description of the action.

**Fix:**
```swift
// ❌ Without label — VoiceOver reads "plus, button"
Button {
    addItem()
} label: {
    Image(systemName: "plus")
}

// ✅ With label — VoiceOver reads "Add item, button"
Button {
    addItem()
} label: {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

Note: do not include the word "button" in the label — VoiceOver appends the trait automatically. Say "Add item", not "Add item button".

---

## Summary

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | CRITICAL | `onTapGesture` used for interactive element | Replace with `Button` |
| 2 | CRITICAL | No `accessibilityLabel` on icon-only control | Add `.accessibilityLabel("Add item")` |

Both issues must be fixed together. Replacing `onTapGesture` with `Button` solves the role/focusability problem, and adding `accessibilityLabel` solves the naming problem. Neither fix alone is sufficient.

## Complete Corrected Code

```swift
Button {
    addItem()
} label: {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

**VoiceOver announces:** "Add item, button" — and users can double-tap to activate.
