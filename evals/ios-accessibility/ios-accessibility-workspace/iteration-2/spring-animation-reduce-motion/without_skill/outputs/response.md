# Spring Animation Should Respect Reduce Motion

## The Problem

Spring animations involve bouncing, overshooting, and oscillating motion that can cause nausea or discomfort for users with vestibular disorders. When the user enables Reduce Motion in Settings > Accessibility > Motion, all spring-based animations should be toned down or replaced.

## SwiftUI Approach

Read the environment value and substitute a simple, non-motion animation (or no animation):

```swift
struct AnimatedCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isExpanded = false

    var body: some View {
        RoundedRectangle(cornerRadius: 12)
            .frame(height: isExpanded ? 300 : 100)
            .animation(
                reduceMotion ? .easeInOut(duration: 0.2) : .spring(response: 0.5, dampingFraction: 0.6),
                value: isExpanded
            )
            .onTapGesture { isExpanded.toggle() }
    }
}
```

## UIKit Approach

```swift
func toggleExpanded() {
    let shouldAnimate = !UIAccessibility.isReduceMotionEnabled

    if shouldAnimate {
        UIView.animate(
            withDuration: 0.5,
            delay: 0,
            usingSpringWithDamping: 0.6,
            initialSpringVelocity: 0.8
        ) {
            self.updateLayout()
        }
    } else {
        UIView.animate(withDuration: 0.2) {
            self.updateLayout()
        }
    }
}
```

## Key Principles

1. **Never completely remove feedback** — a short cross-fade or a quick `.easeInOut` is still useful. Avoid going from spring to abrupt instant changes.
2. **Respond to runtime changes** — the user can toggle Reduce Motion without restarting the app. In SwiftUI `@Environment` updates automatically. In UIKit observe `UIAccessibility.reduceMotionStatusDidChangeNotification`.
3. **Scale transforms and parallax** are also motion concerns — set `motionEffect` to none and avoid large `scaleEffect` animations when Reduce Motion is on.
4. **Test on device** — the Simulator can simulate Reduce Motion via Debug > Accessibility Inspector, but real device behavior is more reliable.
