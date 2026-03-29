# Running Automated Accessibility Audits in XCTest UI Tests

## Overview

iOS provides built-in support for accessibility auditing within XCTest UI tests using the `XCUIApplication` and `XCTestCase` APIs. Starting with Xcode 15 / iOS 17, Apple introduced `performAccessibilityAudit()` which makes automated accessibility checks straightforward.

---

## Method 1: Using `performAccessibilityAudit()` (Xcode 15+ / iOS 17+)

This is the modern, recommended approach. Apple's built-in audit checks for a range of accessibility issues automatically.

### Basic Usage

```swift
import XCTest

final class AccessibilityAuditTests: XCTestCase {

    func testAccessibilityAudit() throws {
        let app = XCUIApplication()
        app.launch()

        // Run a full accessibility audit on the current screen
        try app.performAccessibilityAudit()
    }
}
```

When this test runs, XCTest will inspect the UI hierarchy and automatically fail the test if it finds accessibility violations such as:
- Elements with no accessibility label
- Contrast ratio failures
- Elements with clipped or truncated labels
- Hit targets that are too small
- Dynamic type issues

### Auditing a Specific Screen or State

Navigate to the screen you want to audit before calling `performAccessibilityAudit()`:

```swift
func testLoginScreenAccessibility() throws {
    let app = XCUIApplication()
    app.launch()

    // Navigate to the login screen
    app.buttons["Sign In"].tap()

    // Audit that specific screen
    try app.performAccessibilityAudit()
}
```

### Filtering Audit Types

You can limit which audit categories are checked using `XCUIAccessibilityAuditType`:

```swift
func testContrastAndLabels() throws {
    let app = XCUIApplication()
    app.launch()

    try app.performAccessibilityAudit(for: [.contrast, .textClipped])
}
```

Available audit types include:
- `.contrast` — color contrast ratio
- `.textClipped` — clipped or truncated text
- `.elementDetection` — missing or invalid elements
- `.hitRegion` — tap target size
- `.sufficientElementDescription` — meaningful accessibility labels
- `.dynamicType` — dynamic type scaling support
- `.all` — all available checks (default)

### Handling Expected Failures

If certain violations are known and intentional, you can handle them without failing the test:

```swift
func testWithKnownIssues() throws {
    let app = XCUIApplication()
    app.launch()

    try app.performAccessibilityAudit { issue in
        // Return true to ignore this issue, false to fail the test
        if issue.auditType == .contrast,
           issue.element.identifier == "decorative-background" {
            return true // intentionally skip this one
        }
        return false
    }
}
```

---

## Method 2: Manual Element-Level Checks (All Xcode Versions)

For older Xcode versions or more granular control, you can manually query the element tree and assert properties:

```swift
func testAllButtonsHaveLabels() {
    let app = XCUIApplication()
    app.launch()

    let buttons = app.buttons.allElementsBoundByIndex
    for button in buttons {
        XCTAssertFalse(
            button.label.isEmpty,
            "Button at index has no accessibility label: \(button)"
        )
    }
}

func testTapTargetSize() {
    let app = XCUIApplication()
    app.launch()

    let buttons = app.buttons.allElementsBoundByIndex
    for button in buttons {
        let frame = button.frame
        XCTAssertGreaterThanOrEqual(frame.width, 44,
            "Button width below 44pt: \(button.label)")
        XCTAssertGreaterThanOrEqual(frame.height, 44,
            "Button height below 44pt: \(button.label)")
    }
}
```

---

## Method 3: Integrating with CI/CD

### Xcode Test Plans

Create a `.xctestplan` file and include your accessibility test targets. This allows you to run accessibility audits as part of your regular test suite on CI.

### Running from the Command Line

```bash
xcodebuild test \
  -project MyApp.xcodeproj \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -testPlan AccessibilityTests
```

Or without a test plan, specifying the test class directly:

```bash
xcodebuild test \
  -project MyApp.xcodeproj \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -only-testing:MyAppUITests/AccessibilityAuditTests
```

---

## Best Practices

1. **Audit every major screen** — Create a dedicated test for each key screen in your app, not just the home screen.

2. **Run audits in your CI pipeline** — Include accessibility tests in the same test suite as your functional UI tests so regressions are caught automatically.

3. **Use test plans to organize** — Separate accessibility tests into their own `xctestplan` so they can be run independently or as part of a full suite.

4. **Combine with VoiceOver testing** — `performAccessibilityAudit()` does not simulate VoiceOver navigation order. For that, manually test with VoiceOver enabled in the simulator.

5. **Address issues incrementally** — If you're adding audits to an existing app, use the issue handler closure to suppress known existing issues and fix them over time rather than ignoring audits entirely.

6. **Test dynamic type** — Launch the app with different content size categories to verify layout at large font sizes:

```swift
func testLargeTextAccessibility() throws {
    let app = XCUIApplication()
    app.launchArguments = ["-UIPreferredContentSizeCategoryName",
                           "UICTContentSizeCategoryAccessibilityXL"]
    app.launch()

    try app.performAccessibilityAudit(for: .dynamicType)
}
```

---

## Summary

| Approach | Xcode Version | Best For |
|---|---|---|
| `performAccessibilityAudit()` | Xcode 15+ (iOS 17+) | Comprehensive automated audits |
| Manual element assertions | All versions | Custom rules, older deployment targets |
| CLI + test plans | All versions | CI/CD integration |

The `performAccessibilityAudit()` API is the simplest and most powerful option if your minimum deployment target allows it. For apps targeting iOS 16 and earlier, combine manual assertions with the Accessibility Inspector tool in Xcode for a thorough audit strategy.
