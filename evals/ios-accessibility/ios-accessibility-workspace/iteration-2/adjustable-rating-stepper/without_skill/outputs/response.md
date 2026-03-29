## Accessible Custom Rating Stepper (1–5 Stars) with VoiceOver Swipe Up/Down

### Key Concept: `.isAdjustable` Trait

To let VoiceOver users swipe up/down to change a value, the element must have the `.isAdjustable` trait and implement `accessibilityIncrement()` / `accessibilityDecrement()` (UIKit) or `.accessibilityAdjustableAction` (SwiftUI).

### SwiftUI Implementation

```swift
struct StarRatingView: View {
    @Binding var rating: Int  // 1–5
    let maxRating = 5

    var body: some View {
        HStack(spacing: 4) {
            ForEach(1...maxRating, id: \.self) { star in
                Image(systemName: star <= rating ? "star.fill" : "star")
                    .foregroundColor(.yellow)
                    .onTapGesture { rating = star }
            }
        }
        // Merge all stars into one accessible element
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("Rating")
        .accessibilityValue("\(rating) out of \(maxRating) stars")
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
        .accessibilityAddTraits(.isAdjustable)
    }
}
```

VoiceOver announces: _"Rating, adjustable, 3 out of 5 stars"_
Swipe up → _"4 out of 5 stars"_
Swipe down → _"2 out of 5 stars"_

### UIKit Implementation

Subclass `UIView` (or `UIControl`) and override the adjustable methods:

```swift
class StarRatingControl: UIControl {
    var rating: Int = 3 { didSet { updateStars(); updateAccessibility() } }
    let maxRating = 5

    override var accessibilityTraits: UIAccessibilityTraits {
        get { [.adjustable] }
        set { }
    }

    override var accessibilityLabel: String? {
        get { "Rating" }
        set { }
    }

    override var accessibilityValue: String? {
        get { "\(rating) out of \(maxRating) stars" }
        set { }
    }

    override func accessibilityIncrement() {
        guard rating < maxRating else { return }
        rating += 1
    }

    override func accessibilityDecrement() {
        guard rating > 1 else { return }
        rating -= 1
    }

    private func updateAccessibility() {
        UIAccessibility.post(notification: .announcement, argument: accessibilityValue)
    }
}
```

### Why `onTapGesture` Alone Is Not Enough

`onTapGesture` is not accessible to VoiceOver — it only responds to direct touch, not VoiceOver's double-tap gesture on a focused element. The `.accessibilityAdjustableAction` / `accessibilityIncrement` approach works correctly with VoiceOver regardless of the underlying gesture recognizer.

### Posting Value Change Announcements (optional but recommended)

After each increment/decrement, post an announcement so VoiceOver immediately reads the new value without the user having to re-focus:

```swift
// UIKit
UIAccessibility.post(notification: .announcement, argument: "\(rating) out of \(maxRating) stars")
```

In SwiftUI this is handled automatically when `accessibilityValue` changes on an `.isAdjustable` element.
