# Localizing Accessibility Labels in SwiftUI

Your code is on the right track, but there are important nuances to get right.

## How SwiftUI Accessibility Labels Auto-Localize

In SwiftUI, `.accessibilityLabel("Share")` takes a `LocalizedStringKey` when you pass a string literal. This means it **automatically looks up** the key "Share" in your String Catalog or `.strings` file — the same way `Text("Share")` would.

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel("Share")  // This IS a LocalizedStringKey — auto-localizes
```

However, this only works if:
1. The key "Share" actually **exists in your String Catalog** with translations for each supported language
2. The translation file is in the correct bundle

If the key is missing from the catalog, VoiceOver will just read the raw key text ("Share") in every language.

## Recommended Approach: Semantic Keys with Comments

Instead of using the English word "Share" as the key, use a semantic key with a meaningful comment so translators understand the context:

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel(Text("share_button.a11y.label"))
```

Then in your String Catalog, add the key `share_button.a11y.label` with:
- **Comment:** "Accessibility: Button to share content via the system share sheet"
- **English value:** "Share"
- **Translations** for each supported language

Using a semantic key avoids ambiguity — "Share" as a noun (a share of stock) vs. "Share" as a verb (share content) may need different translations in many languages.

## In Swift Packages

If your view is inside a Swift Package, you need `bundle: .module`:

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel(Text("share_button.a11y.label", bundle: .module))
```

## Dynamic Accessibility Values

For dynamic values like slider percentages or item counts, use string interpolation with `LocalizedStringKey`:

```swift
slider.accessibilityValue = String(
    localized: "slider.a11y.value \(currentValue)",
    comment: "Accessibility: Current slider value, e.g. '50 percent'"
)
```

## Don't Forget accessibilityIdentifier

For UI testing, always add a stable, non-localized identifier alongside the localized label:

```swift
Button(action: share) { Image(systemName: "square.and.arrow.up") }
    .accessibilityLabel("share_button.a11y.label")
    .accessibilityIdentifier("shareButton")  // Stable for tests, never localized
```
