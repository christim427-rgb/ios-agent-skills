# Handling Locale Changes at Runtime

## The Problem

When a user changes their language or region in the Settings app while your app is backgrounded, your app may continue displaying dates, numbers, and currencies in the old format. This happens because:

1. Cached `DateFormatter` and `NumberFormatter` instances retain their original locale settings
2. Labels that were formatted before the change still show stale text
3. The app doesn't re-render its UI with the new locale

## The Fix: Observe Locale Change Notifications

### NSLocale.currentLocaleDidChangeNotification

iOS posts `NSLocale.currentLocaleDidChangeNotification` when the user changes their locale (language, region, calendar, etc.) in Settings. Your app receives this when it returns to the foreground.

### UIKit Implementation

```swift
class ViewController: UIViewController {
    private var localeObserver: NSObjectProtocol?

    override func viewDidLoad() {
        super.viewDidLoad()

        localeObserver = NotificationCenter.default.addObserver(
            forName: NSLocale.currentLocaleDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.invalidateFormatters()
            self?.refreshUI()
        }

        refreshUI()
    }

    private var cachedDateFormatter: DateFormatter?
    private var cachedNumberFormatter: NumberFormatter?

    private func invalidateFormatters() {
        // Clear cached formatters so they're recreated with the new locale
        cachedDateFormatter = nil
        cachedNumberFormatter = nil
    }

    private func refreshUI() {
        // Re-format and re-display all locale-sensitive content
        dateLabel.text = formattedDate(someDate)
        priceLabel.text = formattedPrice(someAmount)
    }

    deinit {
        if let observer = localeObserver {
            NotificationCenter.default.removeObserver(observer)
        }
    }
}
```

### SwiftUI Implementation

In SwiftUI, the `@Environment(\.locale)` property automatically triggers a view update when the locale changes:

```swift
struct ContentView: View {
    @Environment(\.locale) var locale

    var body: some View {
        Text(date, format: .dateTime.month().day().year())
        // This automatically updates when the locale changes
    }
}
```

However, if you have cached formatters in an ObservableObject or singleton, you still need to observe the notification:

```swift
class FormatterCache: ObservableObject {
    @Published var dateFormatter: DateFormatter

    private var localeObserver: NSObjectProtocol?

    init() {
        dateFormatter = Self.makeDateFormatter()

        localeObserver = NotificationCenter.default.addObserver(
            forName: NSLocale.currentLocaleDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.dateFormatter = Self.makeDateFormatter()
        }
    }

    private static func makeDateFormatter() -> DateFormatter {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter
    }
}
```

## The Scenario

This issue occurs when:
1. User opens your app (formatters are created with current locale)
2. User backgrounds your app
3. User goes to Settings and changes their language/region
4. User returns to your app
5. iOS posts `NSLocale.currentLocaleDidChangeNotification`
6. Your app needs to invalidate cached formatters and refresh the UI

Without handling this notification, the user sees content formatted in their old locale until they force-quit and relaunch the app.

## Key Points

- Always observe `NSLocale.currentLocaleDidChangeNotification` if you cache formatters
- Invalidate all cached `DateFormatter`, `NumberFormatter`, and similar objects
- Refresh all visible locale-sensitive UI
- In SwiftUI, `@Environment(\.locale)` handles most cases automatically, but custom caches still need manual invalidation
