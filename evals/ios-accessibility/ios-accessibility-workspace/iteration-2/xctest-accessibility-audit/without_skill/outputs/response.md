# Running Automated Accessibility Audit in XCTest UI Tests

## iOS 17+ — performAccessibilityAudit (Recommended)

Xcode 15 and iOS 17 introduced `XCUIApplication.performAccessibilityAudit()`, which runs a set of automated accessibility checks and reports issues as test failures.

```swift
import XCTest

final class AccessibilityAuditTests: XCTestCase {

    func testHomeScreenAccessibility() throws {
        let app = XCUIApplication()
        app.launch()

        // Run the full default audit
        try app.performAccessibilityAudit()
    }
}
```

### Filtering Audit Types

You can limit the audit to specific categories:

```swift
try app.performAccessibilityAudit(for: [
    .contrast,
    .hitRegion,
    .sufficientElementDescription
])
```

Available audit types (as of iOS 17):
- `.contrast` — color contrast of text and controls
- `.elementDetection` — elements that should be accessible but are not
- `.hitRegion` — tap targets that are too small
- `.sufficientElementDescription` — missing or poor accessibility labels
- `.dynamicType` — text that doesn't scale with Dynamic Type
- `.textClipped` — text that is clipped at large sizes
- `.trait` — incorrect or missing accessibility traits
- `.parentChild` — improper accessibility container relationships

Use `.all` (or omit the parameter) to run all checks.

### Handling Known Issues / Ignoring Specific Failures

```swift
try app.performAccessibilityAudit { issue in
    // Return true to ignore this issue, false to fail the test
    if issue.auditType == .contrast && issue.element?.identifier == "decorativeBanner" {
        return true // known issue, ignore
    }
    return false
}
```

## iOS 16 and Earlier — Accessibility Inspector

For older OS targets, automated in-test auditing is not available via XCTest. Options:

1. **Accessibility Inspector** (Xcode tool, not in-test): Run > Accessibility Inspector > Audit to catch issues manually during development.
2. **XCUIElement checks**: Manually assert accessibility properties in tests:

```swift
func testButtonHasLabel() {
    let app = XCUIApplication()
    app.launch()
    let button = app.buttons["submitButton"]
    XCTAssertFalse(button.label.isEmpty, "Submit button must have an accessibility label")
}
```

## Complete Example

```swift
final class FullAccessibilityTests: XCTestCase {

    var app: XCUIApplication!

    override func setUpWithError() throws {
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    func testMainScreenAudit() throws {
        if #available(iOS 17, *) {
            try app.performAccessibilityAudit()
        } else {
            throw XCTSkip("Accessibility audit API requires iOS 17+")
        }
    }
}
```

## What It Does Not Catch

Automated audits detect structural issues but cannot test:
- Whether labels are *meaningful* (they only check that labels exist)
- Correct reading order in complex custom layouts
- Context-appropriate announcements
- User flow logic (e.g., whether modal dismissal is announced)

Complement automated audits with manual VoiceOver testing.
