# Automated Localization Testing for Russian

To write automated tests that verify localization works correctly for Russian, you need to force the locale via launch arguments, use stable identifiers for element lookup, and test with numbers that exercise all four Russian plural categories.

## Forcing Russian Locale in Tests

Use launch arguments to set the locale and language before launching the app:

```swift
func testRussianLocalization() {
    let app = XCUIApplication()
    app.launchArguments += ["-AppleLocale", "ru_RU"]
    app.launchArguments += ["-AppleLanguages", "(ru)"]
    app.launch()

    // Now the app runs in Russian locale
}
```

These arguments override the simulator's language settings for this test run only, without affecting other tests.

## Element Lookup: Use accessibilityIdentifier, Not accessibilityLabel

This is critical for locale-specific testing. **Never use `accessibilityLabel` for element lookup** — it changes with each language. Use `accessibilityIdentifier` instead, which stays constant across all locales:

```swift
// ✅ Stable across all locales — identifier is never localized
let button = app.buttons["closeButton"]
let titleLabel = app.staticTexts["screenTitle"]

// ❌ Breaks in Russian — label is localized to Russian text
let button = app.buttons["Close"]  // Fails: Russian label is "Закрыть"
```

Make sure your views set `accessibilityIdentifier` on key elements:
```swift
closeButton.accessibilityIdentifier = "closeButton"
```

## Testing Plural Forms

Russian has 4 plural categories (`one`, `few`, `many`, `other`), and you must test with numbers that exercise each one. Use the verification test set:

```swift
func testRussianPluralForms() {
    let app = XCUIApplication()
    app.launchArguments += ["-AppleLocale", "ru_RU"]
    app.launchArguments += ["-AppleLanguages", "(ru)"]
    app.launch()

    // Test numbers that exercise all Russian plural categories:
    // one:   1, 21, 31, 101  (ends in 1, not 11)
    // few:   2, 3, 4, 22, 23 (ends in 2-4, not 12-14)
    // many:  0, 5, 10, 11, 12, 14, 20, 25, 100 (ends in 0, 5-9, or 11-14)
    // other: 1.5, 2.7         (fractions)

    // Example: set item count to 1 and verify Russian "one" form
    setItemCount(1)
    let label = app.staticTexts["itemCountLabel"]
    XCTAssertTrue(label.label.contains("файл"))   // "1 файл" (one)

    // Set to 2 and verify "few" form
    setItemCount(2)
    XCTAssertTrue(label.label.contains("файла"))   // "2 файла" (few)

    // Set to 5 and verify "many" form
    setItemCount(5)
    XCTAssertTrue(label.label.contains("файлов"))  // "5 файлов" (many)

    // Set to 21 — this is the critical test: Russian maps 21 to "one"
    setItemCount(21)
    XCTAssertTrue(label.label.contains("файл"))    // "21 файл" (one)
}
```

The full recommended verification set covers all boundary conditions:
```
[0, 1, 2, 3, 4, 5, 10, 11, 12, 14, 20, 21, 22, 25, 100, 101, 111, 1.5]
```

## Snapshot Testing with Locale

For visual regression testing across locales:

```swift
func testSettingsScreen_Russian() {
    let app = XCUIApplication()
    app.launchArguments += ["-AppleLocale", "ru_RU"]
    app.launchArguments += ["-AppleLanguages", "(ru)"]
    app.launch()

    // Navigate to settings
    app.buttons["settingsTab"].tap()

    let screenshot = app.screenshot()
    // Compare with reference snapshot for Russian locale
}
```

## CI Integration

Run locale-specific tests in CI alongside pseudolanguage tests:

```yaml
- name: Test Russian Localization
  run: |
    xcodebuild test \
      -scheme MyApp \
      -destination 'platform=iOS Simulator,name=iPhone 16' \
      -resultBundlePath RussianTestResults.xcresult
```
