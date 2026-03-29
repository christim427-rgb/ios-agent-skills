# Making a Custom Toggle Accessible

## Starting Point — Inaccessible Custom Toggle

```swift
// ❌ Inaccessible — onTapGesture invisible to AT, no role, no value
HStack {
    Text("Notifications")
    Spacer()
    Circle()
        .fill(isOn ? Color.blue : Color.gray)
        .frame(width: 24, height: 24)
}
.onTapGesture { isOn.toggle() }
```

Problems:
1. `onTapGesture` is invisible to VoiceOver, Switch Control, and eye tracking
2. No accessibility trait — VoiceOver doesn't know this is a toggle
3. No accessibility value — VoiceOver cannot announce "On" or "Off"
4. Children are exposed separately — VoiceOver reads "Notifications" and "circle" individually

## Option 1: Replace with Native Toggle (Recommended)

The native `Toggle` solves all problems automatically:

```swift
// ✅ Preferred — fully accessible with zero extra modifiers
Toggle("Notifications", isOn: $isOn)
```

VoiceOver reads: "Notifications. Toggle button. On. Double-tap to toggle."

Customize appearance while keeping accessibility:

```swift
Toggle(isOn: $isOn) {
    Text("Notifications")
        .font(.body)
}
.toggleStyle(.switch)  // or a custom ToggleStyle
```

## Option 2: Accessible Custom Toggle with Button

When the visual design cannot use native Toggle, use `Button` with the correct traits and value:

```swift
// ✅ Accessible custom toggle
struct CustomToggleView: View {
    @Binding var isOn: Bool
    let label: String

    var body: some View {
        Button {
            isOn.toggle()
        } label: {
            HStack {
                Text(label)
                    .font(.body)
                    .foregroundStyle(.primary)
                Spacer()
                Circle()
                    .fill(isOn ? Color.blue : Color.gray)
                    .frame(width: 24, height: 24)
            }
        }
        // Group children into a single accessible element
        .accessibilityElement(children: .combine)
        // Declare this is a toggle (iOS 17+)
        .accessibilityAddTraits(.isToggle)
        // Announce current state
        .accessibilityValue(isOn ? "On" : "Off")
    }
}
```

VoiceOver reads: "Notifications. On. Toggle. Double-tap to toggle."

## Option 3: Using .accessibilityRepresentation

For even more control, represent the custom toggle as a native Toggle for assistive technology:

```swift
CustomCircleToggle(isOn: $isOn, label: label)
    .accessibilityRepresentation {
        Toggle(label, isOn: $isOn)
    }
```

## Why Each Modifier Is Needed

| Modifier | Purpose |
|---|---|
| `Button` instead of `onTapGesture` | Makes element visible to VoiceOver, Switch Control, Voice Control |
| `.accessibilityElement(children: .combine)` | Groups label text and visual indicator into one element |
| `.accessibilityAddTraits(.isToggle)` | VoiceOver announces "Toggle" so user knows it switches states |
| `.accessibilityValue("On"/"Off")` | Announces current state on focus and after activation |

## Without .isToggle (Before iOS 17)

On iOS 16 and earlier, `.isToggle` was not available. Use a button and manually provide the value; the "Toggle" role won't be announced but the element will still be functional:

```swift
.accessibilityAddTraits(.isButton)
.accessibilityValue(isOn ? "On" : "Off")
.accessibilityHint("Double-tap to toggle")
```

## Verification

After implementing, VoiceOver should announce (on focus):
> "Notifications. On. Toggle. Double-tap to toggle."

After activation:
> "Off." (state change announcement)
