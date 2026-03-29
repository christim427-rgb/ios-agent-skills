# How to Run an Automated Accessibility Audit in XCTest UI Tests

## Overview

XCTest's built-in accessibility audit (`performAccessibilityAudit`) is available since Xcode 15. It runs automated checks against live UI in the simulator as part of your UI test suite — no extra tools required.

---

## Basic Setup

### 1. Full Audit on App Launch

The simplest approach: launch the app and audit the entire screen.

```swift
func testAccessibility() throws {
    let app = XCUIApplication()
    app.launch()
    try app.performAccessibilityAudit()
}
```

This runs all audit categories and fails the test if any issue is found.

---

### 2. Selective Audit — Specific Categories

To focus on particular concern areas, pass a set of audit types:

```swift
try app.performAccessibilityAudit(for: [
    .contrast,
    .dynamicType,
    .sufficientElementDescription
])
```

**Available audit types:**

| Type | What It Checks |
|---|---|
| `.contrast` | Text/background contrast ratio (WCAG 1.4.3) |
| `.dynamicType` | Fonts respond to Dynamic Type size changes |
| `.sufficientElementDescription` | Elements have meaningful, non-empty labels |
| `.hitRegion` | Touch targets meet the 44×44pt minimum size |
| `.textClipped` | Text is not truncated or clipped |
| `.trait` | Traits match the element's actual behavior |
| `.all` | All of the above (default when no argument is passed) |

---

### 3. Filter Out Known Issues

If a specific element has a known, accepted issue you want to suppress without disabling the whole audit, use the handler closure. Return `true` to ignore a specific issue:

```swift
try app.performAccessibilityAudit(for: .all) { issue in
    // Return true to IGNORE this issue
    guard let element = issue.element,
          element.label == "Known Issue" else { return false }
    return issue.auditType == .dynamicType
}
```

This lets you suppress one false positive while keeping the full audit enforced everywhere else.

---

### 4. Regression Pattern — Audit in tearDown

The most effective integration pattern is to add the audit to `tearDownWithError()`. Every existing UI test then also validates accessibility with zero additional test-writing cost:

```swift
override func tearDownWithError() throws {
    try app.performAccessibilityAudit()
}
```

Any new screen your UI tests navigate to is automatically audited. This catches regressions before they reach code review.

---

## CI Pipeline Integration

To run accessibility audits on every pull request, add this to your GitHub Actions workflow:

```yaml
name: Accessibility Audit
on: [pull_request]
jobs:
  a11y-audit:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_16.app
      - name: Test
        run: |
          xcodebuild test \
            -project MyApp.xcodeproj \
            -scheme MyAppUITests \
            -sdk iphonesimulator \
            -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.0' \
            -resultBundlePath TestResults.xcresult | xcpretty
```

---

## What Automated Audits Catch vs. Miss

`performAccessibilityAudit` is effective for:
- Missing or empty accessibility labels
- Insufficient color contrast
- Fonts not scaling with Dynamic Type
- Touch targets smaller than 44×44pt
- Clipped/truncated text

**Important:** Automated audits catch approximately 30% of real-world accessibility issues. They do not catch problems like incorrect reading order, missing custom actions on list cells, focus not being trapped in modals, or missing state announcements for dynamic content. Complement automated audits with a manual VoiceOver testing protocol for full coverage.

---

## Common Issues That Will Fail the Audit

These are the most frequently found failures when first enabling the audit (ranked by frequency):

1. Image filenames used as labels (e.g., `"icon_heart_outline_24.png"`)
2. Missing labels on icon-only buttons
3. Insufficient contrast (light gray text on white backgrounds)
4. Hardcoded font sizes (`.font(.system(size: N))`) that don't respond to Dynamic Type
5. Touch targets under 44×44pt
6. Redundant type in labels (e.g., `"Search button"` — VoiceOver already appends "button" from the trait)

---

## Quick Summary

| Goal | Approach |
|---|---|
| Audit everything on every test run | Add `try app.performAccessibilityAudit()` to `tearDownWithError()` |
| Focus on specific checks | Pass `for: [.contrast, .dynamicType, ...]` |
| Suppress a known false positive | Use the handler closure, return `true` for that issue |
| Block merges on failure | Run the UI test scheme in CI via `xcodebuild test` |
