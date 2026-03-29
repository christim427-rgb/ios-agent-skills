# Why `accessibilityIdentifier` Doesn't Help VoiceOver

## The Root Cause

`accessibilityIdentifier` is **not** read by VoiceOver. It is a developer/testing identifier — used exclusively by UI testing frameworks (XCTest, XCUITest) to locate elements programmatically. VoiceOver completely ignores it.

## What VoiceOver Actually Reads

VoiceOver constructs its spoken output from a different set of accessibility properties:

| Property | What VoiceOver Says | Example |
|---|---|---|
| `accessibilityLabel` | The element's name (what it is) | "Favorite" |
| `accessibilityValue` | The current value/state | "Selected" |
| `accessibilityHint` | What will happen when activated | "Double tap to add to favorites" |
| `accessibilityTraits` | Role descriptor appended automatically | "Button" |

VoiceOver combines these in order: **label, value, traits, hint**.

## The Fix

Replace your identifier assignment with a proper accessibility label:

```swift
// WRONG — VoiceOver ignores this entirely
button.accessibilityIdentifier = "favoriteButton"

// CORRECT — VoiceOver reads this aloud
button.accessibilityLabel = "Favorite"
button.accessibilityHint = "Double tap to add to favorites" // optional but recommended
```

If you still need the identifier for UI tests, keep both:

```swift
button.accessibilityIdentifier = "favoriteButton"   // for XCUITest
button.accessibilityLabel = "Favorite"               // for VoiceOver
```

## Why Buttons Often Work Without Explicit Labels

`UIButton` has a built-in fallback: if `accessibilityLabel` is not set, UIKit uses the button's `titleLabel.text` as the label. If your button has no visible title (e.g., it's icon-only), VoiceOver will say nothing meaningful — which is likely what you're experiencing.

**For icon-only buttons, always set `accessibilityLabel` explicitly.**

## Quick Checklist

- [ ] Set `accessibilityLabel` to a short, descriptive name (noun or verb-noun phrase)
- [ ] Verify `isAccessibilityElement` is `true` (it is by default for `UIButton`)
- [ ] Do not rely on `accessibilityIdentifier` for VoiceOver
- [ ] Test with the iOS Simulator's Accessibility Inspector or a real device with VoiceOver enabled
