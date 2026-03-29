# iOS Accessibility Skill

Production-grade accessibility skill for iOS codebases. Corrects the systematic accessibility failures that AI coding assistants produce — hardcoded fonts, `onTapGesture` instead of `Button`, missing labels, no system preference checks — and enforces accessible output from the start.

## Benchmark Results

Tested on **36 scenarios** with **115 discriminating assertions** across 12 topics.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 115/115 (100%) | 94/115 (81.7%) | **+18.3%** | **35W 0T 1L** (avg 8.9 vs 7.4) |
| **GPT-5.4** | — | — | — | — |
| **Gemini 3.1 Pro** | — | — | — | — |

> Delta = percentage point improvement in discriminating assertion pass rate (with skill vs without skill). A/B Quality: blind judge scores each response 0–10. "—" = not yet benchmarked.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | **115/115 (100%)** |
| Without Skill | 94/115 (81.7%) |
| Delta | **+18.3%** |
| Discriminating assertions | 21 (WITH wins), 0 (WITHOUT wins) |
| A/B Quality | **35W 0T 1L** (avg 8.9 vs 7.4) |

**Interpretation:** The skill achieves perfect pass rate (100%) across all 115 assertions. The baseline misses 21 assertions — concentrated in WCAG 2.2 new criteria, system preference checks (legibilityWeight, colorSchemeContrast, reduceTransparency), @ScaledMetric for icons, Screen Curtain testing, Large Content Viewer patterns, and accessibilityPerformEscape for modal dismiss.

### Topic Breakdown

| Topic | With Skill | Without Skill | Delta | Assertions |
| --- | --- | --- | --- | --- |
| wcag-mapping | 100.0% | 66.7% | **+33.3%** | 9 |
| dynamic-type | 100.0% | 70.0% | **+30.0%** | 10 |
| motion-preferences | 100.0% | 70.0% | **+30.0%** | 10 |
| swiftui-controls | 100.0% | 70.0% | **+30.0%** | 10 |
| system-preferences | 100.0% | 77.8% | **+22.2%** | 9 |
| voiceover-actions | 100.0% | 80.0% | **+20.0%** | 10 |
| voiceover-labels | 100.0% | 80.0% | **+20.0%** | 10 |
| voiceover-grouping | 100.0% | 88.9% | **+11.1%** | 9 |
| voiceover-traits | 100.0% | 88.9% | **+11.1%** | 9 |
| color-contrast | 100.0% | 90.0% | **+10.0%** | 10 |
| testing | 100.0% | 100.0% | 0.0% | 9 |
| uikit-controls | 100.0% | 100.0% | 0.0% | 10 |

### Key Discriminating Assertions (21 — missed WITHOUT skill, all passed WITH)

| ID | Topic | Assertion | Why It Matters |
| --- | --- | --- | --- |
| VL2.2 | voiceover-labels | Hides individual star images from VoiceOver | Stars should not be separate VO stops |
| VL3.4 | voiceover-labels | Custom action closures return Bool | Correct API signature |
| VT3.1 | voiceover-traits | Replace onTapGesture in custom stepper | Element invisible to all AT |
| VG1.3 | voiceover-grouping | .ignore + custom label for natural sentences | .combine produces awkward pauses |
| VA2.3 | voiceover-actions | Announcements lost if VO speaking | Critical timing gotcha |
| VA3.4 | voiceover-actions | accessibilityPerformEscape for dismiss | Two-finger Z gesture |
| DT1.3 | dynamic-type | 25%+ of users change text size | Motivates compliance |
| DT2.3 | dynamic-type | numberOfLines = 0 for text wrapping | UIKit anti-pattern |
| DT3.3 | dynamic-type | @ScaledMetric for icon dimensions | Non-text scaling |
| CC3.3 | color-contrast | Test contrast for both light AND dark | Independent verification |
| MP1.2 | motion-preferences | Replace with crossfade, not remove all animation | UX principle |
| MP3.1 | motion-preferences | reduceTransparency → solid background | Material replacement |
| MP3.5 | motion-preferences | accessibilityIgnoresInvertColors for photos | Smart Invert |
| SC1.1 | swiftui-controls | onTapGesture invisible to VO/Switch Control | #1 AI failure |
| SC2.2 | swiftui-controls | .isToggle trait for custom toggles | iOS 17+ semantics |
| SC3.3 | swiftui-controls | textContentType for autofill | WCAG 1.3.5 |
| WC2.1 | wcag-mapping | WCAG 2.5.7 Dragging (new in 2.2) | AI trained on older WCAG |
| WC2.3 | wcag-mapping | Target size 24pt WCAG / 44pt Apple HIG | WCAG 2.5.8 |
| WC3.3 | wcag-mapping | Criteria that DON'T apply to native iOS | Avoids web-only auditing |
| SP3.2 | system-preferences | accessibilityIgnoresInvertColors cascades to subviews | Parent cascade behavior |
| SP3.4 | system-preferences | .dynamicTypeSize cap + Large Content Viewer | Combined fallback pattern |

### Benchmark Cost Estimate

| Step | Formula | Tokens |
| --- | --- | --- |
| Eval runs (with_skill) | 36 × 35k | 1,260k |
| Eval runs (without_skill) | 36 × 12k | 432k |
| Grading (72 runs × 5k) | 72 × 5k | 360k |
| **Total** | | **~2.1M** |
| **Est. cost (Sonnet 4.6)** | ~$5.4/1M | **~$11** |

---

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| onTapGesture for interactive elements (invisible to VoiceOver) | Button with accessibilityLabel for all interactive elements |
| Hardcoded font sizes (.system(size:)) | Dynamic Type text styles that scale |
| Hardcoded colors (.black, .white) | Semantic colors adapting to dark mode |
| No accessibility on custom controls | Labels, values, traits, and adjustable actions |
| No system preference checks | Reduce motion, contrast, transparency, color |
| Generic WCAG advice | iOS-specific API mapping for each criterion |

## What It Does

- Intercepts 11 documented AI failure patterns before they reach production
- Generates VoiceOver-compatible SwiftUI and UIKit code by default
- Enforces Dynamic Type, semantic colors, and proper element grouping
- Maps iOS APIs to WCAG 2.2 AA success criteria
- Provides accessibility review workflows with severity-ranked findings
- Covers enterprise compliance (ADA, EAA, Section 508, VPAT)

## When It Triggers

- Creating new iOS views or screens
- Reviewing existing code for accessibility
- Adding VoiceOver, Dynamic Type, or contrast support
- Auditing WCAG compliance
- Preparing apps for enterprise or government deployment
- Any mention of "make this accessible", "VoiceOver", "a11y"

## Coverage

| Area | SwiftUI | UIKit |
|---|---|---|
| VoiceOver (labels, traits, grouping, actions, rotors) | Full | Full |
| Dynamic Type (text styles, layout adaptation) | Full | Full |
| Color & Contrast (WCAG ratios, dark mode, color blindness) | Full | Full |
| Motion & Animation (reduce motion, flash safety) | Full | Full |
| Alternative Input (Switch Control, Voice Control, Keyboard) | Full | Full |
| iOS 17/18/26 new APIs | Full | Partial |
| WCAG 2.2 AA mapping | Full | Full |
| Testing (Xcode audit, XCTest, CI) | Full | Full |
| Compliance (ADA, EAA, Section 508, VPAT) | Full | Full |

## Structure

```
ios-accessibility/
├── SKILL.md                           — Decision trees, workflows, critical rules
└── references/
    ├── rules.md                       — Priority rules and do's/don'ts
    ├── ai-failure-patterns.md         — 11 AI failure patterns with code pairs
    ├── voiceover-patterns.md          — Labels, hints, traits, grouping, actions
    ├── swiftui-patterns.md            — All SwiftUI accessibility modifiers
    ├── uikit-patterns.md              — UIKit elements, containers, traits
    ├── dynamic-type.md                — UIFontMetrics, @ScaledMetric, layout
    ├── color-visual.md                — Contrast, color blindness, dark mode
    ├── motion-input.md                — Reduce motion, Switch/Voice Control
    ├── wcag-ios-mapping.md            — WCAG 2.2 → iOS API mapping
    ├── testing.md                     — Xcode audit, XCTest, VoiceOver, CI
    ├── ios-new-features.md            — iOS 17/18/26 new APIs
    └── compliance.md                  — Legal, VPAT, enterprise requirements
```

## Companion Skills

| Skill | Use When |
|---|---|
| `swiftui-mvvm` | ViewModels managing accessibility state |
| `ios-security` | Biometric auth with VoiceOver feedback |
| `ios-testing` | XCTest accessibility audit integration |
| `swift-concurrency` | VoiceOver notifications from async contexts |
