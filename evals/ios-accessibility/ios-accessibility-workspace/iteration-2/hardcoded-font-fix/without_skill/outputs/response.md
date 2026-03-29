## Problem with `Text("Welcome").font(.system(size: 24))`

### The Issue: Hardcoded Font Size Ignores Dynamic Type

`.font(.system(size: 24))` creates a font with a **fixed point size of 24**. This size never changes regardless of the user's preferred text size setting in Settings → Accessibility → Display & Text Size → Larger Text (or Settings → Display & Brightness → Text Size).

Users who rely on larger text sizes — including many older users and users with low vision — will see the same 24pt text as everyone else. Their accessibility preference is completely ignored.

### Why This Matters

Dynamic Type is an iOS accessibility feature that allows users to choose their preferred text size systemwide. Apps that respect this setting automatically scale all text. Apple's Human Interface Guidelines require Dynamic Type support for App Store approval in accessibility-sensitive contexts, and it is a WCAG 2.1 criterion (1.4.4 Resize Text).

### Fix: Use a Semantic Text Style

Replace the hardcoded size with a named text style that automatically scales:

```swift
// Before (hardcoded — bad)
Text("Welcome")
    .font(.system(size: 24))

// After (Dynamic Type — good)
Text("Welcome")
    .font(.title)
```

Common SwiftUI text styles and their default sizes:

| Style | Default Size |
|-------|-------------|
| `.largeTitle` | 34pt |
| `.title` | 28pt |
| `.title2` | 22pt |
| `.title3` | 20pt |
| `.headline` | 17pt (semibold) |
| `.body` | 17pt |
| `.callout` | 16pt |
| `.subheadline` | 15pt |
| `.footnote` | 13pt |
| `.caption` | 12pt |
| `.caption2` | 11pt |

### If You Must Keep a Custom Size

Use `.system(size:design:)` with `relativeTo:` so the font scales proportionally from its base size:

```swift
Text("Welcome")
    .font(.system(size: 24, weight: .semibold, design: .default)
          .leading(.loose))
```

Actually, the correct SwiftUI approach for a custom base size that still scales is:

```swift
Text("Welcome")
    .font(.custom("SFProDisplay-Regular", size: 24, relativeTo: .title))
```

For system fonts with custom size, use `UIFontMetrics` in UIKit or rely on the built-in styles in SwiftUI.

### Bonus: Allow Extra-Large Accessibility Sizes

For the largest accessibility text sizes (AX1–AX5), consider adding `.minimumScaleFactor` and `.lineLimit(nil)` to avoid truncation:

```swift
Text("Welcome")
    .font(.title)
    .lineLimit(nil)
    .fixedSize(horizontal: false, vertical: true)
```
