# How to Check if User Has Reduce Motion Enabled

## UIKit

Use `UIAccessibility.isReduceMotionEnabled`:

```swift
if UIAccessibility.isReduceMotionEnabled {
    // Skip or simplify animations
}
```

Listen for changes at runtime:

```swift
NotificationCenter.default.addObserver(
    self,
    selector: #selector(reduceMotionChanged),
    name: UIAccessibility.reduceMotionStatusDidChangeNotification,
    object: nil
)

@objc func reduceMotionChanged() {
    let enabled = UIAccessibility.isReduceMotionEnabled
    // Update animations accordingly
}
```

## SwiftUI

Use the `@Environment` property wrapper with `\.accessibilityReduceMotion`:

```swift
struct MyView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        Circle()
            .scaleEffect(reduceMotion ? 1.0 : animatedScale)
            .animation(reduceMotion ? .none : .spring(), value: animatedScale)
    }
}
```

## Best Practices

- Check the value at the point where the animation is applied, not just at startup — the user can toggle this at any time.
- When Reduce Motion is on, prefer instant transitions or simple cross-fades over slides, bounces, and scale transforms.
- Apple's own HIG recommends substituting cross-dissolves for motion-heavy transitions when this setting is active.
- The `withAnimation` block can be conditionally set to `nil` or `.linear(duration: 0)` to effectively disable it.

```swift
withAnimation(reduceMotion ? nil : .spring(response: 0.4)) {
    isExpanded.toggle()
}
```
