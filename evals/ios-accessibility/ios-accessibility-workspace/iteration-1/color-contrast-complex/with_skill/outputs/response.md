# WCAG Contrast Check: #6B7280 on #F9FAFB

## Result Summary

**Contrast ratio: 4.63:1**

| WCAG Level | Text Size | Required Ratio | Result |
|---|---|---|---|
| AA (required) | Normal text (<18pt / <14pt bold) | 4.5:1 | PASS |
| AA (required) | Large text (18pt+ / 14pt+ bold) | 3:1 | PASS |
| AAA (enhanced) | Normal text | 7:1 | FAIL |
| AAA (enhanced) | Large text | 4.5:1 | PASS |

**Your color scheme passes WCAG 2.2 AA for normal text — but only barely, with a margin of 0.13.**

---

## How the Ratio Was Calculated

WCAG contrast uses relative luminance per the sRGB linearization formula:

```
Linearize each channel:
  c <= 0.03928  →  c / 12.92
  c >  0.03928  →  ((c + 0.055) / 1.055) ^ 2.4

Luminance = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin

Contrast ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

**#6B7280** (RGB 107, 114, 128) → luminance: **0.1672**
**#F9FAFB** (RGB 249, 250, 251) → luminance: **0.9548**

Ratio: (0.9548 + 0.05) / (0.1672 + 0.05) = **4.63:1**

---

## Key Concerns

### 1. The margin is razor-thin for normal text

AA requires 4.5:1. You're at 4.63:1 — a margin of only 0.13. Any of the following will push you below the threshold:

- Anti-aliasing at certain font weights renders the effective contrast slightly lower
- Rendering on certain display profiles (P3, non-calibrated screens) shifts perceived contrast
- Translucent backgrounds (e.g., a blur material under your surface) drop luminance in unpredictable ways

**Recommendation:** For body text, body copy, form labels, or any text users need to read at length, treat this as a borderline case, not a comfortable pass.

### 2. The "Increase Contrast" accessibility setting will expose the gap

iOS users who enable **Settings > Accessibility > Display & Text Size > Increase Contrast** expect noticeably higher contrast than the default. Your current palette does not accommodate this setting — the system will not auto-boost hardcoded hex values.

You should provide a higher-contrast variant and respond to the trait:

```swift
// SwiftUI
@Environment(\.colorSchemeContrast) var contrast

Text("Label")
    .foregroundStyle(
        contrast == .increased
            ? Color(red: 0.24, green: 0.27, blue: 0.33)  // e.g. #3D4454 — ~7:1 on F9FAFB
            : Color(red: 0.42, green: 0.45, blue: 0.50)  // #6B7280 — 4.63:1 on F9FAFB
    )

// UIKit
if traitCollection.accessibilityContrast == .high {
    label.textColor = UIColor(red: 0.24, green: 0.27, blue: 0.33, alpha: 1)
} else {
    label.textColor = UIColor(red: 0.42, green: 0.45, blue: 0.50, alpha: 1)
}
```

Alternatively, define both variants in the Xcode asset catalog under the color's "High Contrast" slot — the system selects the right value automatically.

### 3. Dark mode needs a separate audit

This analysis covers only the light mode pairing. Your dark mode equivalent must be independently verified. The #F9FAFB background will likely become a dark surface (~#111827 or similar) in dark mode, and your text color must be re-evaluated against that background. Using semantic colors avoids this entirely:

```swift
// ❌ Hardcoded — only valid in light mode
Text("Status")
    .foregroundStyle(Color(hex: "#6B7280"))
    .background(Color(hex: "#F9FAFB"))

// ✅ Semantic — adapts to dark mode and high contrast automatically
Text("Status")
    .foregroundStyle(.secondary)
    .background(Color(.systemBackground))
```

`UIColor.secondaryLabel` on `UIColor.systemBackground` achieves approximately the same visual appearance as your custom palette in light mode, while automatically providing passing contrast in dark mode and respecting the Increase Contrast setting.

### 4. iOS-specific severity classification

Per the ios-accessibility skill severity model:

- Using hardcoded hex colors for text/background is a **HIGH severity** issue
- It breaks under two system accessibility settings: Increase Contrast (HIGH) and Smart Invert Colors (visual corruption if not handled)
- It is not CRITICAL (content is still visible to VoiceOver), but it is a known AI failure pattern (F3) that must be addressed before release in regulated contexts

---

## What to Do

**If you must keep custom brand colors** (cannot use semantic colors):

1. Verify the ratio passes on both light and dark backgrounds independently
2. Provide a high-contrast asset catalog variant (7:1 target for AAA, minimum 4.5:1)
3. Respond to `colorSchemeContrast == .increased` / `accessibilityContrast == .high`
4. Keep the current light-mode pairing as-is — it passes AA

**If this is UI chrome or secondary text** (captions, placeholders, metadata):

Secondary text is often intentionally lower contrast to establish visual hierarchy. WCAG exempts disabled controls and placeholder text, but not secondary body content. If users need to read this text to understand or operate the interface, the 4.5:1 requirement applies.

**If this text is large (18pt+ regular or 14pt+ bold):**

The 3:1 threshold applies. Your 4.63:1 passes with significant headroom. This is the one scenario where your current palette is genuinely safe.

---

## Swift Contrast Utility (from color-visual.md)

The ios-accessibility reference includes a `UIColor` extension you can drop into any project to verify contrast programmatically and catch regressions in unit tests:

```swift
extension UIColor {
    var relativeLuminance: CGFloat {
        var r: CGFloat = 0, g: CGFloat = 0, b: CGFloat = 0
        getRed(&r, green: &g, blue: &b, alpha: nil)
        func linearize(_ c: CGFloat) -> CGFloat {
            c <= 0.03928 ? c / 12.92 : pow((c + 0.055) / 1.055, 2.4)
        }
        return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)
    }

    func contrastRatio(with color: UIColor) -> CGFloat {
        let l1 = max(relativeLuminance, color.relativeLuminance)
        let l2 = min(relativeLuminance, color.relativeLuminance)
        return (l1 + 0.05) / (l2 + 0.05)
    }

    func meetsWCAG_AA(against bg: UIColor, isLargeText: Bool = false) -> Bool {
        contrastRatio(with: bg) >= (isLargeText ? 3.0 : 4.5)
    }
}

// Usage
let text = UIColor(red: 0.42, green: 0.45, blue: 0.50, alpha: 1) // #6B7280
let bg   = UIColor(red: 0.98, green: 0.98, blue: 0.98, alpha: 1) // #F9FAFB
assert(text.meetsWCAG_AA(against: bg), "Contrast regression: text on background fails AA")
```

---

## Verdict

| Scenario | Passes AA? | Passes AAA? | Recommendation |
|---|---|---|---|
| Normal body text in light mode | Yes (4.63:1) | No (needs 7:1) | Borderline pass — provide high-contrast variant |
| Large text (18pt+) in light mode | Yes (4.63:1) | Yes (4.63 >= 4.5) | Safe |
| Normal text in dark mode | Not verified | Not verified | Audit dark mode independently |
| With "Increase Contrast" enabled | Not accommodated | Not accommodated | Add high-contrast color variant |

Your custom scheme passes the WCAG 2.2 AA minimum for normal text in light mode. For a production iOS app — especially one targeting enterprise, government, or regulated industries — you should also handle the Increase Contrast system setting and verify dark mode. Switching to semantic colors (`Color.secondary` / `UIColor.secondaryLabel`) is the lowest-effort path to full compliance across all system configurations.
