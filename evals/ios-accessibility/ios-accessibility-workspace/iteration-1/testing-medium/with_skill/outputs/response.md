# Adding Accessibility Auditing to Every UI Test Without Repeating Code

## The Pattern: Override `tearDownWithError()` in Your Base Test Class

The canonical pattern from `references/testing.md` is to call `performAccessibilityAudit()` inside `tearDownWithError()`. Because every XCTestCase subclass inherits this method, placing it in a shared base class means every UI test automatically runs a full accessibility audit when it finishes — at zero additional test-writing cost.

### Step 1 — Create a Base UI Test Class

```swift
import XCTest

class AccessibleUITestCase: XCTestCase {

    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launch()
    }

    override func tearDownWithError() throws {
        // Runs after every test method in any subclass
        try app.performAccessibilityAudit()
    }
}
```

### Step 2 — Subclass It in Every Test File

```swift
class LoginScreenTests: AccessibleUITestCase {

    func testLoginButtonIsEnabled() {
        // Your test logic here — no audit code needed
        let button = app.buttons["Log In"]
        XCTAssertTrue(button.exists)
    }

    func testEmptyFieldShowsError() {
        app.buttons["Log In"].tap()
        XCTAssertTrue(app.staticTexts["Email is required"].exists)
    }
}
```

Both tests will automatically trigger `performAccessibilityAudit()` when they finish. No audit call is written in either test method.

---

## Audit Scope Options

By default `performAccessibilityAudit()` runs `.all` checks. You can narrow scope in the base class if you want faster runs during development:

```swift
// In AccessibleUITestCase.tearDownWithError()

// Full audit (default, recommended for CI)
try app.performAccessibilityAudit()

// Targeted — only the highest-value checks
try app.performAccessibilityAudit(for: [
    .contrast,
    .dynamicType,
    .sufficientElementDescription
])
```

**Audit types available (`XCUIAccessibilityAuditType`):**

| Type | What it catches |
|---|---|
| `.contrast` | Text/background contrast below WCAG threshold |
| `.dynamicType` | Fonts not responding to Dynamic Type changes |
| `.sufficientElementDescription` | Elements with no label or filename-as-label |
| `.hitRegion` | Touch targets under 44×44 pt |
| `.textClipped` | Text truncated or clipped |
| `.trait` | Traits inconsistent with element behavior |
| `.all` | All of the above |

---

## Suppressing Known False Positives

If your codebase has a known issue that you are tracking separately (e.g., a third-party component with a contrast problem), suppress it in the base class without silencing everything else:

```swift
override func tearDownWithError() throws {
    try app.performAccessibilityAudit(for: .all) { issue in
        // Return true to IGNORE this specific issue
        guard let element = issue.element else { return false }
        let isKnownThirdPartyLabel = element.label == "AdBanner"
        return isKnownThirdPartyLabel && issue.auditType == .contrast
    }
}
```

---

## CI Integration

Add a UI test scheme that runs `AccessibleUITestCase` subclasses on every pull request. No audit-specific CI step is needed — the audits run as part of the normal test run.

```yaml
# .github/workflows/accessibility.yml
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

## Key Points

- `performAccessibilityAudit()` requires **Xcode 15+** (iOS 17 simulator or later).
- The `tearDownWithError()` hook runs even when a test fails, so accessibility regressions are always caught.
- Automated audits catch approximately **30% of accessibility issues**. Supplement with the 10-step manual VoiceOver protocol from `references/testing.md` for pre-release sign-off.
- `continueAfterFailure = false` in `setUpWithError()` ensures the test stops at first failure rather than producing misleading audit results against a broken UI state.

---

## What This Pattern Does NOT Cover

The audit checks structural properties (labels, contrast, touch target size, Dynamic Type compliance). It does not verify:

- Logical reading order for VoiceOver
- Focus trapping in modals
- Custom action availability on list cells
- Dynamic announcements (loading states, errors)

These require the manual VoiceOver protocol or third-party tools like `A11yUITests` (Rob Whitaker) or `AccessibilitySnapshot` (Cash App).
