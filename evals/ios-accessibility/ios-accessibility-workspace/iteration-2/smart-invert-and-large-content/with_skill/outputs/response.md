# Smart Invert for Photos + Large Content Viewer for Toolbar Buttons

## Part 1: Photos Inverted Under Smart Invert

### The Problem

Smart Invert Colors (Settings > Accessibility > Display & Text Size > Smart Invert) inverts most UI colors to create a dark-mode-like effect. Unlike Classic Invert, Smart Invert is designed to spare images — but it only does so automatically for views it recognizes. Custom image views, `UIImageView`, and SwiftUI `Image` views with photos are inverted, making photos look like negatives.

### The Fix: accessibilityIgnoresInvertColors

```swift
// UIKit — prevents inversion on this view
imageView.accessibilityIgnoresInvertColors = true

// SwiftUI — prevents inversion on this view
Image("user-photo")
    .accessibilityIgnoresInvertColors(true)
```

### Cascade Behavior

Setting `accessibilityIgnoresInvertColors` on a parent view **cascades to all subviews**. Use this to protect an entire photo gallery or media container:

```swift
// SwiftUI — protects all images in this container
VStack {
    Image("cover-photo")
    Image("thumbnail-1")
    Image("thumbnail-2")
}
.accessibilityIgnoresInvertColors(true)
```

```swift
// UIKit — protects all subviews
photoContainerView.accessibilityIgnoresInvertColors = true
```

### What to Protect

Always apply `accessibilityIgnoresInvertColors` to:
- User-uploaded photos
- Product images
- Profile pictures
- Video players
- Maps
- Color swatches / color pickers
- Any image showing real-world content

Do NOT apply to:
- Icons and SF Symbols (should invert for legibility)
- Text-based UI (should invert)
- App chrome and controls (should invert)

---

## Part 2: Toolbar Buttons Too Small for Dynamic Type

### The Problem

Toolbar and navigation bar buttons often cannot scale their icons to match the user's Dynamic Type size — the toolbar height is constrained by the OS. At accessibility text sizes (xxxLarge, AX1–AX5), users may need to see larger representations of these controls.

Additionally, capping Dynamic Type at a sensible maximum prevents toolbar layout from breaking while still respecting user preferences for body text.

### Fix 1: Cap Dynamic Type Size

Prevent the button from scaling beyond a size the toolbar can accommodate, while allowing body text elsewhere to scale freely:

```swift
// SwiftUI — caps this view's maximum Dynamic Type size
Button {
    settingsAction()
} label: {
    Image(systemName: "gearshape")
}
.accessibilityLabel("Settings")
.dynamicTypeSize(...DynamicTypeSize.xxxLarge)  // Cap at xxxLarge
```

### Fix 2: Large Content Viewer (Recommended for Toolbar Items)

`accessibilityShowsLargeContentViewer` enables the iOS Large Content Viewer — when a user with very large text settings long-presses the button, a large overlay appears showing the full label and icon at a readable size. This satisfies both usability and Apple's HIG guidance for toolbar accessibility.

```swift
Button {
    shareAction()
} label: {
    Image(systemName: "square.and.arrow.up")
        .font(.body)
}
.accessibilityLabel("Share")
.dynamicTypeSize(...DynamicTypeSize.xxxLarge)           // Cap layout size
.accessibilityShowsLargeContentViewer {                  // Large Content Viewer
    Label("Share", systemImage: "square.and.arrow.up")  // Shown on long-press
}
```

### Complete Toolbar Example

```swift
struct MainToolbar: View {
    var onShare: () -> Void
    var onSettings: () -> Void
    var onFilter: () -> Void

    var body: some View {
        HStack(spacing: 4) {
            Spacer()

            toolbarButton(
                icon: "line.3.horizontal.decrease.circle",
                label: "Filter",
                action: onFilter
            )

            toolbarButton(
                icon: "square.and.arrow.up",
                label: "Share",
                action: onShare
            )

            toolbarButton(
                icon: "gearshape",
                label: "Settings",
                action: onSettings
            )
        }
        .padding(.horizontal)
    }

    private func toolbarButton(
        icon: String,
        label: String,
        action: @escaping () -> Void
    ) -> some View {
        Button(action: action) {
            Image(systemName: icon)
                .font(.title3)
                .frame(width: 44, height: 44)  // Minimum touch target (Apple HIG)
        }
        .accessibilityLabel(label)
        .dynamicTypeSize(...DynamicTypeSize.xxxLarge)
        .accessibilityShowsLargeContentViewer {
            Label(label, systemImage: icon)
        }
    }
}
```

### When to Use Each Fix

| Scenario | Recommended Fix |
|---|---|
| Body text in content area | Full Dynamic Type scaling — no cap |
| Toolbar / navigation bar icons | Cap + Large Content Viewer |
| Tab bar items | SwiftUI handles automatically; add `.accessibilityShowsLargeContentViewer` for custom tab bars |
| Floating action buttons | Large Content Viewer recommended |
| Status bar items / badge counts | Cap + Large Content Viewer |

### Summary

| Issue | API | Notes |
|---|---|---|
| Photos inverted by Smart Invert | `.accessibilityIgnoresInvertColors(true)` | Cascades to subviews; apply to container |
| Toolbar icons too small at large text | `.dynamicTypeSize(...DynamicTypeSize.xxxLarge)` | Caps maximum size without affecting other text |
| Toolbar icons need accessible label at large sizes | `.accessibilityShowsLargeContentViewer { }` | Long-press reveals label + icon overlay |
