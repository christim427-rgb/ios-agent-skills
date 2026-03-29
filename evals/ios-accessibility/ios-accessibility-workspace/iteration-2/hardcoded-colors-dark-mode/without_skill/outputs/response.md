## Accessibility Problem with `Text("Hello").foregroundColor(.black).background(Color.white)`

### The Problem: Hardcoded Colors Break Dark Mode and System Overrides

`.foregroundColor(.black)` and `.background(Color.white)` are absolute color values. They are the same in every context — light mode, dark mode, and system accessibility overrides. This causes several issues:

---

### Issue 1: Dark Mode Inversion

In Dark Mode, the system background becomes dark, but the view's own `.background(Color.white)` remains white. Simultaneously, `.foregroundColor(.black)` keeps the text black. The result is black text on a white island — visible but jarring and inconsistent with the rest of the app.

More critically, if the rest of the UI adapts to dark mode (dark background, light text), your hardcoded view creates a stark visual mismatch that breaks visual hierarchy.

---

### Issue 2: Smart Invert Colors (Accessibility)

The "Smart Invert Colors" accessibility feature inverts most screen content to make it easier to view in low-light conditions, while intelligently skipping images and video. Hardcoded black/white can produce unexpected inverted results (white text on black background from what was intended as black on white, or the inversion may be applied inconsistently).

---

### Issue 3: Increased Contrast Mode

Users with "Increase Contrast" enabled in Settings → Accessibility → Display & Text Size expect system colors to adapt to higher contrast. Semantic colors like `.primary` and `.secondary` respond to this setting; raw `.black` and `.white` do not.

---

### Fix: Use Semantic / Adaptive Colors

Replace hardcoded colors with semantic color assets or system colors that adapt automatically:

```swift
// Before (hardcoded — bad)
Text("Hello")
    .foregroundColor(.black)
    .background(Color.white)

// After (adaptive — good)
Text("Hello")
    .foregroundColor(.primary)           // black in light, white in dark
    .background(Color(UIColor.systemBackground))  // white in light, dark in dark
```

Or in SwiftUI using the environment-aware background:

```swift
Text("Hello")
    // No foregroundColor needed — .primary is the default for Text
    .padding()
    .background(Color(.systemBackground))
```

---

### System Colors That Adapt Automatically

| Purpose | SwiftUI | UIKit |
|---------|---------|-------|
| Primary text | `.primary` | `.label` |
| Secondary text | `.secondary` | `.secondaryLabel` |
| App background | `Color(.systemBackground)` | `.systemBackground` |
| Grouped background | `Color(.systemGroupedBackground)` | `.systemGroupedBackground` |
| Separator | `Color(.separator)` | `.separator` |

---

### Asset Catalog Custom Colors

For brand colors, define them in the Asset Catalog with separate light and dark mode variants. SwiftUI picks the correct variant automatically:

```swift
Text("Hello")
    .foregroundColor(Color("BrandTextColor"))   // defined in Assets.xcassets
    .background(Color("BrandBackground"))
```

---

### Summary

Never use raw `.black` / `.white` / hardcoded `Color(red:green:blue:)` for text and backgrounds in production apps. Always use semantic system colors or Asset Catalog adaptive colors to ensure correct appearance in all color modes and accessibility settings.
