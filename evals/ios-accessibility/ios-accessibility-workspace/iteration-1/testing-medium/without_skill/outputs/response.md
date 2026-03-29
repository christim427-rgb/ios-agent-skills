# Adding Accessibility Auditing to Every UI Test Without Repeating Code

The standard pattern in XCTest is to override `setUp()` in a base test class and enable the built-in accessibility auditing feature there. Every test subclass then inherits the behavior automatically.

---

## The Core Pattern: Base Test Class + `setUp()` Override

### Step 1 — Create a Base UI Test Class

```swift
import XCTest

class AccessibleUITestCase: XCTestCase {

    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()

        // Enable automatic accessibility auditing for every test method
        if #available(iOS 17.0, *) {
            try? performAccessibilityAudit()
        }
    }
}
```

### Step 2 — Subclass It in All Your Test Files

```swift
class LoginScreenTests: AccessibleUITestCase {

    func testLoginButtonIsVisible() {
        // No accessibility setup needed here.
        // The audit runs automatically via setUp() in the base class.
        XCTAssertTrue(app.buttons["Log In"].exists)
    }

    func testInvalidCredentialsShowsError() {
        app.textFields["Email"].tap()
        app.textFields["Email"].typeText("bad@email")
        app.buttons["Log In"].tap()
        XCTAssertTrue(app.staticTexts["Invalid credentials"].exists)
    }
}
```

---

## Using `performAccessibilityAudit()` (iOS 17+)

Apple introduced `XCTestCase.performAccessibilityAudit()` in Xcode 15 / iOS 17. It runs a set of audit types against the current view hierarchy and fails the test if violations are found.

### Full Signature

```swift
// Available on iOS 17+, macOS 14+
func performAccessibilityAudit(
    for auditTypes: XCUIAccessibilityAuditType = .all,
    issueHandler: ((XCUIAccessibilityAuditIssue) -> Bool)? = nil
) throws
```

### Audit Types You Can Specify

| Type | What It Checks |
|---|---|
| `.contrast` | Text/background color contrast ratios |
| `.hitRegion` | Touch target sizes (minimum 44×44 pt) |
| `.sufficientElementDescription` | Meaningful accessibility labels |
| `.dynamicType` | Text scales with Dynamic Type |
| `.textClipped` | Text is not truncated or clipped |
| `.all` | All of the above (default) |

### Configuring Which Audits Run

```swift
// Run only contrast and hit-region checks
if #available(iOS 17.0, *) {
    try performAccessibilityAudit(for: [.contrast, .hitRegion])
}
```

---

## Handling Known / Expected Violations

Some violations may be acceptable (e.g., a decorative image intentionally has no label). Use the `issueHandler` closure to suppress known issues:

```swift
override func setUp() {
    super.setUp()
    // ...
    if #available(iOS 17.0, *) {
        try? performAccessibilityAudit { issue in
            // Return true to suppress (ignore) this issue
            if issue.auditType == .sufficientElementDescription,
               issue.element?.elementType == .image {
                return true // Decorative images are OK without labels
            }
            return false // Fail on everything else
        }
    }
}
```

---

## Calling the Audit at the Right Time

`setUp()` runs before each test method, but the view hierarchy may not have fully loaded yet. If your tests navigate to a specific screen before auditing, call `performAccessibilityAudit()` at the end of each test helper or after navigation, rather than in `setUp()`.

**Pattern: audit after navigation**

```swift
class AccessibleUITestCase: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }

    // Call this after navigating to any screen
    func auditCurrentScreen(
        for types: XCUIAccessibilityAuditType = .all,
        suppressingIssues handler: ((XCUIAccessibilityAuditIssue) -> Bool)? = nil
    ) {
        if #available(iOS 17.0, *) {
            XCTAssertNoThrow(
                try performAccessibilityAudit(for: types, issueHandler: handler)
            )
        }
    }
}

// Usage in a subclass
class HomeScreenTests: AccessibleUITestCase {
    func testHomeScreenAccessibility() {
        // Navigate to home is done by launch
        auditCurrentScreen()
    }

    func testProfileNavigationAccessibility() {
        app.buttons["Profile"].tap()
        auditCurrentScreen()
    }
}
```

---

## Pre-iOS 17 Fallback: Manual Checks

If you need to support iOS 16 and earlier, use a manual helper in the base class:

```swift
func assertAllElementsHaveLabels(in element: XCUIElement? = nil) {
    let root = element ?? app
    let interactiveTypes: [XCUIElement.ElementType] = [.button, .textField, .switch, .slider]
    for type in interactiveTypes {
        let elements = root.descendants(matching: type).allElementsBoundByIndex
        for el in elements {
            XCTAssertFalse(
                el.label.isEmpty,
                "\(type) element at \(el.frame) has no accessibility label"
            )
        }
    }
}
```

---

## Summary

| Approach | iOS Version | Effort | Coverage |
|---|---|---|---|
| `performAccessibilityAudit()` in `setUp()` of base class | iOS 17+ | Minimal | Broad (contrast, labels, hit regions, dynamic type) |
| `performAccessibilityAudit()` called after navigation | iOS 17+ | Low | Full per-screen |
| Manual label/trait checks in base class helper | iOS 13+ | Medium | Partial |

**Recommended approach:** Create `AccessibleUITestCase: XCTestCase`, override `setUp()` to call `performAccessibilityAudit()` (guarded with `#available(iOS 17.0, *)`), and have all UI test classes subclass it. This ensures every test gets an audit with zero per-test boilerplate.
