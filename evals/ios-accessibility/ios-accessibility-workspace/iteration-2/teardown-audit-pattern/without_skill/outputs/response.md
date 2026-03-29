# Add Accessibility Auditing to Every UI Test Without Per-Method Code

## Pattern: Base Test Class with tearDown Override

Create a base `XCTestCase` subclass that runs the audit automatically after every test method. All UI test classes inherit from this base.

```swift
import XCTest

class AccessibleUITestCase: XCTestCase {

    var app: XCUIApplication!

    override func setUpWithError() throws {
        try super.setUpWithError()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    override func tearDownWithError() throws {
        defer { app = nil }

        if #available(iOS 17, *) {
            // Run accessibility audit after every test automatically
            try app.performAccessibilityAudit()
        }

        try super.tearDownWithError()
    }
}
```

### Usage — Subclass and Write Normal Tests

```swift
final class HomeScreenTests: AccessibleUITestCase {

    func testNavigateToSettings() {
        app.buttons["Settings"].tap()
        XCTAssertTrue(app.navigationBars["Settings"].exists)
        // Accessibility audit runs automatically in tearDown
    }

    func testAddItem() {
        app.buttons["Add"].tap()
        XCTAssertTrue(app.sheets.firstMatch.exists)
        // Accessibility audit runs automatically in tearDown
    }
}
```

No accessibility code in any individual test method — the base class handles it.

## Pattern Variant: Selective Opt-Out

Sometimes a screen has known issues or is mid-refactor. Add an opt-out mechanism:

```swift
class AccessibleUITestCase: XCTestCase {

    var app: XCUIApplication!
    var skipAccessibilityAudit = false
    var auditIssueFilter: ((XCUIAccessibilityAuditIssue) -> Bool)?

    override func setUpWithError() throws {
        try super.setUpWithError()
        skipAccessibilityAudit = false
        auditIssueFilter = nil
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    override func tearDownWithError() throws {
        defer { app = nil }

        if #available(iOS 17, *), !skipAccessibilityAudit {
            if let filter = auditIssueFilter {
                try app.performAccessibilityAudit(issueHandler: filter)
            } else {
                try app.performAccessibilityAudit()
            }
        }

        try super.tearDownWithError()
    }
}

// Usage with known issue suppression:
final class LegacyScreenTests: AccessibleUITestCase {

    func testLegacyForm() {
        // Suppress a known contrast issue on a specific element
        auditIssueFilter = { issue in
            issue.auditType == .contrast && issue.element?.identifier == "legacyHeader"
        }
        app.buttons["Legacy Form"].tap()
        // ... test logic
    }

    func testSkippedScreen() {
        skipAccessibilityAudit = true
        // ... test logic for a screen not yet audited
    }
}
```

## Pattern Variant: Test Plan Integration

In Xcode Test Plans, you can enable accessibility auditing for all tests globally without any code:
1. Open the Test Plan (.xctestplan file).
2. Under Configurations > Options, enable "Run Accessibility Audits."

This runs `performAccessibilityAudit()` after every test method automatically at the test plan level, without requiring code changes.

## Recommendation

Use the Test Plan option for the broadest coverage with zero code overhead. Use the base class pattern when you need programmatic control over which audit types to run or which issues to suppress.
