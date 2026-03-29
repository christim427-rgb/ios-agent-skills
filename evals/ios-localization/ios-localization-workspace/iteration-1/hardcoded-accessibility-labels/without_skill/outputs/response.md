# Hardcoded Accessibility Labels

## The Problem

All three accessibility labels are **hardcoded in English**:

```swift
closeButton.accessibilityLabel = "Close"
slider.accessibilityValue = "50 percent"
image.accessibilityLabel = "User profile photo"
```

This means that VoiceOver users who have their device set to a non-English language will hear English text read aloud for these elements. This breaks the accessibility experience for non-English-speaking users.

## The Fix

Localize all accessibility labels and values using `NSLocalizedString` or `String(localized:)`:

```swift
// Using String(localized:) for iOS 15+
closeButton.accessibilityLabel = String(localized: "close_button.accessibility",
    comment: "Accessibility label for close button")
slider.accessibilityValue = String(localized: "slider.accessibility.percent \(value)",
    comment: "Accessibility value showing slider percentage")
image.accessibilityLabel = String(localized: "profile_photo.accessibility",
    comment: "Accessibility label for user's profile photo")

// Or using NSLocalizedString for older targets
closeButton.accessibilityLabel = NSLocalizedString("close_button.accessibility",
    comment: "Accessibility label for close button that dismisses the current screen")
```

## Important Distinction: accessibilityLabel vs accessibilityIdentifier

- **`accessibilityLabel`** -- This is read aloud by VoiceOver to the user. It **must** be localized.
- **`accessibilityValue`** -- This conveys the current value of an element to VoiceOver. It **must** be localized.
- **`accessibilityIdentifier`** -- This is used for UI test automation (XCUITest). It should **NOT** be localized, because tests need stable identifiers that don't change across languages.

```swift
// Localized: for the user via VoiceOver
closeButton.accessibilityLabel = String(localized: "close_button.accessibility",
    comment: "Accessibility: close button")

// NOT localized: for UI tests
closeButton.accessibilityIdentifier = "close_button"
```

## Why This Matters

VoiceOver users rely entirely on accessibility labels to navigate your app. If those labels are in English but the user speaks Arabic, Japanese, or any other language, the app becomes much harder to use. Accessibility and localization must work together.
