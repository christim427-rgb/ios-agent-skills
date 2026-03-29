# iOS Localization Skill

Production-grade localization skill for iOS codebases. Corrects 30+ AI failure patterns — from missing Slavic plural categories to hardcoded left/right constraints that shatter RTL layouts — and enforces correct localization from the start.

## Benchmark Results

Tested on **36 scenarios** with **103 assertions** across 10 topics.

### Results Summary

| Model | With Skill | Without Skill | Delta | A/B Quality |
| --- | --- | --- | --- | --- |
| **Sonnet 4.6** | 103/103 (100%) | 101/103 (98.1%) | **+1.9%** | **27W 0L 9T** (avg 8.8 vs 7.9) |

> Delta = percentage point improvement in discriminating assertion pass rate. A/B Quality: blind judge scores each response 0-10.

### Results (Sonnet 4.6)

| Metric | Value |
| --- | --- |
| With Skill | **103/103 (100%)** |
| Without Skill | 101/103 (98.1%) |
| Delta | **+1.9%** |
| Discriminating assertions | 2 (WITH wins), 0 (WITHOUT wins) |
| A/B Quality | **27W 0L 9T** (avg 8.8 vs 7.9) |

**Interpretation:** Sonnet 4.6 already has strong iOS localization knowledge — the baseline passes 98.1% of assertions. The skill's discriminating value concentrates in niche Xcode-specific details (comment order randomization bug in .xcstrings) and precise Slavic plural rule boundaries (Polish vs Russian number 21 mapping). However, the A/B quality scoring shows the skill consistently produces better responses (27 wins, 0 losses) — the advantage is in depth, edge case coverage, and practical examples rather than missing core knowledge.

### Key Discriminating Assertions

| ID | Topic | Assertion | Why It Matters |
| --- | --- | --- | --- |
| PL2.2 | pluralization | Number 21 maps to 'one' in Russian but 'many' in Polish | Precise cross-language difference |
| SC2.3 | string-catalogs | Xcode comment order randomization bug causing false diffs | Niche Xcode-specific knowledge |

---

## What This Skill Changes

| Without Skill | With Skill |
| --- | --- |
| Only one/other plural categories (breaks Russian, Polish, Arabic) | All CLDR-required categories per language |
| Concatenated string fragments ("Hello, " + name) | Format strings with positional specifiers |
| Custom dateFormat for user-facing dates | System styles (Date.formatted, .dateStyle) |
| Left/right constraints (breaks Arabic, Hebrew) | Leading/trailing constraints everywhere |
| Hardcoded English accessibility labels | Localized accessibility strings |
| Manual .strings file creation | String Catalogs with auto-extraction |
| Direct .xcstrings editing (breaks on large files) | Python scripts for programmatic operations |

## What It Does

- Intercepts 30 documented AI localization failure patterns
- Enforces CLDR-correct pluralization for all supported languages
- Provides Python scripts for .xcstrings validation, editing, and plural auditing
- Covers String Catalogs, SwiftUI/UIKit APIs, date/number/currency formatting
- Handles RTL layout, accessibility localization, and enterprise patterns
- Maps to CLDR specifications and Apple documentation

## Coverage

| Area | SwiftUI | UIKit |
|---|---|---|
| String Catalogs (.xcstrings) | Full | Full |
| CLDR Pluralization (Slavic, Arabic, CJK) | Full | Full |
| Date/Number/Currency Formatting | Full | Full |
| RTL Layout (Arabic, Hebrew) | Full | Full |
| Accessibility String Localization | Full | Full |
| Swift Package Bundle Management | Full | Full |
| Enterprise (White-label, Modular) | Full | Full |
| Testing (Pseudolanguages, CI) | Full | Full |

## Structure

```
ios-localization/
├── SKILL.md                           — Decision trees, workflows, 17 critical rules
├── scripts/
│   └── xcstrings_tool.py             — Validate, add keys, audit plurals, fix plurals
└── references/
    ├── rules.md                       — All 30 rules ranked by severity
    ├── ai-failure-patterns.md         — 30 failure patterns with ❌/✅ code pairs
    ├── string-catalogs.md             — .xcstrings format, pitfalls, Xcode 26 features
    ├── pluralization.md               — CLDR categories, Russian vs Polish, test sets
    ├── swiftui-localization.md        — LocalizedStringKey, verbatim, packages
    ├── formatting.md                  — Date, number, currency formatting
    ├── rtl-layout.md                  — Leading/trailing, semantic content, exceptions
    ├── enterprise-patterns.md         — Modular apps, white-label, accessibility
    └── testing.md                     — Pseudolanguages, launch arguments, CI
```

## Companion Skills

| Skill | Use When |
|---|---|
| `ios-accessibility` | Accessibility labels need localization |
| `swiftui-mvvm` | Localized ViewModels and state management |
| `ios-testing` | Locale-specific test automation |
| `ios-security` | Format string vulnerabilities in localized strings |
