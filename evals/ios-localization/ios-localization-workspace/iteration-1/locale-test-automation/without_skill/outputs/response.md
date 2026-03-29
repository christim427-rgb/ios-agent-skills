# Automated Testing for Russian Localization

## Setting Up Locale in UI Tests

You can force the app to launch in Russian by setting launch arguments in your XCUITest:

```swift
class RussianLocalizationTests: XCTestCase {
    let app = XCUIApplication()

    override func setUpWithError() throws {
        continueAfterFailure = false
        app.launchArguments += ["-AppleLanguages", "(ru)"]
        app.launchArguments += ["-AppleLocale", "ru_RU"]
        app.launch()
    }
}
```

The `-AppleLanguages (ru)` argument forces the app's language to Russian, and `-AppleLocale ru_RU` sets the locale for number/date formatting.

## Finding Elements: Use accessibilityIdentifier

When testing localized apps, **do not** use `accessibilityLabel` to find elements, because labels change per language. Instead, use `accessibilityIdentifier`, which is a stable, non-localized identifier:

```swift
// In your app code
saveButton.accessibilityIdentifier = "save_button"

// In your test
func testSaveButtonExists() {
    let saveButton = app.buttons["save_button"]  // Uses identifier
    XCTAssertTrue(saveButton.exists)
}
```

## Verifying Translated Text

To verify that a specific translation appears:

```swift
func testWelcomeScreenShowsRussianText() {
    let welcomeLabel = app.staticTexts["welcome_label"]  // by identifier
    XCTAssertTrue(welcomeLabel.exists)
    // Verify it shows the Russian translation
    XCTAssertEqual(welcomeLabel.label, "Добро пожаловать")
}
```

## Testing Russian Plural Forms

Russian has 4 plural categories (one, few, many, other). Test with numbers that exercise each category:

```swift
func testRussianPluralForms() {
    // Test key numbers for Russian plural categories:
    // one: 1, 21, 31, 101
    // few: 2, 3, 4, 22, 23, 24
    // many: 0, 5, 6, 10, 11, 12, 13, 14, 20, 25
    // other: 1.5 (fractional)

    let testCases: [(count: Int, expected: String)] = [
        (1, "1 файл"),       // one
        (2, "2 файла"),      // few
        (5, "5 файлов"),     // many
        (11, "11 файлов"),   // many (teens are special)
        (21, "21 файл"),     // one
        (22, "22 файла"),    // few
    ]

    for testCase in testCases {
        // Navigate to set the count, then verify the label
        setItemCount(testCase.count)
        let label = app.staticTexts["item_count_label"]
        XCTAssertEqual(label.label, testCase.expected,
            "Plural form wrong for count \(testCase.count)")
    }
}
```

## Testing Date and Number Formatting

```swift
func testRussianDateFormatting() {
    let dateLabel = app.staticTexts["date_label"]
    XCTAssertTrue(dateLabel.exists)
    // Russian dates use dd.MM.yyyy format
    // Verify it doesn't show MM/dd/yyyy (US format)
    XCTAssertFalse(dateLabel.label.contains("/"),
        "Date should not use US slash format for Russian locale")
}

func testRussianNumberFormatting() {
    let priceLabel = app.staticTexts["price_label"]
    XCTAssertTrue(priceLabel.exists)
    // Russian uses space as thousands separator and comma for decimal
    // e.g., 1 234,56
}
```

## Running Tests for Multiple Locales

You can parameterize tests to run across multiple locales:

```swift
class MultiLocaleTests: XCTestCase {
    func testWithLocale(_ locale: String, language: String) {
        let app = XCUIApplication()
        app.launchArguments += ["-AppleLanguages", "(\(language))"]
        app.launchArguments += ["-AppleLocale", locale]
        app.launch()

        // Your assertions here
    }
}
```
