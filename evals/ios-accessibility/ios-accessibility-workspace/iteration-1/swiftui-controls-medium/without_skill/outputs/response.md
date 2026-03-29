# Making a Custom Toggle Accessible for VoiceOver

## Problem

The original code uses a raw `Circle` shape with an `.onTapGesture` modifier to act as a toggle button. VoiceOver cannot understand this element because:

1. It has no accessibility label — VoiceOver will either skip it or announce something unhelpful like "circle".
2. It has no accessibility trait — VoiceOver does not know it is interactive or that it behaves like a button/toggle.
3. It has no accessibility value — VoiceOver cannot tell users whether the toggle is on or off.
4. `.onTapGesture` is not recognized as an interactive action by the accessibility system.

---

## Solution

Apply a combination of accessibility modifiers to the `Circle` (or the wrapping `HStack`) so that VoiceOver treats it as a proper toggle control.

```swift
HStack {
    Text("Dark Mode")
    Circle()
        .fill(isDarkMode ? .blue : .gray)
        .frame(width: 30, height: 30)
        .onTapGesture { isDarkMode.toggle() }
        .accessibilityLabel("Dark Mode")
        .accessibilityValue(isDarkMode ? "On" : "Off")
        .accessibilityAddTraits(.isButton)
        .accessibilityHint("Double-tap to toggle")
}
```

### What each modifier does

| Modifier | Purpose |
|---|---|
| `.accessibilityLabel("Dark Mode")` | Gives VoiceOver a meaningful name to read aloud. Without this, VoiceOver may say "circle" or nothing at all. |
| `.accessibilityValue(isDarkMode ? "On" : "Off")` | Tells VoiceOver the current state of the toggle. VoiceOver will announce "Dark Mode, On" or "Dark Mode, Off". |
| `.accessibilityAddTraits(.isButton)` | Marks the element as interactive. VoiceOver announces it as a button and enables double-tap activation. |
| `.accessibilityHint("Double-tap to toggle")` | Optional but helpful — tells the user what will happen when they activate the element. |

---

## Alternative: Use the native SwiftUI Toggle

If the visual design allows it, the cleanest and most accessible solution is to use the built-in `Toggle`, which handles all accessibility automatically:

```swift
Toggle("Dark Mode", isOn: $isDarkMode)
```

SwiftUI's `Toggle` automatically provides:
- The correct label
- On/Off state announcements
- The `.isButton` and `.isSelected` traits
- Full Switch Control support

---

## Alternative: Combine into a single accessible element

If you want VoiceOver to treat the entire `HStack` (label + circle) as one focusable unit rather than two separate elements, use `.accessibilityElement(children: .combine)` or configure the HStack directly:

```swift
HStack {
    Text("Dark Mode")
    Circle()
        .fill(isDarkMode ? .blue : .gray)
        .frame(width: 30, height: 30)
}
.onTapGesture { isDarkMode.toggle() }
.accessibilityElement(children: .ignore)
.accessibilityLabel("Dark Mode")
.accessibilityValue(isDarkMode ? "On" : "Off")
.accessibilityAddTraits(.isButton)
.accessibilityHint("Double-tap to toggle")
```

This approach merges the text and the circle into a single VoiceOver focus target, which is often a better user experience for compound controls like this.

---

## Key Accessibility Checklist for Custom Interactive Controls

- [ ] Every interactive element must have an `.accessibilityLabel`
- [ ] Stateful controls must expose their current state via `.accessibilityValue` or `.accessibilityAddTraits(.isSelected)`
- [ ] Interactive elements must carry `.isButton` (or another appropriate trait) so VoiceOver knows they can be activated
- [ ] Avoid relying solely on color to convey state (important for color-blind users — the blue/gray distinction alone is insufficient)
- [ ] Test with VoiceOver enabled on a real device or the simulator to verify announcements
