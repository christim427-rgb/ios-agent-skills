# How to Check if the User Has Reduce Motion Enabled

## SwiftUI — `@Environment` (Recommended)

In SwiftUI, read the `accessibilityReduceMotion` environment value. This automatically updates your view when the user changes the setting in Settings > Accessibility > Motion.

```swift
struct AnimatedView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var showDetail = false

    var body: some View {
        Button("Toggle") {
            // Use crossfade when reduce motion is on, spring when off
            withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring()) {
                showDetail.toggle()
            }
        }

        if showDetail {
            DetailView()
                // Replace slide transition with opacity when reduce motion is on
                .transition(reduceMotion ? .opacity : .slide)
        }
    }
}
```

## UIKit — `UIAccessibility.isReduceMotionEnabled`

In UIKit, read the static property and observe the notification for changes:

```swift
// One-time check
if UIAccessibility.isReduceMotionEnabled {
    // Use opacity/crossfade instead of motion
} else {
    // Use full animation
}

// Observe live changes (register in viewDidLoad or init)
NotificationCenter.default.addObserver(
    self,
    selector: #selector(reduceMotionChanged),
    name: UIAccessibility.reduceMotionStatusDidChangeNotification,
    object: nil
)

@objc private func reduceMotionChanged() {
    let isReduced = UIAccessibility.isReduceMotionEnabled
    // Update animations accordingly
}
```

## Reusable Helper (Works in Both Contexts)

A helper function that wraps `UIAccessibility.isReduceMotionEnabled` for UIKit code or imperative animation calls:

```swift
func withOptionalAnimation<Result>(
    _ animation: Animation? = .default,
    _ body: () throws -> Result
) rethrows -> Result {
    if UIAccessibility.isReduceMotionEnabled {
        return try body()
    } else {
        return try withAnimation(animation, body)
    }
}

// Usage
withOptionalAnimation(.spring()) {
    showDetail = true
}
```

## Key Principles

**Do not remove all animation** — replace aggressive motion with subtle crossfade/opacity transitions. Removing all animation feels broken and disorienting. The goal is to eliminate spatial movement (sliding, scaling, parallax, rotation, 3D transforms), not all visual feedback.

**Animations that need a reduce-motion alternative:**
- Sliding / pushing transitions
- Scaling / zooming transitions
- Parallax effects
- Spinning or rotating animations
- Bouncing springs
- Auto-scrolling carousels

**Animations that are generally safe (no alternative needed):**
- Opacity / crossfade transitions
- Color changes
- Simple state changes without spatial movement

## Severity

Ignoring `reduceMotion` is a **HIGH** severity issue. It breaks the experience for users with vestibular disorders (motion sickness, vertigo) who rely on this system setting. WCAG 2.3.3 (AAA) addresses animation from interactions, and Apple's Human Interface Guidelines explicitly require respecting this preference.

## Quick Checklist

- [ ] Every animation in the app reads `@Environment(\.accessibilityReduceMotion)` or checks `UIAccessibility.isReduceMotionEnabled`
- [ ] Reduce motion replaces motion with opacity/crossfade — it does not simply remove animation
- [ ] UIKit code observes `UIAccessibility.reduceMotionStatusDidChangeNotification` to handle live changes
