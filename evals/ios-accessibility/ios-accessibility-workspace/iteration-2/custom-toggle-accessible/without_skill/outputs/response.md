# Make Custom Toggle (Text + Circle + onTapGesture) Accessible for VoiceOver

## Starting Point (Inaccessible)

```swift
HStack {
    Text("Enable notifications")
    Spacer()
    Circle()
        .fill(isOn ? Color.green : Color.gray)
        .frame(width: 28, height: 28)
}
.onTapGesture { isOn.toggle() }
```

Problems: no label, no toggle trait, no value announcement, individual elements are separately focusable by VoiceOver.

## Fixed Version

```swift
HStack {
    Text("Enable notifications")
    Spacer()
    Circle()
        .fill(isOn ? Color.green : Color.gray)
        .frame(width: 28, height: 28)
}
.onTapGesture { isOn.toggle() }
.accessibilityElement(children: .ignore)          // merge children into one element
.accessibilityLabel("Enable notifications")        // clear label
.accessibilityValue(isOn ? "On" : "Off")          // current state
.accessibilityAddTraits(.isButton)                // interactive trait
.accessibilityHint("Double-tap to toggle")        // optional but helpful
.accessibilityAction {                            // explicit action for VoiceOver double-tap
    isOn.toggle()
}
```

## Better: Use Toggle with Custom Appearance

The most robust approach is to use SwiftUI's built-in `Toggle` with a custom style. This gives you full control over appearance while retaining all semantic behavior:

```swift
struct CircleToggleStyle: ToggleStyle {
    func makeBody(configuration: Configuration) -> some View {
        HStack {
            configuration.label
            Spacer()
            Circle()
                .fill(configuration.isOn ? Color.green : Color.gray)
                .frame(width: 28, height: 28)
                .onTapGesture { configuration.$isOn.wrappedValue.toggle() }
        }
    }
}

// Usage:
Toggle("Enable notifications", isOn: $isOn)
    .toggleStyle(CircleToggleStyle())
```

`Toggle` automatically announces label, value ("on"/"off"), and the toggle trait — no extra accessibility modifiers needed.

## Key Accessibility Modifiers Explained

| Modifier | Purpose |
|---|---|
| `.accessibilityElement(children: .ignore)` | Collapses HStack children into a single VoiceOver element |
| `.accessibilityLabel(_:)` | What VoiceOver reads as the control name |
| `.accessibilityValue(_:)` | Current state ("On" / "Off") |
| `.accessibilityAddTraits(.isButton)` | Tells VoiceOver this is interactive |
| `.accessibilityAction { }` | Handles double-tap activation |
