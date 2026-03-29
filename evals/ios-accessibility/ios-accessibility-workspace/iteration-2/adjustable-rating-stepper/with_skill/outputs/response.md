# Accessible Custom Rating Stepper (1–5 Stars)

## Why `onTapGesture` Breaks Accessibility

`onTapGesture` is **invisible to VoiceOver, Switch Control, and eye tracking**. Users navigating without a finger on screen cannot interact with it at all. This is AI failure pattern F1 — the most common accessibility bug in generated SwiftUI code.

Additionally, individual tappable star images force VoiceOver users to swipe through 5 separate elements, with no indication of the current value or how to change it.

---

## The Correct Pattern: Adjustable Control

Group all stars into a **single accessibility element**, give it the `.adjustable` trait, and implement `accessibilityAdjustableAction` so VoiceOver users can swipe up/down to change the value. This mirrors the experience of a native `Slider`.

```swift
struct StarRatingPicker: View {
    @Binding var rating: Int  // 1–5
    private let maxRating = 5

    var body: some View {
        HStack(spacing: 4) {
            ForEach(1...maxRating, id: \.self) { star in
                Image(systemName: star <= rating ? "star.fill" : "star")
                    .font(.title2)
                    .foregroundStyle(star <= rating ? .yellow : .gray)
                    // Hide individual stars — the group is the single a11y element
                    .accessibilityHidden(true)
            }
        }
        // Group all stars into ONE accessibility element
        .accessibilityElement(children: .ignore)
        // Label: describes what this control is
        .accessibilityLabel("Rating")
        // Value: announces the current rating value
        .accessibilityValue("\(rating) out of \(maxRating) stars")
        // Trait: tells VoiceOver this is an adjustable control
        .accessibilityAddTraits(.isAdjustable)
        // Adjustable action: swipe up increments, swipe down decrements
        .accessibilityAdjustableAction { direction in
            switch direction {
            case .increment:
                if rating < maxRating { rating += 1 }
            case .decrement:
                if rating > 1 { rating -= 1 }
            @unknown default:
                break
            }
        }
    }
}
```

### VoiceOver Behavior

- **On focus:** "Rating, 3 out of 5 stars, adjustable"
- **Swipe up:** rating increments; VoiceOver reads updated value "4 out of 5 stars"
- **Swipe down:** rating decrements; VoiceOver reads "2 out of 5 stars"

---

## Key Design Decisions

### 1. `.accessibilityElement(children: .ignore)`

Collapses the 5 star images into a single element. Without this, VoiceOver would have to swipe through each star individually, reading "star fill" or "star" with no context.

### 2. `.accessibilityValue` vs `.accessibilityLabel`

- **Label** = the name of the control (stable): `"Rating"`
- **Value** = the current state (changes): `"3 out of 5 stars"`

VoiceOver re-reads the value after each adjustment, so the user gets immediate feedback. The label remains constant.

### 3. `.accessibilityAddTraits(.isAdjustable)`

This trait signals to VoiceOver that swipe up/down gestures on this element change its value. Without this trait, swipe up/down would just navigate to the next/previous element.

### 4. Boundary clamping in `accessibilityAdjustableAction`

Always guard against going out of bounds. VoiceOver does not automatically stop at the ends — the action handler must enforce the valid range.

### 5. `@unknown default` in switch

Required because `AccessibilityAdjustmentDirection` is a non-frozen enum. The compiler will warn without it.

---

## No `onTapGesture` Anywhere

The stars are purely visual decorations (`accessibilityHidden(true)`). If you also want sighted users to tap individual stars to set the rating, add that as an **additional** interaction layer, but always ensure the adjustable pattern is the primary accessibility interface:

```swift
ForEach(1...maxRating, id: \.self) { star in
    Image(systemName: star <= rating ? "star.fill" : "star")
        .font(.title2)
        .foregroundStyle(star <= rating ? .yellow : .gray)
        .accessibilityHidden(true)
        // Use Button for tap interaction — not onTapGesture
        .onTapGesture {  // ← still fine here because the group provides a11y
            rating = star
        }
}
```

Since the parent container handles all accessibility, the per-star `onTapGesture` (for visual/pointer interaction) is acceptable — the hidden stars are not VoiceOver targets.
