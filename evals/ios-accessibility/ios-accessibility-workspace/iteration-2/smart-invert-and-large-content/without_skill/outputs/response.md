# Photos Inverted Under Smart Invert + Toolbar Buttons Too Small at Accessibility Sizes

## Problem 1: Photos Inverted Under Smart Invert

Smart Invert Colors (Settings > Accessibility > Display & Text Size > Smart Invert) inverts most colors in the display to provide a dark appearance, but is supposed to be "smart" enough to skip images, video, and certain UI elements. By default, however, custom image views are not excluded — you must explicitly opt out.

### UIKit Fix

Set `accessibilityIgnoresInvertColors = true` on any `UIView` that contains photos or images that should not be inverted:

```swift
// On the UIImageView directly:
imageView.accessibilityIgnoresInvertColors = true

// Or on a container view to protect everything inside:
photoContainerView.accessibilityIgnoresInvertColors = true
```

### SwiftUI Fix

Use the `.accessibilityIgnoresInvertColors()` modifier:

```swift
Image("userPhoto")
    .resizable()
    .scaledToFill()
    .accessibilityIgnoresInvertColors()  // preserves true colors under Smart Invert
```

### When to Apply It

Apply to:
- Photo thumbnails and full-screen photos
- Video thumbnails and players
- Maps and camera previews
- Charts and graphs that use color to encode meaning
- App logos and brand imagery where color identity matters

Do NOT apply to UI chrome — buttons, backgrounds, text — those should invert normally to maintain the dark appearance the user has chosen.

---

## Problem 2: Toolbar Buttons Too Small at Accessibility Text Sizes

At larger Dynamic Type sizes, toolbar icons may not scale and the touch target can become disproportionately small compared to the surrounding text.

### Cause

Custom toolbar buttons using `UIBarButtonItem` with fixed-size views, or SwiftUI toolbar items with fixed frames, don't automatically scale their hit areas.

### SwiftUI Fix: Large Content Viewer

For toolbar items and other elements that cannot grow in size at accessibility text sizes, enable the Large Content Viewer (a zoom-on-hold accessibility feature):

```swift
// SwiftUI toolbar item:
ToolbarItem(placement: .navigationBarTrailing) {
    Button(action: share) {
        Image(systemName: "square.and.arrow.up")
    }
    .accessibilityShowsLargeContentViewer()  // enables long-press zoom
    .accessibilityLabel("Share")
}
```

### UIKit Fix: Large Content Viewer

```swift
button.showsLargeContentViewer = true
button.largeContentTitle = "Share"
button.largeContentImage = UIImage(systemName: "square.and.arrow.up")
button.addInteraction(UILargeContentViewerInteraction())
```

### SwiftUI Fix: Scale with @ScaledMetric

For icons that CAN grow:

```swift
struct ToolbarIcon: View {
    @ScaledMetric(relativeTo: .body) var iconSize: CGFloat = 24

    var body: some View {
        Image(systemName: "gear")
            .font(.system(size: iconSize))
            .frame(minWidth: 44, minHeight: 44)  // ensure minimum hit area
    }
}
```

### Minimum Hit Target

Always ensure at least 44×44 pt tappable area regardless of icon size:

```swift
Image(systemName: "square.and.arrow.up")
    .frame(minWidth: 44, minHeight: 44)
    .contentShape(Rectangle())
```

---

## Combined Fix Summary

```swift
struct PhotoCell: View {
    @ScaledMetric(relativeTo: .body) var actionIconSize: CGFloat = 22

    var body: some View {
        ZStack {
            Image("userPhoto")
                .resizable()
                .scaledToFill()
                .accessibilityIgnoresInvertColors()  // fix Smart Invert

            VStack {
                Spacer()
                HStack {
                    Spacer()
                    Button(action: sharePhoto) {
                        Image(systemName: "square.and.arrow.up")
                            .font(.system(size: actionIconSize)) // scales with Dynamic Type
                            .frame(minWidth: 44, minHeight: 44)   // adequate hit area
                    }
                    .accessibilityLabel("Share photo")
                    .accessibilityShowsLargeContentViewer()
                }
            }
        }
    }
}
```
