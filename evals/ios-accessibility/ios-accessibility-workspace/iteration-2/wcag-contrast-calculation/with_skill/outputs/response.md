# WCAG Contrast Verification: #6B7280 on #F9FAFB

## WCAG AA Contrast Requirement

**Normal text:** minimum ratio of **4.5:1**
**Large text (18pt+ or 14pt+ bold):** minimum ratio of **3:1**
**UI components and icons:** minimum ratio of **3:1**

---

## Color Values

| Role | Hex | RGB |
|---|---|---|
| Foreground (text) | `#6B7280` | (107, 114, 128) |
| Background | `#F9FAFB` | (249, 250, 251) |

---

## Contrast Ratio Calculation

WCAG uses **relative luminance** based on the sRGB color space.

### Step 1: Calculate Relative Luminance

The formula linearizes each channel: `c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ^ 2.4`

Then: `L = 0.2126 * R + 0.7152 * G + 0.0722 * B`

**Foreground `#6B7280`:**
- R: 107/255 = 0.4196 → linearized: ((0.4196 + 0.055) / 1.055)^2.4 = 0.1448
- G: 114/255 = 0.4471 → linearized: ((0.4471 + 0.055) / 1.055)^2.4 = 0.1620
- B: 128/255 = 0.5020 → linearized: ((0.5020 + 0.055) / 1.055)^2.4 = 0.2158
- **L(foreground) = 0.2126 × 0.1448 + 0.7152 × 0.1620 + 0.0722 × 0.2158 ≈ 0.1534**

**Background `#F9FAFB`:**
- R: 249/255 = 0.9765 → linearized: ((0.9765 + 0.055) / 1.055)^2.4 = 0.9529
- G: 250/255 = 0.9804 → linearized: ((0.9804 + 0.055) / 1.055)^2.4 = 0.9573
- B: 251/255 = 0.9843 → linearized: ((0.9843 + 0.055) / 1.055)^2.4 = 0.9617
- **L(background) = 0.2126 × 0.9529 + 0.7152 × 0.9573 + 0.0722 × 0.9617 ≈ 0.9521**

### Step 2: Contrast Ratio

`ratio = (L_lighter + 0.05) / (L_darker + 0.05)`
`ratio = (0.9521 + 0.05) / (0.1534 + 0.05)`
`ratio = 1.0021 / 0.2034`
`ratio ≈ 4.49:1`

---

## Verdict

| Text Size | Required | Actual | Pass/Fail |
|---|---|---|---|
| Normal text (< 18pt regular, < 14pt bold) | 4.5:1 | ~4.49:1 | **FAIL** (just below threshold) |
| Large text (18pt+ regular or 14pt+ bold) | 3:1 | ~4.49:1 | **PASS** |
| UI components / icons | 3:1 | ~4.49:1 | **PASS** |

**`#6B7280` on `#F9FAFB` fails WCAG AA for normal-sized body text.** The ratio of approximately 4.49:1 falls just below the 4.5:1 requirement. This is a common Tailwind Gray palette combination (`gray-500` on `gray-50`) that many developers assume passes.

---

## Test Both Light AND Dark Mode

The above calculation covers light mode. In dark mode your colors will be different — if you hardcode `#6B7280` and `#F9FAFB`, dark mode doesn't change them. With semantic system colors, iOS provides dark mode variants automatically.

If you're using custom colors in both modes, verify:
- Light mode foreground on light background ← tested above
- Dark mode foreground on dark background ← separate check required

Use an asset catalog with "Any Appearance" + "Dark Appearance" variants, or a tool like Stark/Contrast to verify both.

---

## Increase Contrast Mode: 7:1 Target

When **Settings → Accessibility → Display & Text Size → Increase Contrast** is enabled, the system signals that the user needs higher contrast. For these users, the WCAG AAA target of **7:1** for normal text is the appropriate goal.

Check for this in your app:

```swift
// SwiftUI
@Environment(\.colorSchemeContrast) var contrast

var textColor: Color {
    contrast == .increased ? Color(hex: "#374151") : Color(hex: "#6B7280")
    // gray-700 on gray-50 = ~10:1 ratio ✅
}
```

```swift
// UIKit
if traitCollection.accessibilityContrast == .high {
    label.textColor = UIColor(hex: "#374151")  // Much higher contrast
} else {
    label.textColor = UIColor(hex: "#6B7280")
}
```

Or use asset catalogs with "High Contrast" variants to provide dark/thick variants automatically.

---

## Fix Options

| Option | Hex | Ratio on #F9FAFB | Normal Text |
|---|---|---|---|
| Use gray-600 | `#4B5563` | ~7.0:1 | **PASS (AA + AAA)** |
| Use gray-700 | `#374151` | ~10.0:1 | **PASS (AA + AAA)** |
| Use `.secondary` semantic color | System-defined | System-verified | Auto-adapts |

The simplest fix for a SwiftUI app is to use `.secondary` (`Color.secondary` or `.foregroundStyle(.secondary)`) which Apple verifies passes contrast requirements in all system appearances.

---

## Verification Tools

- **Xcode Accessibility Inspector** — Color Contrast Calculator tab
- **Apple Color Contrast Calculator** (macOS app)
- **WebAIM Contrast Checker** (web) — `webaim.org/resources/contrastchecker`
- **Stark** (Figma/Sketch plugin) — checks designs before implementation
- In code: `UIColor.contrastRatio(with:)` extension (see `references/color-visual.md`)
