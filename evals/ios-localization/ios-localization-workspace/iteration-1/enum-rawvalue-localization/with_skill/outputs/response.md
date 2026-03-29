# Enum rawValue Not Localizing in Tab Bar

The problem is that `tab.rawValue` is a `String` variable, not a string literal. When you pass a `String` variable to `Text()`, SwiftUI uses the `StringProtocol` overload, which displays the string verbatim — **no localization lookup occurs**.

## The Problem

```swift
enum Tab: String {
    case home, search, profile
}

// ❌ rawValue is a String variable — Text displays it literally
Text(tab.rawValue)  // Displays "home", "search", "profile" — never localized
```

SwiftUI only auto-localizes **string literals** passed directly to `Text()`. When you pass a variable of type `String`, Swift resolves to `Text.init(_ content: some StringProtocol)` instead of `Text.init(_ key: LocalizedStringKey)`. The rawValue `"home"` is treated as display text, not as a localization key.

## The Fix: Add a displayName Computed Property

Create a computed property that returns `LocalizedStringKey` values, which will be looked up in your String Catalog:

```swift
enum Tab: String {
    case home, search, profile

    var displayName: LocalizedStringKey {
        switch self {
        case .home: "tab.home"
        case .search: "tab.search"
        case .profile: "tab.profile"
        }
    }
}

// ✅ LocalizedStringKey — localization lookup occurs
Text(tab.displayName)
```

Then add these keys to your String Catalog with appropriate translations:

| Key | English | Russian | Arabic |
|-----|---------|---------|--------|
| `tab.home` | Home | Главная | الرئيسية |
| `tab.search` | Search | Поиск | بحث |
| `tab.profile` | Profile | Профиль | الملف الشخصي |

## Why This Happens

This is a specific instance of the broader SwiftUI localization trap: only **string literals** trigger `LocalizedStringKey` resolution. Any time you pass a `String` variable to `Text()`, localization is bypassed. The `rawValue` property of a `String`-backed enum is a `String` variable, so it falls into this trap.

## Alternative: Use LocalizedStringResource (iOS 16+)

For more complex cases, `LocalizedStringResource` bundles the key, default value, and comment:

```swift
var displayResource: LocalizedStringResource {
    switch self {
    case .home: LocalizedStringResource("tab.home", defaultValue: "Home",
        comment: "Tab bar label for home screen")
    case .search: LocalizedStringResource("tab.search", defaultValue: "Search",
        comment: "Tab bar label for search screen")
    case .profile: LocalizedStringResource("tab.profile", defaultValue: "Profile",
        comment: "Tab bar label for user profile screen")
    }
}

Text(tab.displayResource)
```
