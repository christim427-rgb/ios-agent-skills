# Hardcoded Strings Issue

Yes, there are localization issues with this code. All three strings are hardcoded in English, which means they will never be translated for users in other locales.

## Problems

1. `"Welcome to MyApp"` - hardcoded title
2. `"Get started in minutes"` - hardcoded subtitle
3. `"Continue"` - hardcoded button title

None of these strings go through the localization system, so non-English users will always see English text.

## Recommended Fix

For iOS 15+, use `String(localized:)`:

```swift
class OnboardingViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        titleLabel.text = String(localized: "onboarding.title",
                                 comment: "Title shown on the first onboarding screen welcoming the user")
        subtitleLabel.text = String(localized: "onboarding.subtitle",
                                   comment: "Subtitle on onboarding screen encouraging user to get started")
        continueButton.setTitle(String(localized: "onboarding.continue_button",
                                       comment: "Button to proceed from onboarding to the next step"), for: .normal)
    }
}
```

For older deployment targets (below iOS 15), use `NSLocalizedString`:

```swift
titleLabel.text = NSLocalizedString("onboarding.title",
                                     comment: "Title shown on the first onboarding screen welcoming the user")
subtitleLabel.text = NSLocalizedString("onboarding.subtitle",
                                       comment: "Subtitle on onboarding screen encouraging user to get started")
continueButton.setTitle(NSLocalizedString("onboarding.continue_button",
                                           comment: "Button to proceed from onboarding to the next step"), for: .normal)
```

## Key Points

- Always wrap user-facing strings in localization calls.
- Provide meaningful translator comments that describe the context and where the string appears in the UI. Do not leave the `comment` parameter empty -- translators rely on these comments to produce accurate translations.
- Use semantic keys (like `"onboarding.title"`) rather than the English text itself as the key, to avoid ambiguity when the same English word might need different translations in different contexts.
