# WCAG Contrast Check: #6B7280 on #F9FAFB

## Color Values

- **Text color**: #6B7280 (Tailwind's `gray-500` — a medium gray)
- **Background color**: #F9FAFB (Tailwind's `gray-50` — a near-white)

## Contrast Ratio Calculation

To calculate the WCAG contrast ratio, we need the relative luminance of each color using the WCAG 2.1 formula.

### Step 1: Convert hex to linear RGB

For each channel, divide by 255, then apply the linearization formula:
- If value <= 0.04045: `linear = value / 12.92`
- If value > 0.04045: `linear = ((value + 0.055) / 1.055) ^ 2.4`

**#6B7280 (text)**
- R: 0x6B = 107 → 107/255 = 0.4196 → ((0.4196 + 0.055) / 1.055)^2.4 ≈ 0.1329
- G: 0x72 = 114 → 114/255 = 0.4471 → ((0.4471 + 0.055) / 1.055)^2.4 ≈ 0.1591
- B: 0x80 = 128 → 128/255 = 0.5020 → ((0.5020 + 0.055) / 1.055)^2.4 ≈ 0.2154

Luminance (L1) = 0.2126 × 0.1329 + 0.7152 × 0.1591 + 0.0722 × 0.2154
             = 0.02824 + 0.11381 + 0.01555
             ≈ **0.1576**

**#F9FAFB (background)**
- R: 0xF9 = 249 → 249/255 = 0.9765 → ((0.9765 + 0.055) / 1.055)^2.4 ≈ 0.9529
- G: 0xFA = 250 → 250/255 = 0.9804 → ((0.9804 + 0.055) / 1.055)^2.4 ≈ 0.9567
- B: 0xFB = 251 → 251/255 = 0.9843 → ((0.9843 + 0.055) / 1.055)^2.4 ≈ 0.9605

Luminance (L2) = 0.2126 × 0.9529 + 0.7152 × 0.9567 + 0.0722 × 0.9605
              = 0.20258 + 0.68432 + 0.06934
              ≈ **0.9562**

### Step 2: Calculate contrast ratio

Contrast ratio = (L_lighter + 0.05) / (L_darker + 0.05)
              = (0.9562 + 0.05) / (0.1576 + 0.05)
              = 1.0062 / 0.2076
              ≈ **4.85:1**

## WCAG Pass/Fail Results

| Criterion | Requirement | Result |
|-----------|-------------|--------|
| WCAG AA — Normal text (< 18pt / < 14pt bold) | 4.5:1 minimum | **PASS** (4.85:1) |
| WCAG AA — Large text (≥ 18pt or ≥ 14pt bold) | 3.0:1 minimum | **PASS** (4.85:1) |
| WCAG AA — UI components & graphical objects | 3.0:1 minimum | **PASS** (4.85:1) |
| WCAG AAA — Normal text | 7.0:1 minimum | **FAIL** (4.85:1) |
| WCAG AAA — Large text | 4.5:1 minimum | **PASS** (4.85:1) |

## Summary

The combination of **#6B7280 on #F9FAFB produces a contrast ratio of approximately 4.85:1**.

- It **passes WCAG 2.1 Level AA** for normal-sized body text — but only marginally (the threshold is 4.5:1, so there is about 0.35 of headroom).
- It **fails WCAG 2.1 Level AAA** for normal text (requires 7.0:1).
- It is commonly seen in Tailwind-based UIs (gray-500 on gray-50) for secondary/muted text.

## Recommendations

1. **If targeting strict AA compliance for body text**: The color passes, but the margin is slim. Any slight rendering variation (sub-pixel antialiasing, screen calibration) could make the text feel harder to read in practice. Consider using a slightly darker gray like **#4B5563** (Tailwind `gray-600`) which produces a ratio of approximately **7.0:1** — satisfying AAA as well.

2. **If this is used for placeholder or disabled-state text**: WCAG explicitly allows lower contrast for placeholder/inactive UI text, so your current values are fine in that context.

3. **For large text (18pt+ or bold 14pt+)**: Your current combination passes both AA and AAA — no changes needed for headings.

4. **Recommended accessible alternatives for normal body text (AA-safe with margin)**:
   - `#4B5563` (#4B5563) on `#F9FAFB` → ~7.0:1 (AAA)
   - `#374151` on `#F9FAFB` → ~10.0:1 (AAA, high contrast)

## Tools to Verify Independently

- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Colour Contrast Analyser (desktop app)](https://www.tpgi.com/color-contrast-checker/)
- Browser DevTools: Chrome/Firefox accessibility panel shows contrast ratios on selected elements
