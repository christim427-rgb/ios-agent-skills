# RTL Exceptions: Not Everything Should Flip

## Short Answer: No

Not all content should flip to RTL. While the overall layout and text direction should respect the user's language, certain elements are inherently directional and should remain Left-to-Right even in an RTL interface.

## Content That Should NOT Flip

1. **Phone numbers and numerical sequences** -- Phone numbers like +1 (555) 123-4567 are always read left-to-right, even in Arabic and Hebrew.

2. **Media playback controls** -- Play, fast-forward, and rewind controls follow a universal convention tied to the physical concept of time progressing from left to right. These should remain LTR.

3. **Progress bars and sliders** -- These typically remain LTR, as they represent a progression (0% to 100%) that is universally understood in that direction.

4. **Music notation and timelines** -- These follow their own directional conventions that do not change with language.

5. **Graphs and charts** -- X-axis progression is typically left-to-right.

## Content That SHOULD Flip

- Navigation elements (back/forward buttons)
- List layouts and table views
- Text and paragraph alignment
- Directional icons like arrows and chevrons (a "forward" arrow should point left in RTL)
- Slide-in menus and navigation drawers

## How to Force LTR

### UIKit
```swift
// Force a specific view to stay LTR
phoneNumberLabel.semanticContentAttribute = .forceLeftToRight

// Force a view to stay RTL (rare)
someView.semanticContentAttribute = .forceRightToLeft
```

### SwiftUI
```swift
// Force LTR layout direction on a specific view
PhoneNumberView()
    .environment(\.layoutDirection, .leftToRight)
```

## Image Considerations

Directional images like arrows and chevrons should flip in RTL. In your asset catalog, you can enable "Direction" on an image to have it automatically mirror. However, logos and brand marks should **never** flip -- they should remain as designed regardless of language direction.

You can mark an image as flipping in the asset catalog by setting its "Direction" property to "Both" or "Left to Right, Mirrors."
