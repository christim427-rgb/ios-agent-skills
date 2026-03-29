# How to Check if the User Has Reduce Motion Enabled on iOS

## Overview

iOS provides the `UIAccessibility` API to check whether the user has enabled **Reduce Motion** in Settings > Accessibility > Motion > Reduce Motion. This preference signals that the user prefers minimal or no animations.

---

## Checking the Current Value

Use the `UIAccessibility.isReduceMotionEnabled` property:

```swift
import UIKit

if UIAccessibility.isReduceMotionEnabled {
    // Use simplified or no animations
} else {
    // Full animations are fine
}
```

---

## Observing Changes at Runtime

The user can toggle Reduce Motion while your app is running. Subscribe to the `UIAccessibility.reduceMotionStatusDidChangeNotification` notification to respond dynamically:

```swift
import UIKit

class MyViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(reduceMotionChanged),
            name: UIAccessibility.reduceMotionStatusDidChangeNotification,
            object: nil
        )
    }

    @objc private func reduceMotionChanged() {
        if UIAccessibility.isReduceMotionEnabled {
            // Switch to reduced-motion experience
        } else {
            // Restore full animations
        }
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
```

---

## SwiftUI

In SwiftUI, use the `@Environment` key `\.accessibilityReduceMotion`:

```swift
import SwiftUI

struct ContentView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion

    var body: some View {
        Text("Hello")
            .animation(reduceMotion ? .none : .spring(), value: someState)
    }
}
```

---

## Practical Guidelines

- **Always check before animating**: Any animation that moves objects across the screen or scales content should be suppressed or replaced with a simple fade when `isReduceMotionEnabled` is `true`.
- **Prefer cross-fades**: A brief opacity transition (fade in/out) is generally acceptable even with Reduce Motion enabled.
- **Test in the Simulator**: You can toggle Reduce Motion in the iOS Simulator via Settings > Accessibility > Motion > Reduce Motion, or in Xcode's Accessibility Inspector.
- **Test at runtime**: Toggle the setting while the app is running to verify your notification observer works correctly.

---

## Summary

| Approach | API |
|---|---|
| Check current state (UIKit) | `UIAccessibility.isReduceMotionEnabled` |
| Observe changes (UIKit) | `UIAccessibility.reduceMotionStatusDidChangeNotification` |
| SwiftUI environment value | `@Environment(\.accessibilityReduceMotion)` |
