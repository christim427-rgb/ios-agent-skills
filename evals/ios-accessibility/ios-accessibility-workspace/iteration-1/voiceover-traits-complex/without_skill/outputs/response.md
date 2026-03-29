# Making a Custom Rating Stepper Accessible with VoiceOver

## The Problem

Your current implementation renders five individual star images, each with a tap gesture. This creates several VoiceOver issues:

1. VoiceOver sees five separate, unlabeled image elements instead of one unified control.
2. There is no accessibility label describing the current rating.
3. There is no way for VoiceOver users to adjust the value with swipe up/down gestures.
4. Each star image has no meaningful role or description.

## The Solution

Treat the entire `HStack` as a single **adjustable** accessibility element. The `.accessibilityAdjustableAction` modifier is the key -- it gives VoiceOver the `.adjustable` trait automatically, enabling swipe-up to increment and swipe-down to decrement.

```swift
struct RatingStepper: View {
    @Binding var rating: Int

    var body: some View {
        HStack {
            ForEach(1...5, id: \.self) { i in
                Image(systemName: i <= rating ? "star.fill" : "star")
                    .foregroundStyle(i <= rating ? .yellow : .gray)
                    .onTapGesture { rating = i }
            }
        }
        // Combine all child elements into a single accessible element
        .accessibilityElement(children: .ignore)
        // Provide a meaningful label
        .accessibilityLabel("Rating")
        // Announce the current value
        .accessibilityValue("\(rating) out of 5 stars")
        // Enable swipe up/down adjustment -- this automatically adds the .adjustable trait
        .accessibilityAdjustableAction { direction in
            switch direction {
            case .increment:
                rating = min(rating + 1, 5)
            case .decrement:
                rating = max(rating - 1, 1)
            @unknown default:
                break
            }
        }
    }
}
```

## How It Works

### `.accessibilityElement(children: .ignore)`

This collapses the five individual star images into a single VoiceOver focus target. Without this, VoiceOver would land on each star separately, which is confusing and verbose. The `children: .ignore` parameter tells VoiceOver to disregard the child views and treat the `HStack` as one atomic element.

### `.accessibilityLabel("Rating")`

Provides the name of the control. When VoiceOver focuses on this element, it announces "Rating" so the user understands what the control represents.

### `.accessibilityValue("\(rating) out of 5 stars")`

Tells VoiceOver the current state. After reading the label, VoiceOver announces the value -- for example, "3 out of 5 stars". This updates dynamically as the rating changes.

### `.accessibilityAdjustableAction`

This is the critical modifier. It does two things:

1. **Adds the `.adjustable` trait** to the element automatically. VoiceOver will announce "adjustable" after the label and value, signaling to the user that they can swipe up or down.
2. **Provides the handler** for increment and decrement actions. When the user swipes up, VoiceOver calls the closure with `.increment`. When they swipe down, it calls with `.decrement`.

The `@unknown default` case handles any future directions Apple might add.

## VoiceOver Behavior

When a VoiceOver user navigates to this control, they hear:

> "Rating, 3 out of 5 stars, adjustable"

- **Swipe up**: Increments the rating (e.g., 3 becomes 4). VoiceOver announces "4 out of 5 stars".
- **Swipe down**: Decrements the rating (e.g., 3 becomes 2). VoiceOver announces "2 out of 5 stars".

The value is clamped between 1 and 5 so the user cannot go out of range.

## Optional Enhancements

### Adding a Hint

You can add an accessibility hint to provide additional guidance for users who have hints enabled:

```swift
.accessibilityHint("Swipe up or down to adjust the rating")
```

### Using `accessibilityAddTraits` for Extra Semantics

If you want VoiceOver to also recognize this as an image (since it displays stars visually), you can layer on an additional trait:

```swift
.accessibilityAddTraits(.isImage)
```

### Supporting Direct Tap in VoiceOver

Since tapping individual stars is not practical with VoiceOver (the children are ignored), the adjustable action becomes the primary interaction method. This is the standard iOS pattern for stepper-like controls -- `UIStepper` in UIKit works the same way under VoiceOver.

## Summary

| Modifier | Purpose |
|---|---|
| `.accessibilityElement(children: .ignore)` | Merge stars into one VoiceOver element |
| `.accessibilityLabel("Rating")` | Name the control |
| `.accessibilityValue("\(rating) out of 5 stars")` | Announce current state |
| `.accessibilityAdjustableAction` | Enable swipe up/down + add adjustable trait |

This pattern follows Apple's accessibility guidelines for custom adjustable controls and matches user expectations from built-in iOS components like sliders and steppers.
