# What's Wrong With `Text("Welcome").font(.system(size: 24))`

## Severity: 🟡 HIGH — AI Failure Pattern F2

This code uses a hardcoded font size. It will never change regardless of what the user has set in Settings → Accessibility → Display & Text Size → Larger Text.

---

## Why This Matters

Over **25% of iOS users** change their preferred text size. This includes:
- Elderly users who need larger text to read comfortably
- Users with low vision who rely on accessibility text sizes
- Users who prefer smaller text to see more content
- Users who set text size per app (iOS 15+)

When a font is hardcoded with `.system(size: 24)`, it ignores all of these preferences. The text stays 24pt regardless. For users at the largest accessibility sizes, this can render text completely unreadable compared to everything else on screen.

This violates **WCAG 1.4.4 Resize Text (AA)**: text must be resizable up to 200% without loss of content or functionality.

---

## The Fix: Use Dynamic Type Text Styles

Replace `.system(size: 24)` with the appropriate semantic text style:

```swift
// ❌ Hardcoded — never scales
Text("Welcome")
    .font(.system(size: 24))

// ✅ Dynamic Type — scales with user preference
Text("Welcome")
    .font(.title)
```

`.title` defaults to 28pt at the system Large (default) size — close to 24pt. It scales up and down proportionally as the user changes their text size preference.

---

## Choosing the Right Text Style

| Style | Default Size | Typical Use |
|---|---|---|
| `.largeTitle` | 34pt | Screen or page titles |
| `.title` | 28pt | Major headings |
| `.title2` | 22pt | Sub-section headings |
| `.title3` | 20pt | Minor headings |
| `.headline` | 17pt (semibold) | Emphasized body content |
| `.body` | 17pt | Primary content |
| `.callout` | 16pt | Secondary content |
| `.subheadline` | 15pt | Supporting text |
| `.footnote` | 13pt | Fine print, footnotes |
| `.caption` | 12pt | Labels, timestamps |
| `.caption2` | 11pt | Smallest readable text |

For a "Welcome" heading, `.title` or `.largeTitle` is appropriate.

---

## Complete Corrected View

```swift
// ❌ Before — hardcoded, never scales
struct WelcomeView: View {
    var body: some View {
        VStack(spacing: 16) {
            Text("Welcome")
                .font(.system(size: 24))
                .bold()
            Text("Let's get started")
                .font(.system(size: 16))
                .foregroundColor(.gray)
        }
    }
}

// ✅ After — Dynamic Type, scales correctly
struct WelcomeView: View {
    var body: some View {
        VStack(spacing: 16) {
            Text("Welcome")
                .font(.title)
                .bold()
            Text("Let's get started")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
}
```

---

## What If You Need a Custom Size?

If the design requires a specific custom size that must still scale, use `.custom(_:size:relativeTo:)`:

```swift
// ✅ Custom font size that still scales with Dynamic Type
Text("Welcome")
    .font(.custom("Georgia", size: 24, relativeTo: .title))
```

The `relativeTo:` parameter defines the scaling curve — this font will scale at the same rate as `.title`.

**Do NOT use:**
```swift
// ❌ fixedSize prevents Dynamic Type scaling
Text("Welcome")
    .font(.custom("Georgia", fixedSize: 24))
```

---

## Testing Dynamic Type

In Xcode:
1. Open the Canvas preview
2. Adjust the Dynamic Type size slider in the preview inspector
3. Alternatively: Simulator → Settings → Accessibility → Display & Text Size → Larger Text

In the Accessibility Inspector: Feature → Fonts → test all 12 text size categories.
