# Color-Only Status Indicator: `Circle().fill(isOnline ? .green : .red)`

## Severity: 🟡 HIGH — WCAG 1.4.1 Use of Color

A colored circle is a **color-only** status indicator. Approximately 8% of men and 0.5% of women have some form of color vision deficiency. The most common form is red-green color blindness (deuteranopia/protanopia) — the exact combination used here.

For these users, a green circle and a red circle look identical or nearly identical. They have no way to determine whether a contact is online or offline.

This also fails VoiceOver entirely — a `Circle` with no label is announced as nothing meaningful, or skipped.

---

## The Fix: Add Shape + Text Alongside Color

The correct approach communicates status through **multiple channels simultaneously**: color, shape/icon, and text.

```swift
// ❌ Color only — fails for colorblind users and VoiceOver
Circle()
    .fill(isOnline ? .green : .red)
    .frame(width: 12, height: 12)

// ✅ Color + shape/icon + text — works for everyone
HStack(spacing: 6) {
    Image(systemName: isOnline ? "checkmark.circle.fill" : "xmark.circle.fill")
        .foregroundStyle(isOnline ? .green : .red)
    Text(isOnline ? "Online" : "Offline")
        .font(.caption)
        .foregroundStyle(.secondary)
}
```

**VoiceOver reads:** "Online" or "Offline" — unambiguous regardless of color perception.

**For colorblind users (sighted):** The checkmark vs. X shape communicates status independent of color.

---

## With `accessibilityDifferentiateWithoutColor`

The system setting **Settings → Accessibility → Display & Text Size → Differentiate Without Color** signals that a user relies on shape/text rather than color. Check this environment value and enhance your indicator accordingly:

```swift
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor

var body: some View {
    HStack(spacing: 6) {
        if differentiateWithoutColor {
            // When differentiate is on: use shape exclusively; don't rely on color at all
            Image(systemName: isOnline ? "checkmark.circle.fill" : "xmark.circle.fill")
                .foregroundStyle(.primary)  // No color distinction — shape carries meaning
        } else {
            // Default: use shape + color
            Image(systemName: isOnline ? "circle.fill" : "circle")
                .foregroundStyle(isOnline ? .green : .red)
        }

        Text(isOnline ? "Online" : "Offline")
            .font(.caption)
            .foregroundStyle(.secondary)
    }
}
```

---

## Compact Indicator (Inline Badge)

When the indicator must be compact (e.g., an avatar badge), use shape + VoiceOver label:

```swift
struct OnlineStatusBadge: View {
    let isOnline: Bool

    @Environment(\.accessibilityDifferentiateWithoutColor) var diffWithoutColor

    var body: some View {
        ZStack {
            // Background ring for contrast
            Circle()
                .fill(Color(.systemBackground))
                .frame(width: 14, height: 14)

            Circle()
                .fill(statusColor)
                .frame(width: 10, height: 10)

            // When differentiating without color, overlay a shape mark
            if diffWithoutColor {
                Image(systemName: isOnline ? "checkmark" : "xmark")
                    .font(.system(size: 6, weight: .bold))
                    .foregroundStyle(.white)
            }
        }
        // Single accessibility label for the badge
        .accessibilityLabel(isOnline ? "Online" : "Offline")
    }

    private var statusColor: Color {
        isOnline ? .green : .red
    }
}
```

---

## For VoiceOver Specifically

If the status indicator is part of a larger group (e.g., a contact card), hide the individual badge and include status in the card's combined label:

```swift
struct ContactCard: View {
    let name: String
    let isOnline: Bool

    var body: some View {
        HStack {
            // Avatar with online badge
            ZStack(alignment: .bottomTrailing) {
                AvatarView(name: name)
                OnlineStatusBadge(isOnline: isOnline)
                    .accessibilityHidden(true)  // Hidden — status is in the group label
            }

            Text(name)
                .font(.headline)
        }
        // Group with combined label including status
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("\(name), \(isOnline ? "online" : "offline")")
    }
}
```

**VoiceOver reads:** "Jane Smith, online"

---

## WCAG Criteria

| Criterion | Requirement | This Fix |
|---|---|---|
| 1.4.1 Use of Color (AA) | Color must not be the sole way to convey information | Shape + text added alongside color |
| 1.1.1 Non-text Content (AA) | Non-text content has text alternative | `.accessibilityLabel` added |
| 1.4.11 Non-text Contrast (AA) | UI components have 3:1 contrast ratio | Green/red circles on white — typically pass; verify with contrast checker |

---

## Summary

Never use color as the sole indicator of state. Always pair color with at least one of:
- A **shape** that changes (checkmark vs. X, filled vs. outline)
- **Text** that states the status explicitly
- An **accessibility label** that VoiceOver reads

Check `accessibilityDifferentiateWithoutColor` and enhance the non-color channel when it's enabled.
