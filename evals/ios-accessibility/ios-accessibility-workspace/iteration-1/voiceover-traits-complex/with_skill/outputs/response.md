# Accessible Rating Stepper with VoiceOver Adjustable Support

Your current `RatingStepper` has several accessibility issues. Here is the analysis and the corrected implementation.

## Issues in the Original Code

### 1. CRITICAL -- `onTapGesture` on Interactive Elements

Each star `Image` uses `.onTapGesture`, which is invisible to VoiceOver, Switch Control, and Full Keyboard Access. VoiceOver users cannot activate any of the stars. This is AI failure pattern F1.

### 2. CRITICAL -- No Accessibility on Custom Control

The `HStack` of stars has no `accessibilityLabel`, no `accessibilityValue`, no traits, and no adjustable action. VoiceOver reads each star as a separate, unlabeled image. This is AI failure pattern F7.

### 3. CRITICAL -- No Adjustable Trait or Increment/Decrement

You asked for swipe up/down adjustment. This requires the `.adjustable` trait combined with `.accessibilityAdjustableAction`. Without it, VoiceOver has no mechanism to let users change the value by swiping.

### 4. MEDIUM -- No Grouping

The five star images are five separate VoiceOver stops. A rating control is a single conceptual element and should be grouped into one.

### 5. HIGH -- No `accessibilityValue`

Without `.accessibilityValue`, VoiceOver cannot announce the current rating when the user lands on the control or adjusts it.

## Corrected Implementation

```swift
struct RatingStepper: View {
    @Binding var rating: Int

    private let range = 1...5

    var body: some View {
        HStack {
            ForEach(range, id: \.self) { i in
                Image(systemName: i <= rating ? "star.fill" : "star")
                    .foregroundStyle(i <= rating ? .yellow : .secondary)
            }
        }
        // Group all stars into a single accessibility element
        .accessibilityElement(children: .ignore)
        // Label describes purpose, not appearance (no "stars" type info)
        .accessibilityLabel("Rating")
        // Value tells VoiceOver the current state
        .accessibilityValue("\(rating) out of \(range.upperBound)")
        // Adjustable trait enables swipe up/down gestures
        .accessibilityAdjustableAction { direction in
            switch direction {
            case .increment:
                rating = min(rating + 1, range.upperBound)
            case .decrement:
                rating = max(rating - 1, range.lowerBound)
            @unknown default:
                break
            }
        }
        .accessibilityHint("Swipe up or down to adjust")
    }
}
```

## How It Works with VoiceOver

1. **User swipes to the control.** VoiceOver announces: *"Rating, 3 out of 5, adjustable. Swipe up or down to adjust."*
2. **User swipes up.** Rating increments to 4. VoiceOver announces: *"4 out of 5."*
3. **User swipes down.** Rating decrements to 3. VoiceOver announces: *"3 out of 5."*
4. The value is clamped to 1-5 so it never goes out of range.

## Why Each Modifier Matters

| Modifier | Purpose | What Happens Without It |
|---|---|---|
| `.accessibilityElement(children: .ignore)` | Groups five stars into one VoiceOver stop | User must swipe through 5 separate unlabeled images |
| `.accessibilityLabel("Rating")` | Identifies the control by purpose | VoiceOver reads nothing or raw SF Symbol names |
| `.accessibilityValue("\(rating) out of \(range.upperBound)")` | Announces current state | User has no idea what the current rating is |
| `.accessibilityAdjustableAction` | Adds `.adjustable` trait and handles swipe up/down | No swipe-to-adjust; user cannot change the value at all |
| `.accessibilityHint(...)` | Tells user how to interact | Experienced VoiceOver users may know, but new users will not |

## Key Points

- `.accessibilityAdjustableAction` automatically adds the `.adjustable` trait -- you do not need to add it separately.
- The `@unknown default` case in the switch handles future `AccessibilityAdjustmentDirection` values without a compiler warning.
- The label says "Rating", not "Rating stepper" or "Star rating button" -- VoiceOver adds "adjustable" from the trait automatically.
- Clamping with `min`/`max` prevents the value from going below 1 or above 5 on repeated swipes.
- The `.foregroundStyle(.yellow)` uses semantic styling rather than a hardcoded color, and `.secondary` adapts to light/dark mode automatically.

## WCAG Mapping

- **WCAG 4.1.2 Name, Role, Value** -- The control now exposes its name (label), role (adjustable), and value to assistive technology.
- **WCAG 1.3.1 Info and Relationships** -- Grouping conveys that the stars are a single control, not five independent elements.
- **WCAG 2.1.1 Keyboard** -- The adjustable action provides a non-touch mechanism for changing the value, which also supports Switch Control and Full Keyboard Access.
