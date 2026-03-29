# Hardcoded Accessibility Labels

No, these accessibility labels are **not correct**. All three are hardcoded in English, which means they are completely broken for non-English VoiceOver users. A Spanish, Arabic, or Japanese user using VoiceOver will hear English labels, making the app inaccessible in their language.

## The Problem

```swift
// ❌ All three are hardcoded English — broken for non-English VoiceOver users
closeButton.accessibilityLabel = "Close"
slider.accessibilityValue = "50 percent"
image.accessibilityLabel = "User profile photo"
```

Apple's documentation explicitly states that `accessibilityLabel` must be "a succinct label in a **localized string**." VoiceOver reads these labels aloud, so a French user would hear "Close" instead of "Fermer," and an Arabic user would hear English words in the middle of their RTL VoiceOver experience.

## The Fix

Use `String(localized:)` with accessibility-specific translator comments:

```swift
// ✅ Localized accessibility labels
closeButton.accessibilityLabel = String(
    localized: "close_button.a11y.label",
    comment: "Accessibility: Label for the close button"
)

slider.accessibilityValue = String(
    localized: "slider.a11y.value \(percentage)",
    comment: "Accessibility: Slider percentage value, e.g. '50 percent'"
)

image.accessibilityLabel = String(
    localized: "profile_photo.a11y.label",
    comment: "Accessibility: User's profile photo image"
)
```

## Important: `accessibilityIdentifier` Should NOT Be Localized

Do not confuse `accessibilityLabel` with `accessibilityIdentifier`:

- **`accessibilityLabel`** — spoken by VoiceOver to users. **Must be localized.**
- **`accessibilityIdentifier`** — used by UI test automation to find elements. **Must NOT be localized** — it needs to stay stable across all locales so tests work regardless of language.

```swift
// ✅ Identifier is for tests — never localized
closeButton.accessibilityIdentifier = "closeButton"

// ✅ Label is for users — always localized
closeButton.accessibilityLabel = String(
    localized: "close_button.a11y.label",
    comment: "Accessibility: Close button"
)
```

## SwiftUI

In SwiftUI, `.accessibilityLabel("literal")` with a string literal auto-localizes through `LocalizedStringKey`, but the key must exist in your String Catalog with translations for each supported language:

```swift
Button(action: close) { Image(systemName: "xmark") }
    .accessibilityLabel("close_button.a11y.label")
    .accessibilityIdentifier("closeButton")  // Not localized
```
