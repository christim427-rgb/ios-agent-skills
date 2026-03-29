# What's Wrong with This Font?

```swift
Text("Welcome").font(.system(size: 24))
```

## The Problem: No Dynamic Type Support

This code uses a **fixed font size of 24 points** that never changes, regardless of the user's preferred text size setting. This breaks Dynamic Type support.

### Why This Matters

iOS provides a powerful accessibility feature called **Dynamic Type**, which allows users to set their preferred text size in **Settings > Accessibility > Display & Text Size > Larger Text** (or via Control Center). When users adjust this setting, all well-behaved apps update their text sizes accordingly.

By hard-coding `.system(size: 24)`, your text:

- **Ignores the user's preferred text size** — the text stays at 24pt no matter what the user has configured
- **Fails users with visual impairments** who rely on larger text to read comfortably
- **Fails users who prefer smaller text** who want more content visible on screen
- **Does not conform to Apple's Human Interface Guidelines**, which explicitly recommend using Dynamic Type

### The Fix

Use a semantic text style instead of a fixed size:

```swift
Text("Welcome").font(.title)
```

Or if you need the system font with Dynamic Type scaling:

```swift
Text("Welcome").font(.system(.title))
```

If you must use a custom size but still want it to scale with Dynamic Type:

```swift
Text("Welcome")
    .font(.system(size: 24, weight: .regular, design: .default))
    .dynamicTypeSize(.xSmall ... .accessibility5)
```

Or use `scaledFont` via `@ScaledMetric` for fully custom sizing:

```swift
@ScaledMetric(relativeTo: .title) var fontSize: CGFloat = 24

Text("Welcome").font(.system(size: fontSize))
```

### Recommended Approach

The cleanest solution is to use one of SwiftUI's built-in text styles, which automatically scale with the user's Dynamic Type setting:

| Style | Typical Size |
|---|---|
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

For a "Welcome" heading, `.title` or `.largeTitle` is the most appropriate replacement:

```swift
Text("Welcome").font(.title)
```

This single change makes your app respect the user's accessibility preferences and brings it in line with Apple's HIG.
