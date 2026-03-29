# XCTest Accessibility Audit

## Overview

`performAccessibilityAudit()` is available from Xcode 15 / iOS 17. It runs automated accessibility checks directly within your UI test suite, catching issues at build time — before they reach users.

## Full Audit

Runs all available audit checks:

```swift
import XCTest

final class HomeViewAccessibilityTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    func testAccessibility() throws {
        // Navigate to the view under test
        app.buttons["Open Home"].tap()

        // Run all accessibility checks
        try app.performAccessibilityAudit()
    }
}
```

Any detected issue causes the test to fail with a description of the element and violation type.

## Selective Audit — Specific Categories

Run only the checks you care about, reducing noise from known outstanding issues:

```swift
func testContrastAndDynamicType() throws {
    app.launch()

    try app.performAccessibilityAudit(for: [
        .contrast,
        .dynamicType
    ])
}

func testElementDescriptions() throws {
    app.launch()
    app.buttons["Settings"].tap()

    try app.performAccessibilityAudit(for: [
        .sufficientElementDescription,
        .trait,
        .hitRegion
    ])
}
```

## Available Audit Types

| Audit Type | What It Checks |
|---|---|
| `.contrast` | Text/background contrast ratio meets WCAG 1.4.3 (4.5:1 normal, 3:1 large) |
| `.dynamicType` | Fonts respond to Dynamic Type — detects hardcoded `.system(size:)` |
| `.sufficientElementDescription` | Elements have meaningful `accessibilityLabel` — catches image filenames as labels |
| `.hitRegion` | Touch targets meet minimum size (24×24pt WCAG / 44×44pt Apple HIG) |
| `.textClipped` | Text is not truncated or clipped at any text size |
| `.trait` | Traits match element behavior (e.g., interactive element has `.isButton`) |
| `.all` | All of the above — use for comprehensive audit |

## Filtering Known Issues

When some issues are known and tracked (but not yet fixed), filter them to avoid blocking CI:

```swift
func testAccessibilityWithKnownIssues() throws {
    app.launch()

    try app.performAccessibilityAudit(for: .all) { issue in
        // Return true to IGNORE (suppress) this issue
        var shouldIgnore = false

        // Suppress known contrast issue on the legacy banner
        if let element = issue.element,
           element.label == "Legacy Banner",
           issue.auditType == .contrast {
            shouldIgnore = true
        }

        // Suppress known Dynamic Type issue on the chart view (tracked in ticket #1234)
        if let element = issue.element,
           element.identifier == "monthly-chart",
           issue.auditType == .dynamicType {
            shouldIgnore = true
        }

        return shouldIgnore
    }
}
```

The filter closure receives each `XCUIAccessibilityAuditIssue`. Returning `true` suppresses the issue; `false` keeps it as a failure.

## Practical Patterns

### Per-Screen Tests

Write one audit test per screen:

```swift
func testHomeScreenAccessibility() throws {
    app.launch()
    try app.performAccessibilityAudit()
}

func testProfileScreenAccessibility() throws {
    app.launch()
    app.buttons["Profile"].tap()
    try app.performAccessibilityAudit()
}

func testSettingsScreenAccessibility() throws {
    app.launch()
    app.buttons["Settings"].tap()
    try app.performAccessibilityAudit()
}
```

### Targeted Category Tests

```swift
// Fast contract test — contrast and labels only
func testCriticalAccessibilityProperties() throws {
    app.launch()
    try app.performAccessibilityAudit(for: [.contrast, .sufficientElementDescription])
}
```

## Limitations

`performAccessibilityAudit` catches approximately 30% of real accessibility issues — it cannot detect:
- Wrong labels (semantically incorrect but present)
- Missing VoiceOver navigation order issues
- Custom control behavior that doesn't respond correctly
- Focus trapping problems in modals

Always supplement with manual VoiceOver testing for a complete picture.
