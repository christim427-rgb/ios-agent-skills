# Enum rawValue Not Localizing in Tab Bar

## The Problem

```swift
enum Tab: String {
    case home, search, profile
}

Text(tab.rawValue)
```

The issue is that `tab.rawValue` is a **String variable** (with values like `"home"`, `"search"`, `"profile"`). When you pass a `String` variable to `Text()`, SwiftUI uses the `StringProtocol` initializer, which displays the string literally -- it does **not** treat it as a `LocalizedStringKey`.

Only string **literals** (directly typed in code) trigger SwiftUI's automatic localization lookup. A `rawValue` is a computed property that returns a `String`, not a literal.

## The Fix

Add a computed property that returns a `LocalizedStringKey` for display:

```swift
enum Tab: String {
    case home, search, profile

    var displayName: LocalizedStringKey {
        switch self {
        case .home: return "tab.home"
        case .search: return "tab.search"
        case .profile: return "tab.profile"
        }
    }
}

// Usage
Text(tab.displayName) // Now looks up localization keys
```

Then in your String Catalog or `.strings` file, provide translations for `"tab.home"`, `"tab.search"`, and `"tab.profile"`.

## Alternative: Use LocalizedStringKey Directly

```swift
enum Tab: String {
    case home, search, profile

    var localizedTitle: String {
        switch self {
        case .home:
            return String(localized: "tab.home", comment: "Tab bar item: Home screen")
        case .search:
            return String(localized: "tab.search", comment: "Tab bar item: Search screen")
        case .profile:
            return String(localized: "tab.profile", comment: "Tab bar item: User profile screen")
        }
    }
}

// Usage
Text(tab.localizedTitle)
```

## Why rawValue Doesn't Work

The key insight is that SwiftUI `Text` has two initializers:
- `Text(_ key: LocalizedStringKey)` -- triggered by string literals, performs localization
- `Text(_ content: some StringProtocol)` -- triggered by String variables, displays verbatim

Since `rawValue` returns a `String`, Swift selects the second initializer, and no localization occurs.
