# iOS Accessibility Issues: Smart Invert Colors & Toolbar Button Size

## Issue 1: Photos Inverted Under Smart Invert Colors

### Problem
Smart Invert Colors (introduced in iOS 11) intelligently inverts most UI colors while attempting to preserve images, media, and app icons. However, it does not automatically know which `UIImageView` instances contain photos versus decorative UI images. If your photo views are not marked correctly, Smart Invert will invert them, making photos look color-negative.

### Solution: Mark Image Views to Exclude from Inversion

Set the `accessibilityIgnoresInvertColors` property to `true` on any `UIImageView` (or other view) that displays real photos or content that should not be color-inverted.

**UIKit (Swift):**
```swift
let imageView = UIImageView(image: photo)
imageView.accessibilityIgnoresInvertColors = true
```

**UIKit (Objective-C):**
```objc
imageView.accessibilityIgnoresInvertColors = YES;
```

**SwiftUI:**
Use the `.accessibilityIgnoresInvertColors()` view modifier:
```swift
Image(uiImage: photo)
    .resizable()
    .scaledToFit()
    .accessibilityIgnoresInvertColors()
```

### Important Notes
- This property is available on **any UIView subclass**, not just `UIImageView`. If you have a custom view that renders photo content (e.g., a `WKWebView` displaying images, or a `GLKView`/`MTKView` rendering camera frames), apply it there as well.
- Setting `accessibilityIgnoresInvertColors = true` on a **parent view** also prevents all of its **subviews** from being inverted. Be deliberate about scope — only exclude views that truly contain photographic or media content.
- This does **not** affect the Dark Mode appearance of a view; it only controls Smart Invert behavior.
- Available since **iOS 11** / **tvOS 11**.

### Where to Apply It
Apply this in:
- `UICollectionViewCell` or `UITableViewCell` subclasses that contain photo thumbnails
- Detail/full-screen photo view controllers
- Any custom view used for camera previews (`AVCaptureVideoPreviewLayer` host views)
- Profile picture image views

---

## Issue 2: Toolbar Buttons Too Small at Accessibility Text Sizes

### Problem
When users enable larger Dynamic Type sizes (especially the five "Accessibility" sizes available under Settings > Accessibility > Display & Text Size > Larger Text), standard `UIBarButtonItem` buttons in toolbars and navigation bars may not scale up their tap target or may clip. The 44×44 pt minimum tap target recommended by Apple's Human Interface Guidelines can become insufficient, and custom button layouts may break.

### Root Causes
1. Fixed-size constraints on toolbar buttons that do not adapt to content size category changes.
2. Custom bar button items built with `UIButton` that have fixed frames rather than intrinsic content size.
3. Icon-only buttons that do not increase their tap area at larger text sizes.

### Solutions

#### 1. Use Dynamic Type and Scale Symbols/Icons

Use SF Symbols configured with a Dynamic Type text style so they scale automatically:

```swift
let config = UIImage.SymbolConfiguration(textStyle: .body)
let image = UIImage(systemName: "square.and.arrow.up", withConfiguration: config)
let button = UIBarButtonItem(image: image, style: .plain, target: self, action: #selector(share))
```

For SF Symbols, prefer configurations tied to text styles over fixed point sizes:
```swift
// Scales with the user's preferred text size
UIImage.SymbolConfiguration(textStyle: .title3)
```

#### 2. Enforce Minimum Tap Target Size

Subclass `UIButton` to ensure the tap area is always at least 44×44 pt regardless of the icon size:

```swift
class AccessibleBarButton: UIButton {
    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        let minSize: CGFloat = 44
        let dx = max(0, minSize - bounds.width) / 2
        let dy = max(0, minSize - bounds.height) / 2
        let expandedBounds = bounds.insetBy(dx: -dx, dy: -dy)
        return expandedBounds.contains(point)
    }
}
```

#### 3. Respond to Content Size Category Changes

Listen for `UIContentSizeCategory.didChangeNotification` and update your layout when it fires:

```swift
NotificationCenter.default.addObserver(
    self,
    selector: #selector(contentSizeCategoryDidChange),
    name: UIContentSizeCategory.didChangeNotification,
    object: nil
)

@objc private func contentSizeCategoryDidChange() {
    // Recompute button sizes, invalidate layout, reload toolbar items, etc.
    toolbarItems = buildToolbarItems()
}
```

#### 4. Use `UIBarButtonItem` with Custom Views Carefully

When creating a custom-view `UIBarButtonItem`, ensure the custom view does not have hard-coded width/height constraints:

```swift
let button = AccessibleBarButton(type: .system)
button.setImage(UIImage(systemName: "trash"), for: .normal)
button.translatesAutoresizingMaskIntoConstraints = false
// Do NOT pin to a fixed width/height — let intrinsic content size do the work
let item = UIBarButtonItem(customView: button)
```

#### 5. SwiftUI Toolbars

In SwiftUI, toolbar buttons built with `Button` and `Label` automatically participate in Dynamic Type. Avoid hardcoding `.frame(width:height:)` on toolbar content. Use `.contentShape(Rectangle())` with a reasonably sized frame to keep tap targets large:

```swift
toolbar {
    ToolbarItem(placement: .navigationBarTrailing) {
        Button(action: share) {
            Label("Share", systemImage: "square.and.arrow.up")
        }
        .contentShape(Rectangle())
        .frame(minWidth: 44, minHeight: 44)
    }
}
```

#### 6. Test with Accessibility Inspector and Large Text Sizes

- In **Xcode Simulator**: Settings > Accessibility > Larger Text — drag the slider to the maximum "Accessibility 5" size.
- Use **Xcode's Accessibility Inspector** (Xcode > Open Developer Tool > Accessibility Inspector) to verify hit areas.
- Enable **Button Shapes** in the simulator to visually confirm tap targets.

---

## Summary

| Issue | API / Property | Minimum iOS |
|---|---|---|
| Photos inverted by Smart Invert | `UIView.accessibilityIgnoresInvertColors = true` | iOS 11 |
| SwiftUI photos inverted | `.accessibilityIgnoresInvertColors()` modifier | iOS 14 |
| Toolbar button tap target | Override `point(inside:with:)`, min 44x44 pt | iOS 9 |
| SF Symbol scaling with text size | `UIImage.SymbolConfiguration(textStyle:)` | iOS 13 |
| Layout update on text size change | `UIContentSizeCategory.didChangeNotification` | iOS 7 |

Addressing both issues together ensures your app is usable and visually correct for the 15–20% of iOS users who rely on accessibility features.
