# Making VoiceOver Announce a Section Heading

To make VoiceOver announce an element as a section heading, you need to set the `.header` accessibility trait on that element. This tells VoiceOver to announce "heading" after reading the label, and it also allows users to navigate between headings using the rotor.

## SwiftUI

In SwiftUI, use the `.accessibilityAddTraits(.isHeader)` modifier:

```swift
Text("Account Settings")
    .font(.title)
    .accessibilityAddTraits(.isHeader)
```

## UIKit

In UIKit, set the `accessibilityTraits` property to include `.header`:

```swift
let sectionLabel = UILabel()
sectionLabel.text = "Account Settings"
sectionLabel.accessibilityTraits = .header
```

If the element already has other traits, combine them with a union:

```swift
sectionLabel.accessibilityTraits = [.header, .staticText]
```

## What This Does

When VoiceOver focuses on an element with the header trait, it announces it as a heading (e.g., "Account Settings, heading"). This serves two purposes:

1. **Announces the role** -- Users know the element is a section heading, not just regular text.
2. **Enables rotor navigation** -- Users can set the VoiceOver rotor to "Headings" and swipe up/down to jump between sections, which is especially valuable in long, scrollable screens.

## Tips

- Apply the header trait to the top-level label of each section, not to the container view.
- Make sure the element has a meaningful `accessibilityLabel` (or visible text) so the heading announcement is useful.
- You do not need to include the word "heading" in the label itself -- VoiceOver appends that automatically based on the trait.
