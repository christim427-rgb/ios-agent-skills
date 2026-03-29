## Fixing a Color-Only Status Indicator for Colorblind Users

### The Problem

`Circle().fill(isOnline ? .green : .red)` conveys status **solely through color**. This violates WCAG 2.1 Success Criterion 1.4.1 (Use of Color): "Color is not used as the only visual means of conveying information."

Users with deuteranopia or protanopia (red-green color blindness, affecting ~8% of males) see both colors as a similar muddy brown/yellow and cannot distinguish the states.

---

### Fix 1: Add a Shape Difference (Pattern/Form)

Use different shapes or fills for each state so the difference is perceivable without color:

```swift
Group {
    if isOnline {
        Circle()
            .fill(Color.green)
    } else {
        Circle()
            .strokeBorder(Color.red, lineWidth: 2)
            // hollow vs filled — perceivable without color
    }
}
.frame(width: 12, height: 12)
```

---

### Fix 2: Add a Text Label

The simplest, most robust fix:

```swift
HStack(spacing: 4) {
    Circle()
        .fill(isOnline ? Color.green : Color.red)
        .frame(width: 10, height: 10)
    Text(isOnline ? "Online" : "Offline")
        .font(.caption)
}
```

Text is the most universally accessible solution and works for colorblind, VoiceOver, and high-contrast users.

---

### Fix 3: Use System Symbols with Inherent Meaning

SF Symbols carry semantic meaning independent of color:

```swift
Image(systemName: isOnline ? "wifi" : "wifi.slash")
    .foregroundColor(isOnline ? .green : .red)
```

Or for an online/offline indicator:

```swift
Image(systemName: isOnline ? "circle.fill" : "circle.slash")
    .foregroundColor(isOnline ? .green : .red)
```

The shape difference (filled circle vs slashed circle) conveys the state without relying on color.

---

### Fix 4: `accessibilityDifferentiateWithoutColor` Environment Variable

Respect the system setting "Differentiate Without Color" (Settings → Accessibility → Display & Text Size):

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

var body: some View {
    ZStack {
        Circle()
            .fill(isOnline ? Color.green : Color.red)
        if differentiateWithoutColor {
            // Add non-color indicator when setting is on
            if !isOnline {
                Image(systemName: "xmark")
                    .font(.system(size: 6, weight: .bold))
                    .foregroundColor(.white)
            }
        }
    }
    .frame(width: 14, height: 14)
}
```

---

### Fix 5: VoiceOver Label

Regardless of the visual fix, add an accessibility label so VoiceOver users know the state:

```swift
Circle()
    .fill(isOnline ? Color.green : Color.red)
    .frame(width: 12, height: 12)
    .accessibilityLabel(isOnline ? "Online" : "Offline")
```

---

### Recommended Combined Solution

```swift
HStack(spacing: 6) {
    Circle()
        .fill(isOnline ? Color.green : Color.red)
        .frame(width: 10, height: 10)
        .accessibilityHidden(true)  // label is on the HStack
    Text(isOnline ? "Online" : "Offline")
        .font(.caption)
        .foregroundColor(.secondary)
}
.accessibilityElement(children: .combine)
.accessibilityLabel(isOnline ? "Status: Online" : "Status: Offline")
```

This approach satisfies:
- WCAG 1.4.1 (Use of Color) — text label provides non-color indicator
- VoiceOver — explicit accessibility label
- Colorblind users — text is unambiguous
