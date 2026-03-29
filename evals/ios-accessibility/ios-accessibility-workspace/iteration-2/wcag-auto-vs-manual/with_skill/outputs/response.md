# WCAG 2.2 Criteria: Auto-Handled vs Manual in iOS

## Automatically Handled by Standard Controls

When you use standard UIKit/SwiftUI controls (`Button`, `Toggle`, `TextField`, `List`, `TabView`, `Alert`), these criteria are satisfied without any additional code:

| WCAG | Criterion | Why It's Handled Automatically |
|---|---|---|
| **4.1.2** | Name, Role, Value | Standard controls auto-set accessibility traits (`.isButton`, `.isToggle`), labels from title text, and values from state. `Toggle` announces "On"/"Off" automatically. |
| **2.5.2** | Pointer Cancellation | UIKit fires action on `.touchUpInside` (finger lifted inside), not on touch-down. Users can cancel by sliding finger off-target before releasing. |
| **2.1.1 / 2.1.2** | Keyboard / No Keyboard Trap | Standard controls are operable via VoiceOver linear navigation, Switch Control scanning, and hardware keyboard. Focus is not trapped. |
| **3.1.1** | Language of Page | iOS respects `NSLocale` and the device language setting. VoiceOver selects the correct voice. |
| **3.2.1 / 3.2.2** | On Focus / On Input | Standard controls don't trigger navigation changes or context shifts on focus. A `TextField` gaining focus doesn't navigate away. |
| **1.3.2** | Meaningful Sequence | Default VoiceOver reading order follows top-to-bottom, left-to-right layout order — matching visual order. |

## Requires Manual Implementation

These criteria are your responsibility as a developer:

| WCAG | Criterion | Required iOS API | Priority |
|---|---|---|---|
| **1.1.1** | Non-text Content | `accessibilityLabel` on images; `Image(decorative:)` or `.accessibilityHidden(true)` for decorative images | 🔴 CRITICAL |
| **1.3.1** | Info and Relationships | `.accessibilityAddTraits(.isHeader)` on headings; `.accessibilityElement(children:)` for grouping; `accessibilityElements` for tables | 🟡 HIGH |
| **1.4.3** | Contrast (Minimum) | 4.5:1 normal text, 3:1 large text — use semantic colors and test in both light and dark mode | 🟡 HIGH |
| **1.4.4** | Resize Text | `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory = true`; never `.system(size:)` | 🟡 HIGH |
| **1.4.10** | Reflow | Dynamic Type at accessibility sizes + HStack→VStack layout adaptation; `ViewThatFits` | 🟡 HIGH |
| **2.4.6** | Headings and Labels | `.accessibilityAddTraits(.isHeader)` on section headings — enables VoiceOver rotor heading navigation | 🟡 HIGH |
| **2.5.3** | Label in Name | `accessibilityLabel` must contain any visible text on the control (critical for Voice Control) | 🟡 HIGH |
| **4.1.2** (custom controls) | Name, Role, Value | Custom controls need all three: label + trait + value | 🔴 CRITICAL |

## Criteria That Do NOT Apply to Native iOS Apps

| WCAG | Criterion | Why Not Applicable |
|---|---|---|
| **4.1.1** | Parsing | Marked as "always satisfied" in the 2023 WCAG errata. Originally for malformed HTML — not relevant to native compiled apps. |
| **2.4.1** | Bypass Blocks | Intended for web pages where "skip to content" links bypass repeated navigation. Within a native app, navigation is already per-screen — this pattern doesn't apply. |
| **1.4.12** | Text Spacing | Applies only to markup-based content (HTML/CSS in WebViews). Native SwiftUI/UIKit layouts are not affected by CSS text-spacing overrides. |

## WCAG 2.2 New Criteria (Not in 2.1)

These are brand-new in WCAG 2.2 — added in 2023:

| Criterion | Requirement | iOS Implementation |
|---|---|---|
| **2.4.11** Focus Not Obscured (AA) | Keyboard-focused element not fully hidden by sticky headers/footers | Ensure focused elements scroll into view |
| **2.4.13** Focus Appearance (AAA) | 3:1 contrast ratio for custom focus indicators | Custom focus rings on non-standard controls |
| **2.5.7** Dragging Movements (AA) | Non-drag alternative for all drag operations | `accessibilityCustomActions` for reorder, resize |
| **2.5.8** Target Size Minimum (AA) | 24×24pt minimum touch target (Apple HIG: 44×44pt) | `.frame(minWidth: 44, minHeight: 44)` |
| **3.2.6** Consistent Help (A) | Help mechanism in same relative position on each screen | Consistent help button placement across views |
| **3.3.7** Redundant Entry (A) | Don't ask for info already entered in the same session | `textContentType` autofill; pre-populate fields |
| **3.3.8** Accessible Authentication (AA) | Support password managers, paste, biometrics | `.password` textContentType; never block paste |

## Decision Summary

```
Standard control (Button, Toggle, List, Alert)?
├── YES → 4.1.2, 2.5.2, 2.1.1 handled automatically
└── NO (custom control) → Must manually implement:
    ├── accessibilityLabel (1.1.1, 4.1.2)
    ├── trait (4.1.2)
    ├── accessibilityValue for stateful controls (4.1.2)
    └── accessibilityCustomActions for drag alternatives (2.5.7)

Hardcoded font sizes? → Violates 1.4.4 — use Dynamic Type
No heading traits? → Violates 1.3.1 — add .isHeader
Color-only status? → Violates 1.4.1 — add icons/text
```
