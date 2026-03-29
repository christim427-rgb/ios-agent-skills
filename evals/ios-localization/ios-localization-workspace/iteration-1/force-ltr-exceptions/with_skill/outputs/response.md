# RTL Exceptions: Not Everything Should Flip

No, not all content should flip to RTL. While the general UI layout (text alignment, navigation flow, constraint direction) should mirror for RTL languages, certain types of content are **inherently left-to-right** regardless of language and must remain LTR.

## Content That Should NOT Flip

These elements are universally LTR and should be forced to stay that way:

- **Phone numbers** — always read left to right (+1-555-123-4567)
- **Media playback controls** — play/pause/skip/rewind follow a universal convention (play points right)
- **Progress bars** — fill from left to right universally
- **Numeric sequences** — mathematical expressions, credit card numbers
- **Code snippets** — programming code is always LTR
- **Timestamps** — clock formats (14:30:00)

## How to Force LTR

**UIKit:**
```swift
phoneLabel.semanticContentAttribute = .forceLeftToRight
playbackView.semanticContentAttribute = .forceLeftToRight
```

**SwiftUI:**
```swift
PhoneNumberView()
    .environment(\.layoutDirection, .leftToRight)
```

## Content That SHOULD Flip

The rest of your UI should respect RTL, including:
- Body text and labels
- Navigation flow (back button, drill-down direction)
- List items and their layouts
- Form fields and their labels
- Tab bar order (tabs reverse in RTL)

## Images and Icons

This is an area often missed:

- **Directional images** (arrows, chevrons indicating navigation) **should flip** in RTL:
  ```swift
  // UIKit — auto-flips for RTL
  let image = UIImage(named: "arrow")?.imageFlippedForRightToLeftLayoutDirection()
  ```

- **Non-directional images** (logos, photos, brand icons, icons without directional meaning) should **NOT flip**:
  ```swift
  imageView.semanticContentAttribute = .forceLeftToRight
  ```

For example, a "next" chevron (>) should mirror to (<) in RTL so it points in the reading direction, but your company logo should remain unchanged.

## Testing RTL

Use Xcode's **Right to Left Pseudolanguage** (Edit Scheme -> Options -> Application Language) to flip the entire UI without needing Arabic translations. This makes it easy to verify which elements flip correctly and which exceptions remain LTR.
