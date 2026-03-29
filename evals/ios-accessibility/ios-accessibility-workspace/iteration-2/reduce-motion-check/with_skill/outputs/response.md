# Checking Reduce Motion in SwiftUI

## Reading the System Preference

Use `@Environment(\.accessibilityReduceMotion)` to read the user's Reduce Motion setting:

```swift
struct AnimatedCardView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isExpanded = false

    var body: some View {
        VStack {
            CardContent(isExpanded: isExpanded)
        }
        .onTapGesture {
            withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(response: 0.5, dampingFraction: 0.7)) {
                isExpanded.toggle()
            }
        }
    }
}
```

## Replace Motion with Crossfade — Don't Remove All Animation

The key principle: **replace aggressive motion with subtle opacity/crossfade transitions**. Removing all animation entirely makes the UI feel broken and unresponsive.

```swift
// ❌ Ignores Reduce Motion entirely
.transition(.slide)
.animation(.spring(response: 0.4, dampingFraction: 0.6), value: isVisible)

// ❌ Removes animation completely — feels broken
withAnimation(reduceMotion ? nil : .spring()) {
    isVisible.toggle()
}

// ✅ Replace motion with crossfade/opacity — still feels responsive
.transition(reduceMotion ? .opacity : .slide)
.animation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(), value: isVisible)
```

## Transition Examples

```swift
struct DetailPanel: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var showDetail = false

    var body: some View {
        VStack {
            Button("Toggle Detail") {
                withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring()) {
                    showDetail.toggle()
                }
            }

            if showDetail {
                DetailView()
                    .transition(reduceMotion ? .opacity : .move(edge: .bottom))
            }
        }
    }
}
```

## Reusable Helper

For consistency across the app, extract a helper that centralises the motion check:

```swift
// UIKit-based helper (works outside SwiftUI)
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
    isExpanded.toggle()
}
```

## What Counts as Motion (Needs Alternative)

- Sliding / pushing transitions
- Scaling or zooming
- Parallax effects
- Bouncing springs
- Spinning / rotating animations
- Auto-scrolling carousels

## What Is Generally Safe (No Alternative Needed)

- Opacity / crossfade transitions
- Color changes
- Simple state changes without spatial movement

## Summary

| Pattern | Recommendation |
|---|---|
| `.spring()` animation | Replace with `.easeInOut(duration: 0.2)` when `reduceMotion` |
| `.slide` / `.move` transition | Replace with `.opacity` when `reduceMotion` |
| Removing all animation | Avoid — feels unresponsive; use crossfade instead |
| `UIAccessibility.isReduceMotionEnabled` | Use in non-SwiftUI contexts (UIKit, helpers) |
