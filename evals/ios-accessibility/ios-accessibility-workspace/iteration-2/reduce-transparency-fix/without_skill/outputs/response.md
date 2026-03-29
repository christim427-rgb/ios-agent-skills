# App Uses .ultraThinMaterial — Breaks with Reduce Transparency Fix

## The Problem

`.ultraThinMaterial` (and other material backgrounds) use blur effects for their visual appearance. When the user enables Settings > Accessibility > Display & Text Size > Reduce Transparency, iOS disables blur effects system-wide. In these conditions, materials either become solid colors or may render as fully transparent, causing text to be unreadable against the underlying content.

## How to Detect It

### SwiftUI

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency
```

### UIKit

```swift
UIAccessibility.isReduceTransparencyEnabled

// Observe changes:
NotificationCenter.default.addObserver(
    self,
    selector: #selector(transparencyChanged),
    name: UIAccessibility.reduceTransparencyStatusDidChangeNotification,
    object: nil
)
```

## Fix in SwiftUI

Conditionally substitute a solid, opaque background when Reduce Transparency is enabled:

```swift
struct BlurredCard: View {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency

    var body: some View {
        content
            .background(
                reduceTransparency
                    ? AnyView(Color(.systemBackground))      // solid opaque fallback
                    : AnyView(RoundedRectangle(cornerRadius: 16).fill(.ultraThinMaterial))
            )
    }
}
```

### For Navigation Bars and Tab Bars

These use materials internally. SwiftUI `toolbarBackground` and UIKit `UINavigationBarAppearance` adapt automatically in most cases, but verify with real device testing.

## Fix for UIKit Views

```swift
func applyBackground() {
    if UIAccessibility.isReduceTransparencyEnabled {
        blurView.isHidden = true
        containerView.backgroundColor = .systemBackground
    } else {
        blurView.isHidden = false
        containerView.backgroundColor = .clear
    }
}
```

## Full Pattern with Dynamic Updates

```swift
struct AdaptiveMaterialView: View {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency
    @Environment(\.colorScheme) var colorScheme

    var fallbackBackground: Color {
        colorScheme == .dark ? Color(white: 0.15) : Color(white: 0.95)
    }

    var body: some View {
        VStack {
            Text("Content")
                .padding()
        }
        .background(
            Group {
                if reduceTransparency {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(fallbackBackground)
                } else {
                    RoundedRectangle(cornerRadius: 16)
                        .fill(.ultraThinMaterial)
                }
            }
        )
    }
}
```

## Key Principles

- Never assume the material will remain translucent — always provide a solid fallback.
- The solid fallback should maintain adequate contrast against the text it contains (WCAG 1.4.3: minimum 4.5:1 for normal text).
- Test with Reduce Transparency enabled in both light and dark mode.
- In SwiftUI, the `@Environment(\.accessibilityReduceTransparency)` value updates automatically — no need to observe notifications manually.
