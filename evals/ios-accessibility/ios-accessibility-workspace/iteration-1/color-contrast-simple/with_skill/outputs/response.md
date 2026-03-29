# Accessibility Problem: Hardcoded Colors

### [HIGH] Hardcoded colors break dark mode and accessibility settings

**WCAG:** 1.4.3 Contrast (Minimum) — AA | **HIG:** Use semantic colors that adapt to appearance modes
**Issue:** Both `.foregroundColor(.black)` and `.background(Color.white)` are hardcoded absolute colors. They will not adapt to dark mode, increased contrast mode, or smart invert. In dark mode, a white background with black text inverts the expected appearance and may create visual problems depending on the surrounding UI context. More critically, this pattern is a known AI failure mode (F3) because it ignores the system's dynamic color environment entirely.

**VoiceOver Impact:** VoiceOver itself is not directly affected by color choices, but users who rely on VoiceOver often also use dark mode or increased contrast — both of which this code ignores. There is no redundant non-color indicator of meaning, so any semantic intent carried by the white/black color pair is lost to users with color vision deficiencies.

**Additional Issue — Deprecated API (F4):** `.foregroundColor()` is deprecated as of iOS 17. The modern replacement is `.foregroundStyle()`.

**Fix:**

```swift
// ❌ Current — hardcoded absolute colors + deprecated modifier
Text("Hello").foregroundColor(.black)
    .background(Color.white)

// ✅ Corrected — semantic colors that adapt to dark mode, increased contrast, and smart invert
Text("Hello")
    .foregroundStyle(.primary)                    // adapts: black in light, white in dark
    .background(Color(.systemBackground))         // adapts: white in light, black in dark
```

**Why `.primary` and `Color(.systemBackground)`?**

| Property | `.black` / `Color.white` | `.primary` / `Color(.systemBackground)` |
|---|---|---|
| Light mode | Black on white | Black on white |
| Dark mode | Black on white (wrong — illegible against dark surrounds) | White on black (correct) |
| Increased Contrast | No change | Automatically increases contrast |
| Smart Invert | Inverted incorrectly | Adapts correctly |

**Contrast note:** Pure black (`#000000`) on pure white (`#FFFFFF`) technically achieves a 21:1 contrast ratio — far exceeding the WCAG AA requirement of 4.5:1 for normal text. However, passing raw contrast math in one appearance mode does not exempt code from using semantic colors. The real failure is that this code breaks in dark mode and ignores the iOS dynamic color system. Always use semantic colors; let the system handle contrast adaptation across all modes.

**Checklist after fixing:**

- [ ] No hardcoded `.black`, `.white`, or other absolute SwiftUI/UIKit colors for text or backgrounds
- [ ] `.foregroundStyle()` used instead of deprecated `.foregroundColor()`
- [ ] Contrast verified in both light AND dark mode (use Xcode Accessibility Inspector)
- [ ] `@Environment(\.colorSchemeContrast)` checked if the view needs explicit high-contrast variants
