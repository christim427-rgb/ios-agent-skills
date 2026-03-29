# Accessibility Audit in tearDown — Zero-Cost Regression Pattern

## The Pattern

Place `performAccessibilityAudit()` in `tearDownWithError()`. Every existing UI test automatically becomes an accessibility regression test — no per-method audit code needed, no new test functions required.

```swift
import XCTest

class BaseUITestCase: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    override func tearDownWithError() throws {
        // Runs after EVERY test method in this class
        try app.performAccessibilityAudit()
    }
}
```

Every test that navigates to a screen now also audits that screen's accessibility as a side effect.

## Why tearDown, Not the Test Method Itself

- **Zero additional code** — existing functional tests gain accessibility coverage
- **Catches regressions** — a UI change that breaks a label or contrast fails the next CI run automatically
- **Screen coverage scales with test coverage** — as you write more functional tests, more screens get audited

## Filtering Known Issues in tearDown

When the audit has pre-existing failures that are tracked but not yet fixed, filter them globally from the base class:

```swift
class BaseUITestCase: XCTestCase {
    let app = XCUIApplication()

    // Known accessibility issues — tracked in backlog, not yet fixed
    private let knownIssues: [(label: String, type: XCUIAccessibilityAuditType)] = [
        ("Legacy Banner", .contrast),          // Ticket #1204 — old UI component
        ("monthly-chart", .dynamicType),        // Ticket #1347 — chart axes not scaled
    ]

    override func tearDownWithError() throws {
        try app.performAccessibilityAudit(for: .all) { [self] issue in
            for known in knownIssues {
                if let element = issue.element,
                   (element.label == known.label || element.identifier == known.label),
                   issue.auditType == known.type {
                    return true  // Suppress this known issue
                }
            }
            return false  // Fail on unknown issues
        }
    }
}
```

## Subclassing for Per-Suite Customization

Subclass `BaseUITestCase` for test suites that need different audit configurations:

```swift
// Standard screens — full audit
class HomeTests: BaseUITestCase {
    func testHomeLoads() {
        // Test logic here
        // tearDown automatically audits Home screen accessibility
        XCTAssertTrue(app.staticTexts["Welcome"].exists)
    }
}

// Charts-heavy screen — skip Dynamic Type audit (known outstanding issue)
class DashboardTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
        app.buttons["Dashboard"].tap()
    }

    override func tearDownWithError() throws {
        // Skip .dynamicType for this suite — tracked separately
        try app.performAccessibilityAudit(for: [
            .contrast,
            .sufficientElementDescription,
            .hitRegion
        ])
    }

    func testDashboardMetrics() {
        // ... test logic
    }
}
```

## CI Integration

The tearDown pattern integrates naturally with GitHub Actions — no changes to the CI pipeline needed beyond running the UI test target:

```yaml
- name: Run UI Tests (includes accessibility audit)
  run: |
    xcodebuild test \
      -project MyApp.xcodeproj \
      -scheme MyAppUITests \
      -sdk iphonesimulator \
      -destination 'platform=iOS Simulator,name=iPhone 16,OS=18.0' \
      -resultBundlePath TestResults.xcresult
```

## Managing the Known Issues List

Known issues in the filter list should:
1. Reference a ticket number in a comment so they can be found and removed
2. Be reviewed in each sprint — if the ticket is closed, remove the suppression
3. Be as specific as possible — suppress by both element identifier AND audit type to avoid over-suppressing

```swift
// Good — specific suppression
("monthly-chart", .dynamicType)  // Ticket #1347

// Too broad — don't suppress by element alone without audit type
// This would hide all audit failures on that element
```
