# Spring Animation and Reduce Motion

## The Problem

Spring animations use spatial movement — elements bounce, overshoot, and oscillate. This is exactly the type of animation that triggers vestibular disorders and motion sickness. Users who enable Reduce Motion need a non-spatial alternative.

## The Ternary Pattern

The cleanest approach is a ternary expression directly in the animation call:

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

// withAnimation ternary
withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(response: 0.5, dampingFraction: 0.7)) {
    isExpanded.toggle()
}

// .animation modifier ternary
.animation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(), value: isExpanded)
```

## Full Example

```swift
struct ExpandableCard: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @State private var isExpanded = false

    // Computed property keeps the body clean
    private var cardAnimation: Animation {
        reduceMotion
            ? .easeInOut(duration: 0.2)
            : .spring(response: 0.45, dampingFraction: 0.65)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button {
                withAnimation(cardAnimation) {
                    isExpanded.toggle()
                }
            } label: {
                HStack {
                    Text("Details")
                        .font(.headline)
                    Spacer()
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                }
            }
            .accessibilityLabel(isExpanded ? "Collapse details" : "Expand details")

            if isExpanded {
                CardDetailContent()
                    .transition(reduceMotion ? .opacity : .move(edge: .top).combined(with: .opacity))
            }
        }
        .padding()
    }
}
```

## Animation Options When Reduce Motion Is On

| Instead of | Use |
|---|---|
| `.spring()` | `.easeInOut(duration: 0.2)` |
| `.spring(response:dampingFraction:)` | `.easeInOut(duration: 0.2)` |
| `.interpolatingSpring(stiffness:damping:)` | `.easeIn(duration: 0.15)` |
| `.none` | Avoid — removes all feedback |

## Why Not `.none`?

Using `.none` (no animation) makes state changes feel instantaneous and jarring — like the UI is glitching. A short `.easeInOut` crossfade still communicates the state change smoothly without spatial movement.

```swift
// ❌ Abrupt — feels broken
withAnimation(reduceMotion ? .none : .spring()) {
    showPanel.toggle()
}

// ✅ Smooth crossfade — communicates change without motion
withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring()) {
    showPanel.toggle()
}
```

## Transition Pairing

Always pair the animation replacement with a transition replacement:

```swift
if showContent {
    ContentView()
        .transition(
            reduceMotion
                ? .opacity                               // crossfade only
                : .asymmetric(insertion: .move(edge: .trailing), removal: .move(edge: .leading))
        )
}
```

## UIKit / Non-SwiftUI Contexts

```swift
// UIKit: check directly on UIAccessibility
let animation: Animation = UIAccessibility.isReduceMotionEnabled
    ? .easeInOut(duration: 0.2)
    : .spring()
```
