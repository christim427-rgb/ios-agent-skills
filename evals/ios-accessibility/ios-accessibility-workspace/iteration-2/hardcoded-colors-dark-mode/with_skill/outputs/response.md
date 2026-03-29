# What's Wrong With `Text("Hello").foregroundColor(.black).background(Color.white)`

## Two Issues, Two Severity Levels

### Issue 1: Hardcoded Colors — 🟡 HIGH (AI Failure Pattern F3)

`.black` text on `.white` background creates a hardcoded color combination that is completely invisible in dark mode. When the user switches to dark mode (or has auto dark mode enabled at sunset), the background turns dark but your text stays black — black text on a dark background is unreadable.

### Issue 2: Deprecated API — 🟡 HIGH (AI Failure Pattern F4)

`.foregroundColor()` is **deprecated as of iOS 17**. The replacement is `.foregroundStyle()`, which additionally supports multi-layer content like gradients, materials, and hierarchical styles — not just flat colors.

---

## The Fix: Semantic Colors + Modern API

```swift
// ❌ Current — hardcoded colors break in dark mode, deprecated API
Text("Hello")
    .foregroundColor(.black)
    .background(Color.white)

// ✅ Corrected — semantic colors adapt to light/dark/contrast modes, modern API
Text("Hello")
    .foregroundStyle(.primary)
    .background(Color(.systemBackground))
```

**In light mode:** `.primary` is near-black, `systemBackground` is white — visually identical to the original.

**In dark mode:** `.primary` becomes near-white, `systemBackground` becomes dark — readable automatically. No code change required.

---

## Why Semantic Colors Work

Semantic colors are **adaptive** — they automatically return the correct value for:
- Light mode
- Dark mode
- Light + High Contrast (Increase Contrast enabled)
- Dark + High Contrast

The system handles all four variants. You write the code once.

| Hardcoded | Semantic equivalent | Adapts to |
|---|---|---|
| `.black` (text) | `.primary` | Dark mode, high contrast |
| `.white` (background) | `Color(.systemBackground)` | Dark mode, high contrast |
| `.gray` (secondary text) | `.secondary` | Dark mode, high contrast |
| `Color(red:green:blue:)` | Asset catalog with variants | All modes (if configured) |

---

## Complete Corrected Component

```swift
// ❌ Before — two issues: hardcoded colors and deprecated API
struct GreetingCard: View {
    let name: String

    var body: some View {
        VStack(spacing: 12) {
            Text("Hello, \(name)")
                .font(.system(size: 24))        // Also wrong — hardcoded font
                .foregroundColor(.black)        // Deprecated + hardcoded
            Text("Welcome back")
                .font(.system(size: 16))        // Also wrong
                .foregroundColor(Color(red: 0.4, green: 0.4, blue: 0.4))  // Hardcoded gray
        }
        .padding()
        .background(Color.white)                // Hardcoded white
        .cornerRadius(12)                       // Also deprecated
    }
}

// ✅ After — semantic colors, modern API, Dynamic Type
struct GreetingCard: View {
    let name: String

    var body: some View {
        VStack(spacing: 12) {
            Text("Hello, \(name)")
                .font(.title)                          // Dynamic Type
                .foregroundStyle(.primary)             // Adapts to dark mode
            Text("Welcome back")
                .font(.subheadline)                    // Dynamic Type
                .foregroundStyle(.secondary)           // Adapts to dark mode
        }
        .padding()
        .background(Color(.systemBackground))          // Adapts to dark mode
        .clipShape(.rect(cornerRadius: 12))            // Modern API (iOS 17+)
    }
}
```

---

## Semantic Color Reference

| Purpose | SwiftUI | UIKit |
|---|---|---|
| Primary text | `.primary` | `UIColor.label` |
| Secondary text | `.secondary` | `UIColor.secondaryLabel` |
| Tertiary text | — | `UIColor.tertiaryLabel` |
| Primary background | `Color(.systemBackground)` | `UIColor.systemBackground` |
| Secondary background | `Color(.secondarySystemBackground)` | `UIColor.secondarySystemBackground` |
| Grouped background | `Color(.systemGroupedBackground)` | `UIColor.systemGroupedBackground` |
| Separator | `Color(.separator)` | `UIColor.separator` |
| Tint / accent | `.tint` | `UIColor.tintColor` |

---

## API Deprecation Summary

| Deprecated | Replacement | Since |
|---|---|---|
| `.foregroundColor()` | `.foregroundStyle()` | iOS 17 |
| `.cornerRadius()` | `.clipShape(.rect(cornerRadius:))` | iOS 17 |
| `NavigationView` | `NavigationStack` | iOS 16 |

`.foregroundStyle()` is strictly more capable than `.foregroundColor()`. It accepts all `ShapeStyle` types: flat colors (`.primary`, `.red`), hierarchical styles (`.primary`, `.secondary`), materials (`.ultraThinMaterial`), gradients, and more.

---

## Testing Dark Mode

- **Xcode Canvas:** Toggle dark mode variant in the preview assistant editor
- **Simulator:** Settings → Developer → Dark Appearance toggle
- **Device:** Control Center → Brightness → Dark Mode, or Settings → Display & Brightness
