# System Accessibility Preferences for a Truly Adaptive iOS UI

Beyond `UIAccessibility.isReduceMotionEnabled`, iOS exposes a rich set of accessibility preferences that your app should respond to. Here is a comprehensive breakdown organized by category.

---

## Visual Display Preferences

### Bold Text
- **API:** `UIAccessibility.isBoldTextEnabled`
- **Notification:** `UIAccessibility.boldTextStatusDidChangeNotification`
- **Adaptive behavior:** Increase font weight throughout your UI, or use Dynamic Type weights that naturally respond. Avoid relying on thin/ultralight fonts as primary text styles.

### Increased Contrast
- **API:** `UIAccessibility.isDarkerSystemColorsEnabled`
- **Notification:** `UIAccessibility.darkerSystemColorsStatusDidChangeNotification`
- **Adaptive behavior:** Swap your color palette for higher-contrast variants. Ensure text/background contrast ratios meet WCAG AA (4.5:1 for normal text, 3:1 for large). In SwiftUI, use the `colorScheme` environment combined with `.accessibilityReduceTransparency` awareness.

### Reduce Transparency
- **API:** `UIAccessibility.isReduceTransparencyEnabled`
- **Notification:** `UIAccessibility.reduceTransparencyStatusDidChangeNotification`
- **Adaptive behavior:** Replace blur/vibrancy effects (`UIBlurEffect`, `.ultraThinMaterial`) with fully opaque backgrounds. Frosted glass backgrounds that look elegant can become illegible for users with low vision or certain cognitive conditions.

### Differentiate Without Color
- **API:** `UIAccessibility.shouldDifferentiateWithoutColor`
- **Notification:** `UIAccessibility.shouldDifferentiateWithoutColorDidChangeNotification`
- **Adaptive behavior:** Never rely on color alone to convey meaning (e.g., red = error, green = success). Add icons, labels, patterns, or shapes as secondary indicators alongside any color coding.

### Invert Colors (Smart Invert)
- **API:** `UIAccessibility.isInvertColorsEnabled`
- **Notification:** `UIAccessibility.invertColorsStatusDidChangeNotification`
- **Adaptive behavior:** Mark image views, video layers, and color-critical content with `accessibilityIgnoresInvertColors = true` to prevent them from being incorrectly inverted. Without this, photos and custom-drawn graphics will look wrong.

### Display Zoom / Large Display Mode
- **Consideration:** Users may be running the device in Display Zoom mode (Settings > Display & Brightness > Display Zoom), which effectively changes the screen scale. Ensure your layouts use Auto Layout or SwiftUI's adaptive containers and never hardcode pixel dimensions.

---

## Text and Reading Preferences

### Dynamic Type / Preferred Content Size Category
- **API:** `UIApplication.shared.preferredContentSizeCategory` / `traitCollection.preferredContentSizeCategory`
- **Notification:** `UIContentSizeCategory.didChangeNotification`
- **Adaptive behavior:** Use `.preferredFont(forTextStyle:)` or SwiftUI's built-in text styles. Sizes range from `extraSmall` through `accessibilityExtraExtraExtraLarge`. Test all layouts at the largest accessibility sizes — text can be 3-4x larger than the default. Use `adjustsFontForContentSizeCategory = true` on labels.

---

## Motion and Animation Preferences

### Reduce Motion
- **API:** `UIAccessibility.isReduceMotionEnabled`
- **Notification:** `UIAccessibility.reduceMotionStatusDidChangeNotification`
- **Adaptive behavior:** Replace parallax, large spring animations, page-curl transitions, and auto-playing animations with simple fades or instant transitions. In SwiftUI, use the `.animation` modifier conditionally or the `@Environment(\.accessibilityReduceMotion)` environment value.

### Prefer Cross-Fade Transitions (iOS 14+)
- **API:** `UIAccessibility.prefersCrossFadeTransitions`
- **Notification:** `UIAccessibility.prefersCrossFadeTransitionsStatusDidChange`
- **Adaptive behavior:** When Reduce Motion is on, users can further indicate they prefer simple cross-fades rather than even subtle motion. Respect this by switching to opacity-only transitions.

---

## Audio and Haptic Preferences

### On/Off Labels for Switches
- **API:** `UIAccessibility.isOnOffSwitchLabelsEnabled`
- **Notification:** `UIAccessibility.onOffSwitchLabelsDidChangeNotification`
- **Adaptive behavior:** The system handles UISwitch automatically, but if you build custom toggle components, add visible "0"/"1" or "Off"/"On" labels when this is enabled.

### Mono Audio
- **API:** `UIAccessibility.isMonoAudioEnabled`
- **Notification:** `UIAccessibility.monoAudioStatusDidChangeNotification`
- **Adaptive behavior:** If your app uses stereo-panned audio for gameplay or UI feedback (e.g., a sound on the left channel means one thing, right means another), ensure mono users still receive equivalent information through other means.

---

## Interaction Preferences

### Switch Control
- **API:** `UIAccessibility.isSwitchControlRunning`
- **Notification:** `UIAccessibility.switchControlStatusDidChangeNotification`
- **Adaptive behavior:** Ensure all interactive elements are reachable via Switch Control scanning. Avoid gesture-only interactions. Provide sufficient tap target sizes (minimum 44x44 pt). Test that your accessibility element ordering matches the visual flow.

### VoiceOver
- **API:** `UIAccessibility.isVoiceOverRunning`
- **Notification:** `UIAccessibility.voiceOverStatusDidChangeNotification`
- **Adaptive behavior:** When VoiceOver is running, avoid auto-playing audio or video without user intent. Ensure custom views have meaningful `accessibilityLabel`, `accessibilityHint`, and `accessibilityValue`. Consider adjusting layout — hidden decorative elements should have `accessibilityElementsHidden = true`.

### Assistive Touch
- **API:** `UIAccessibility.isAssistiveTouchRunning`
- **Notification:** `UIAccessibility.assistiveTouchStatusDidChangeNotification`
- **Adaptive behavior:** Users relying on AssistiveTouchoften have motor impairments. Avoid requiring precise gestures, multi-finger swipes, or time-sensitive interactions. Provide alternative single-tap routes for all functionality.

### Shake to Undo
- **API:** `UIAccessibility.isShakeToUndoEnabled`
- **Adaptive behavior:** If you use shake gestures for custom actions, provide an alternative interaction path when this setting indicates the user may have modified shake behavior.

### Speak Selection / Speak Screen
- **API:** `UIAccessibility.isSpeakSelectionEnabled`, `UIAccessibility.isSpeakScreenEnabled`
- **Adaptive behavior:** Ensure your text content has accurate `accessibilityLabel` values. Avoid rendering text as images; use actual `UILabel`/`Text` views so the system can read them.

---

## Cognitive and Focus Preferences

### Guided Access
- **API:** `UIAccessibility.isGuidedAccessEnabled`
- **Notification:** `UIAccessibility.guidedAccessStatusDidChangeNotification`
- **Adaptive behavior:** When Guided Access is running, the device is typically being used by someone who needs a focused, restricted interface (e.g., a child or someone with a cognitive disability). Consider simplifying your UI or disabling features outside the session's scope.

---

## SwiftUI Environment Values (Unified Access Point)

SwiftUI provides environment values that consolidate several of the above:

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
@Environment(\.accessibilityReduceTransparency) var reduceTransparency
@Environment(\.accessibilityDifferentiateWithoutColor) var differentiateWithoutColor
@Environment(\.accessibilityInvertColors) var invertColors
@Environment(\.colorSchemeContrast) var contrast  // .standard or .increased
@Environment(\.sizeCategory) var sizeCategory
@Environment(\.legibilityWeight) var legibilityWeight  // .regular or .bold
```

Using these environment values in SwiftUI is preferred over the UIKit static APIs because they automatically trigger view re-renders when the user changes preferences.

---

## Implementation Strategy

1. **Audit your color usage first.** Run your app with Increase Contrast and Differentiate Without Color enabled. These two catch the most widespread issues.

2. **Test at `accessibilityExtraExtraExtraLarge` text size.** Most layouts break here. Fix truncation, clipping, and overflow.

3. **Use `UIAccessibility.post(notification:argument:)` appropriately.** When your UI changes significantly (modal appears, content reloads), announce it so VoiceOver users are not confused.

4. **Subscribe to change notifications rather than polling.** Register for the relevant `NSNotification.Name` values at app launch and update your UI reactively.

5. **Never assume defaults.** A significant percentage of users (studies suggest 7-25% depending on feature) have at least one accessibility setting enabled. These are mainstream features, not edge cases.

6. **Test with real assistive technology.** Enable VoiceOver and navigate your entire critical user journey. Enable Switch Control with a keyboard. This surfaces issues that static checks miss.

---

## Quick Reference: All Key APIs

| Preference | UIKit API | SwiftUI Environment |
|---|---|---|
| Reduce Motion | `isReduceMotionEnabled` | `\.accessibilityReduceMotion` |
| Prefer Cross-Fade | `prefersCrossFadeTransitions` | — |
| Reduce Transparency | `isReduceTransparencyEnabled` | `\.accessibilityReduceTransparency` |
| Increase Contrast | `isDarkerSystemColorsEnabled` | `\.colorSchemeContrast` |
| Bold Text | `isBoldTextEnabled` | `\.legibilityWeight` |
| Differentiate Without Color | `shouldDifferentiateWithoutColor` | `\.accessibilityDifferentiateWithoutColor` |
| Invert Colors | `isInvertColorsEnabled` | `\.accessibilityInvertColors` |
| Dynamic Type | `preferredContentSizeCategory` | `\.sizeCategory` |
| VoiceOver Running | `isVoiceOverRunning` | — |
| Switch Control Running | `isSwitchControlRunning` | — |
| AssistiveTouch Running | `isAssistiveTouchRunning` | — |
| Guided Access | `isGuidedAccessEnabled` | — |
| Mono Audio | `isMonoAudioEnabled` | — |
| On/Off Switch Labels | `isOnOffSwitchLabelsEnabled` | — |
