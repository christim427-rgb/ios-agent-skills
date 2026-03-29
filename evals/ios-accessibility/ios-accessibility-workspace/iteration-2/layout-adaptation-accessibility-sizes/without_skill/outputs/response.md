## Fixing HStack Overflow at Accessibility Text Sizes

### The Problem

`HStack` lays out views horizontally. At large accessibility text sizes (AX1–AX5), text can become 2–3× its default size, causing content to overflow, truncate, or overlap because the horizontal space is not sufficient.

---

### Fix 1: Switch to `VStack` at Large Sizes Using `@Environment(\.dynamicTypeSize)`

Detect the current text size and switch the layout axis automatically:

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    Group {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading, spacing: 8) {
                contentViews
            }
        } else {
            HStack(spacing: 12) {
                contentViews
            }
        }
    }
}

@ViewBuilder
var contentViews: some View {
    Image(systemName: "star.fill")
    Text("Starred items")
    Spacer()
    Text("24")
}
```

`dynamicTypeSize.isAccessibilitySize` is `true` for AX1–AX5 (the five extra-large accessibility sizes above the standard range).

---

### Fix 2: `ViewThatFits` (iOS 16+)

`ViewThatFits` tries each provided layout and picks the first that fits without clipping:

```swift
ViewThatFits(in: .horizontal) {
    // Preferred layout
    HStack {
        Text("Starred items")
        Spacer()
        Text("24 items")
    }
    // Fallback layout when HStack doesn't fit
    VStack(alignment: .leading) {
        Text("Starred items")
        Text("24 items")
    }
}
```

No environment variable needed — the system picks the layout automatically.

---

### Fix 3: Allow Text to Wrap with `fixedSize` and `lineLimit`

If the content is just text, let it wrap instead of switching layouts:

```swift
HStack(alignment: .top) {
    Text("Starred items")
        .fixedSize(horizontal: false, vertical: true)
        .lineLimit(nil)
    Spacer()
    Text("24")
}
```

---

### Fix 4: Use `minimumScaleFactor` as a Last Resort

```swift
Text("Starred items")
    .minimumScaleFactor(0.75)
    .lineLimit(1)
```

This shrinks text to 75% of its size before truncating. It is a less accessible solution than switching layouts but may be acceptable for short labels.

---

### General Best Practices for Accessibility Sizes

- **Test all screens** at AX1, AX3, and AX5 in the iOS simulator (Settings → Accessibility → Display & Text Size → Larger Text).
- Avoid fixed `.frame(width:)` on text containers — use flexible sizing.
- Prefer `VStack` fallbacks over truncation or clipping.
- Ensure minimum touch target size (44×44pt) is maintained even at larger text sizes.
- Use `ScrollView` when content may exceed screen height at large sizes.

---

### Quick Reference

| Technique | iOS Version | Best For |
|-----------|------------|---------|
| `dynamicTypeSize.isAccessibilitySize` | iOS 15+ | Conditional layout switching |
| `ViewThatFits` | iOS 16+ | Automatic layout selection |
| `fixedSize(horizontal:vertical:)` | iOS 13+ | Allowing text to grow vertically |
| `minimumScaleFactor` | iOS 13+ | Single-line labels only (last resort) |
