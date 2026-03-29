# Making a Custom Toggle Accessible for VoiceOver

## Issues Found

### [CRITICAL] onTapGesture used instead of Button

**WCAG:** 4.1.2 Name, Role, Value | **HIG:** Accessibility — VoiceOver
**Issue:** The `Circle` view uses `.onTapGesture` for interaction. Views with `onTapGesture` are completely invisible to VoiceOver, Switch Control, and eye tracking — assistive technology users cannot discover or activate this control at all.
**VoiceOver Impact:** VoiceOver skips the circle entirely. The user hears only "Dark Mode" (the label text) with no way to toggle the setting.

### [CRITICAL] Custom control missing accessibility semantics

**WCAG:** 4.1.2 Name, Role, Value | **HIG:** Accessibility — Custom Controls
**Issue:** Even if the tap were fixed, the control expresses state only visually (blue vs. gray fill). VoiceOver has no label, no role (toggle), and no value (on/off) to announce.
**VoiceOver Impact:** User cannot tell what the control does, what its current state is, or that it is interactive.

---

## Fix

Replace the entire `HStack` with a SwiftUI `Toggle` using a custom label, or — if the circle appearance must be preserved — replace `onTapGesture` with a `Button` and add explicit accessibility modifiers.

### Option A — Preferred: Use SwiftUI Toggle (fully accessible by default)

SwiftUI `Toggle` automatically announces name, role ("toggle button"), and value ("on"/"off"). This is the simplest and most robust solution.

```swift
// ✅ Option A — Standard Toggle with custom label styling
Toggle(isOn: $isDarkMode) {
    Text("Dark Mode")
}
// VoiceOver reads: "Dark Mode. Toggle button. Off. Double-tap to toggle."
// (or "On" when enabled)
```

If the circle indicator must be shown alongside, render it as a decorative element hidden from VoiceOver:

```swift
// ✅ Option A with decorative circle preserved
Toggle(isOn: $isDarkMode) {
    HStack {
        Text("Dark Mode")
        Circle()
            .fill(isDarkMode ? Color.blue : Color.gray)
            .frame(width: 30, height: 30)
            .accessibilityHidden(true)  // Decorative — Toggle already conveys state
    }
}
// VoiceOver reads: "Dark Mode. Toggle button. Off. Double-tap to toggle."
```

### Option B — Custom appearance using Button with full accessibility modifiers

Use this if the Toggle chrome (the pill switch) cannot appear and only the circle must render.

```swift
// ✅ Option B — Button replacing onTapGesture, with explicit a11y modifiers
Button(action: { isDarkMode.toggle() }) {
    HStack {
        Text("Dark Mode")
        Circle()
            .fill(isDarkMode ? Color.blue : Color.gray)
            .frame(width: 30, height: 30)
    }
}
.accessibilityLabel("Dark Mode")
.accessibilityValue(isDarkMode ? "On" : "Off")
.accessibilityAddTraits(.isButton)
.accessibilityHint("Double-tap to toggle")
// VoiceOver reads: "Dark Mode. On. Button. Double-tap to toggle."
```

> Note: `.accessibilityAddTraits(.isButton)` is included for explicitness, though `Button` already carries the button trait. The key additions are `.accessibilityLabel` and `.accessibilityValue` so VoiceOver communicates both purpose and current state.

---

## Why Each Change Was Made

| Change | Reason |
|---|---|
| `onTapGesture` → `Button` | `onTapGesture` is invisible to VoiceOver, Switch Control, and visionOS eye tracking. `Button` registers as an interactive element with the correct role. |
| `.accessibilityLabel("Dark Mode")` | Without an explicit label, VoiceOver reads the raw text children, which may be inconsistent. An explicit label ensures a stable, coherent announcement. |
| `.accessibilityValue(isDarkMode ? "On" : "Off")` | State changes (on/off) must be communicated as an accessibility value, not only via color. This is the only way VoiceOver users learn the current state. |
| `.accessibilityHidden(true)` on circle (Option A) | The circle is a visual redundancy when the Toggle already communicates state. Hiding it prevents VoiceOver from announcing confusing color information ("circle"). |
| `Color.blue` / `Color.gray` kept as-is | Color alone must not be the sole state indicator (WCAG 1.4.1), which is satisfied here because VoiceOver now announces state in words. For full compliance also add a non-color visual differentiator (e.g., checkmark icon). |

---

## VoiceOver Verification

After applying Option A, confirm VoiceOver announces:

- Focus on control: **"Dark Mode. Toggle button. Off."** (when off)
- After double-tap: **"On"** (state change announcement)
- Focus again: **"Dark Mode. Toggle button. On."**

After applying Option B, confirm:

- Focus on control: **"Dark Mode. Off. Button."**
- After double-tap: **"On"** (state change announcement)
- Focus again: **"Dark Mode. On. Button."**

---

## Confidence Checklist

- [x] No `onTapGesture` on interactive elements — replaced with `Button` or `Toggle`
- [x] No hardcoded font sizes — `Text("Dark Mode")` uses default Dynamic Type body style
- [x] No hardcoded semantic colors — fill uses `Color.blue`/`Color.gray` for the decorative indicator only (acceptable); label text uses default foreground
- [x] Interactive control has `accessibilityLabel`
- [x] `accessibilityValue` communicates stateful on/off to VoiceOver
- [x] Decorative circle hidden from VoiceOver in Option A
- [x] Labels describe purpose ("Dark Mode"), not appearance
- [x] Labels do not include element type ("Dark Mode" not "Dark Mode toggle")
