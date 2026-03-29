# WCAG Criterion for Text Resizing on iOS

## Answer

**WCAG 1.4.4 — Resize Text** is the criterion that covers text resizing on iOS.

## Details

| Field | Value |
|---|---|
| Criterion | 1.4.4 Resize Text |
| Level | AA |
| Priority | HIGH |
| iOS APIs | `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory = true` |

## What It Requires

WCAG 1.4.4 requires that text can be resized up to 200% without loss of content or functionality. On iOS, this is implemented through **Dynamic Type** — the system-level text scaling mechanism.

## iOS Implementation

### SwiftUI
Use Dynamic Type text styles instead of hardcoded sizes:

```swift
// WRONG — hardcoded size, fails WCAG 1.4.4
Text("Hello").font(.system(size: 17))

// CORRECT — scales with user's text size preference
Text("Hello").font(.body)

// CORRECT — custom font that scales relative to a text style
Text("Hello").font(.custom("MyFont", size: 17, relativeTo: .body))
```

### UIKit
Use `UIFontMetrics` and enable automatic adjustment:

```swift
// WRONG
label.font = UIFont.systemFont(ofSize: 17)

// CORRECT
label.font = UIFont.preferredFont(forTextStyle: .body)
label.adjustsFontForContentSizeCategory = true

// CORRECT — custom font
let baseFont = UIFont(name: "MyFont", size: 17)!
label.font = UIFontMetrics(forTextStyle: .body).scaledFont(for: baseFont)
label.adjustsFontForContentSizeCategory = true
```

## Related: WCAG 1.4.10 — Reflow

At the largest accessibility text sizes, layouts must also adapt without requiring horizontal scrolling (WCAG 1.4.10 — Reflow). On iOS this means:

- Switching `HStack` to `VStack` at accessibility sizes
- Wrapping content in `ScrollView` to handle overflow
- Using `ViewThatFits` (iOS 16+) for automatic layout switching

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    Group {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading) { content }
        } else {
            HStack { content }
        }
    }
}
```

## Why AI-Generated Code Commonly Fails This

AI coding assistants (including Claude without this skill) systematically use `.font(.system(size: N))` with hardcoded sizes. This is classified as a **HIGH severity** failure because it breaks the experience for approximately 25%+ of users who increase their text size in iOS Settings.

## Source

From `references/wcag-ios-mapping.md` in the ios-accessibility skill:

> | **1.4.4** | Resize Text | `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory` | HIGH | AI always uses hardcoded sizes |
