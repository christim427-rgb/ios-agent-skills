## Making VoiceOver Announce a Section Heading

### The `.isHeader` Accessibility Trait

Apply the `.isHeader` trait to any view that acts as a section heading. VoiceOver will append "heading" to the announcement, and the element becomes reachable via the Headings rotor so users can jump between sections quickly.

#### SwiftUI

```swift
Text("Recent Orders")
    .font(.title2)
    .accessibilityAddTraits(.isHeader)
```

VoiceOver reads: _"Recent Orders, heading"_

#### UIKit

```swift
sectionLabel.accessibilityTraits = .header
```

Or add it without overwriting existing traits:

```swift
sectionLabel.accessibilityTraits.insert(.header)
```

### Headings Rotor

Once elements have the `.isHeader` / `.header` trait, VoiceOver users can:
1. Rotate two fingers on the screen to open the Rotor.
2. Select "Headings".
3. Flick up/down to jump directly between headings — skipping all content in between.

This is the iOS equivalent of landmark navigation on the web and is extremely valuable for long scrolling screens.

### When to Apply

- Section titles in a `List` or `ScrollView`
- Screen titles (if not already a `NavigationBar` title)
- Category headers in a settings screen or form
- Any `Text` that visually acts as a heading but is not inside a native `NavigationView`

### What NOT to Do

```swift
// Wrong — overwrites all traits, removing any defaults
label.accessibilityTraits = .header

// Correct — insert preserves existing traits
label.accessibilityTraits.insert(.header)
```

In SwiftUI, `.accessibilityAddTraits(.isHeader)` is always additive and safe.

### Heading Levels (iOS 16+)

iOS does not expose HTML-style `h1`–`h6` levels natively through the standard trait API, but you can use `accessibilityHeadingLevel` (available via `UIAccessibilityCustomAttributedStringKey` on NSAttributedString) for more granular rotor hierarchy in complex documents.
