# Stale Date Formats After Language Change

The issue is that your app caches `DateFormatter` instances (or their results), and when the user changes their language in Settings while the app is backgrounded, the cached formatters still use the old locale. iOS does not restart your app when the user changes language — the app comes back from background with stale formatters.

## The Scenario

1. User runs your app in English (dates show as "Mar 29, 2025")
2. User goes to Settings and changes language to German
3. User returns to your app (from background, no restart)
4. Dates still show "Mar 29, 2025" instead of "29. Mär. 2025"

This happens because `DateFormatter` captures the locale at creation time. If the formatter is cached (which it should be for performance), it keeps the old locale.

## The Fix: Observe NSLocale.currentLocaleDidChangeNotification

Register for the locale change notification and invalidate your cached formatters when it fires:

```swift
NotificationCenter.default.addObserver(
    forName: NSLocale.currentLocaleDidChangeNotification,
    object: nil,
    queue: .main
) { [weak self] _ in
    self?.invalidateFormatters()
}
```

## Full Implementation Pattern

```swift
class FormatterCache {
    static let shared = FormatterCache()

    private var _dateFormatter: DateFormatter?
    private var _numberFormatter: NumberFormatter?
    private var _currencyFormatter: NumberFormatter?

    init() {
        NotificationCenter.default.addObserver(
            forName: NSLocale.currentLocaleDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.invalidateAll()
        }
    }

    var dateFormatter: DateFormatter {
        if let cached = _dateFormatter { return cached }
        let f = DateFormatter()
        f.dateStyle = .medium
        f.timeStyle = .short
        _dateFormatter = f
        return f
    }

    var numberFormatter: NumberFormatter {
        if let cached = _numberFormatter { return cached }
        let f = NumberFormatter()
        f.numberStyle = .decimal
        _numberFormatter = f
        return f
    }

    private func invalidateAll() {
        _dateFormatter = nil
        _numberFormatter = nil
        _currencyFormatter = nil
        // Post notification for views to refresh
        NotificationCenter.default.post(name: .formattersDidInvalidate, object: nil)
    }
}

extension Notification.Name {
    static let formattersDidInvalidate = Notification.Name("formattersDidInvalidate")
}
```

## Key Points

- **Invalidate all cached formatters:** `DateFormatter`, `NumberFormatter`, `MeasurementFormatter`, and any other locale-sensitive formatter.
- **Refresh the UI:** After invalidating formatters, your views need to re-render. Post a custom notification or use a Combine publisher that views observe to trigger a refresh.
- **This applies to backgrounded apps:** iOS sends `NSLocale.currentLocaleDidChangeNotification` when the app returns to foreground after a locale change. The app is NOT restarted — it resumes from background with stale state.
- **`Date.formatted()` (iOS 15+):** Uses the current locale at call time (not cached), so it is less susceptible to this issue. But if you cache the formatted string result, it will still go stale.
- **Do not recreate formatters on every use without caching:** `DateFormatter` creation is expensive. The correct pattern is to cache formatters and invalidate them on locale change — not to avoid caching entirely.
