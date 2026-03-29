# System Accessibility Preferences Beyond Reduce Motion

For a truly adaptive UI, check all of the following system accessibility preferences:

## Motion & Visual Effects

| Preference | API (UIKit) | SwiftUI Environment Key |
|---|---|---|
| Reduce Motion | `UIAccessibility.isReduceMotionEnabled` | `\.accessibilityReduceMotion` |
| Prefer Cross-Fade Transitions | `UIAccessibility.prefersCrossFadeTransitions` | `\.accessibilityReduceMotion` (same gate) |

## Display & Color

| Preference | API (UIKit) | SwiftUI Environment Key |
|---|---|---|
| Reduce Transparency | `UIAccessibility.isReduceTransparencyEnabled` | `\.accessibilityReduceTransparency` |
| Increase Contrast | `UIAccessibility.isDarkerSystemColorsEnabled` | `\.accessibilityDifferentiateWithoutColor` / `\.colorSchemeContrast` |
| Differentiate Without Color | `UIAccessibility.shouldDifferentiateWithoutColor` | `\.accessibilityDifferentiateWithoutColor` |
| Smart Invert Colors | `UIAccessibility.isInvertColorsEnabled` | `\.accessibilityInvertColors` |
| Bold Text | `UIAccessibility.isBoldTextEnabled` | (use Dynamic Type — it includes bold) |

## Text Size

| Preference | API | SwiftUI |
|---|---|---|
| Dynamic Type size | `UIApplication.shared.preferredContentSizeCategory` | `\.dynamicTypeSize` / `\.sizeCategory` |

## Interaction

| Preference | API (UIKit) | Notes |
|---|---|---|
| Switch Control | `UIAccessibility.isSwitchControlRunning` | Adapt scanning, avoid time-based UI |
| VoiceOver | `UIAccessibility.isVoiceOverRunning` | Adjust layout for linear navigation |
| Assistive Touch | `UIAccessibility.isAssistiveTouchRunning` | Avoid drag-only interactions |
| Guided Access | `UIAccessibility.isGuidedAccessEnabled` | Restrict navigation if needed |
| Shake to Undo | `UIAccessibility.isShakeToUndoEnabled` | Check before triggering undo via shake |
| On/Off Labels | `UIAccessibility.isOnOffSwitchLabelsEnabled` | Use I/O labels on custom toggles |

## Hearing

| Preference | API (UIKit) | Notes |
|---|---|---|
| Mono Audio | `UIAccessibility.isMonoAudioEnabled` | Mix audio channels identically |
| Closed Captions | `MXMetricManager` / AVFoundation | Enable CC by default |

## Practical Usage in SwiftUI

```swift
struct AdaptiveView: View {
    @Environment(\.accessibilityReduceMotion) var reduceMotion
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    @Environment(\.accessibilityDifferentiateWithoutColor) var noColor
    @Environment(\.colorSchemeContrast) var contrast
    @Environment(\.dynamicTypeSize) var typeSize

    var body: some View {
        // Use these to branch your layout/styling
    }
}
```

## Notifications to Observe (UIKit)

```swift
let notifications: [NSNotification.Name] = [
    UIAccessibility.reduceMotionStatusDidChangeNotification,
    UIAccessibility.reduceTransparencyStatusDidChangeNotification,
    UIAccessibility.darkerSystemColorsStatusDidChangeNotification,
    UIAccessibility.invertColorsStatusDidChangeNotification,
    UIAccessibility.voiceOverStatusDidChangeNotification,
    UIContentSizeCategory.didChangeNotification
]
```

All these preferences can change at runtime without an app restart.
