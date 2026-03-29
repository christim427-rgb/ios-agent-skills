# What's Wrong With This Font?

```swift
Text("Welcome").font(.system(size: 24))
```

## Issue: Hardcoded Font Size Breaks Dynamic Type

**Severity: HIGH**

**WCAG:** 1.4.4 Resize Text (AA) | **Apple HIG:** Dynamic Type

This code uses `.font(.system(size: 24))` — a hardcoded point size. The text will always render at exactly 24pt regardless of what the user has configured in Settings > Display & Text Size. This breaks Dynamic Type support entirely.

**Why this matters:** Over 25% of iOS users change their preferred text size. Users who need larger text for readability — including older users, users with low vision, or anyone who simply prefers a more comfortable size — will see text that never adapts to their preference. This violates WCAG 1.4.4 (Resize Text), which requires text to be scalable up to 200% without loss of content or functionality.

## The Fix

Replace the hardcoded size with a Dynamic Type text style:

```swift
// Before — hardcoded, never scales
Text("Welcome").font(.system(size: 24))

// After — scales with the user's text size preference
Text("Welcome").font(.title)
```

The `.title` style defaults to 28pt at the system default size, which is close to your intended 24pt and semantically appropriate for a welcome/heading context. Other options depending on the intended hierarchy:

| Text Style | Default Size | Best For |
|---|---|---|
| `.title` | 28pt | Major headings, welcome screens |
| `.title2` | 22pt | Sub-section headings |
| `.title3` | 20pt | Minor headings |
| `.headline` | 17pt (Semibold) | Emphasized body text |

Choose the style that matches the semantic role of the text, not the one that happens to match your desired pixel size at default settings.

## If You Need a Custom Size as a Starting Point

If your design requires a specific base size, use `.custom` with `relativeTo:` so it still scales:

```swift
// Custom font that still scales with Dynamic Type
Text("Welcome").font(.custom("YourFontName", size: 24, relativeTo: .title))

// Or for SF system fonts with a custom starting size, you can still use a text style
// and trust that the system will size it appropriately
Text("Welcome").font(.title)
```

Avoid `.custom("...", fixedSize: 24)` — the `fixedSize:` parameter explicitly opts out of Dynamic Type scaling.

## VoiceOver Impact

Dynamic Type is distinct from VoiceOver but they are complementary. Users with low vision often use both simultaneously — they need large text AND VoiceOver narration. Hardcoded sizes that ignore Dynamic Type affect these users doubly: the text doesn't scale, and at very small sizes it may become unreadable even with VoiceOver active.

## How to Verify the Fix

In Xcode, use the Environment Overrides panel (Debug > Environment Overrides, or the slider icon in the debug bar at the bottom) to live-preview your view at different Dynamic Type sizes. The text should grow and shrink smoothly as you drag the slider. If it stays fixed, the font is still hardcoded.

You can also test in Simulator:
- Settings > Accessibility > Display & Text Size > Larger Text
- Drag the slider to the largest setting
- Return to your app — "Welcome" should now render at the accessibility scale
