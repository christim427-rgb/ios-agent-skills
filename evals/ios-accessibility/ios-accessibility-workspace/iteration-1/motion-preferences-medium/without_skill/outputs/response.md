# Respecting Reduce Motion with Spring Animations in SwiftUI

## The Problem

Your current animation uses a bouncy spring with a low damping fraction (0.3), which creates a highly oscillating, energetic motion. For users who have enabled **Reduce Motion** in iOS Settings (Settings > Accessibility > Motion > Reduce Motion), this type of animation can cause discomfort or even physical symptoms like dizziness or nausea.

## Solution

Use the `@Environment(\.accessibilityReduceMotion)` environment value to detect the user's preference and substitute a gentler animation (or no animation at all) when Reduce Motion is enabled.

### Approach 1: Conditional Animation (Recommended)

```swift
struct ContentView: View {
    @State private var showDetail = false
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        Button("Toggle Detail") {
            let animation: Animation = reduceMotion
                ? .easeInOut(duration: 0.2)
                : .spring(response: 0.5, dampingFraction: 0.3)

            withAnimation(animation) {
                showDetail.toggle()
            }
        }

        if showDetail {
            DetailView()
        }
    }
}
```

### Approach 2: No Animation When Reduce Motion is Enabled

If the transition itself (not just the spring bounce) is the concern, you can skip animation entirely:

```swift
Button("Toggle Detail") {
    if reduceMotion {
        showDetail.toggle() // instant, no animation
    } else {
        withAnimation(.spring(response: 0.5, dampingFraction: 0.3)) {
            showDetail.toggle()
        }
    }
}
```

### Approach 3: Reusable Helper Extension

For consistency across your app, create a helper that wraps this logic:

```swift
extension Animation {
    static func accessibleSpring(
        response: Double = 0.5,
        dampingFraction: Double = 0.3
    ) -> Animation {
        // This is called at the call site with the environment value
        .spring(response: response, dampingFraction: dampingFraction)
    }
}

// Helper function at the view or app level
func withAccessibleAnimation<Result>(
    reduceMotion: Bool,
    _ body: () throws -> Result
) rethrows -> Result {
    if reduceMotion {
        return try withAnimation(.easeInOut(duration: 0.2), body)
    } else {
        return try withAnimation(.spring(response: 0.5, dampingFraction: 0.3), body)
    }
}
```

Then use it:

```swift
withAccessibleAnimation(reduceMotion: reduceMotion) {
    showDetail.toggle()
}
```

### Approach 4: Custom View Modifier

```swift
struct AccessibleAnimationModifier: ViewModifier {
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    let trigger: Bool

    func body(content: Content) -> some View {
        content
            .animation(
                reduceMotion
                    ? .easeInOut(duration: 0.2)
                    : .spring(response: 0.5, dampingFraction: 0.3),
                value: trigger
            )
    }
}

extension View {
    func accessibleSpringAnimation(trigger: Bool) -> some View {
        modifier(AccessibleAnimationModifier(trigger: trigger))
    }
}

// Usage
DetailView()
    .accessibleSpringAnimation(trigger: showDetail)
```

## What Makes a "Reduce Motion" Friendly Animation?

When Reduce Motion is on, prefer:

| Instead of | Use |
|---|---|
| Bouncy springs (dampingFraction < 0.7) | `.easeInOut` or a critically damped spring |
| Large-scale transforms (zoom in/out) | Fade (`.opacity`) transitions |
| Sliding transitions | Cross-dissolve (`.opacity`) |
| Parallax or continuous motion | Static or no animation |

A critically damped spring (no oscillation) is also acceptable:
```swift
.spring(response: 0.3, dampingFraction: 1.0) // no bounce, settles immediately
```

## Key API Reference

- `@Environment(\.accessibilityReduceMotion) var reduceMotion: Bool` — reads the system preference
- `UIAccessibility.isReduceMotionEnabled` — UIKit equivalent (also available in SwiftUI contexts if needed)
- You can also observe `UIAccessibility.reduceMotionStatusDidChangeNotification` for dynamic updates in UIKit

## Apple Human Interface Guidelines

Apple recommends:
- Avoid adding motion to interfaces that don't need it.
- Use fade transitions instead of sliding or zooming when Reduce Motion is on.
- Never disable the Reduce Motion accommodation — always respect it.

The `accessibilityReduceMotion` environment value automatically updates if the user changes their preference while your app is running, so `@Environment` will always reflect the current state without any extra work on your part.
