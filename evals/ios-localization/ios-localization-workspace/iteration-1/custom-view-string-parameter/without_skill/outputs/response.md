# Custom SwiftUI View: String Parameter Prevents Localization

## The Problem

```swift
struct CardView: View {
    let title: String
    var body: some View { Text(title) }
}

CardView(title: "welcome_title")  // Shows "welcome_title" literally
```

Even though `"welcome_title"` is a string literal at the call site, by the time it reaches `Text(title)` inside `CardView`, it's a `String` variable. SwiftUI's `Text` only auto-localizes when given a **literal** `LocalizedStringKey` directly. Since `title` is declared as `String`, `Text(title)` uses the `StringProtocol` initializer, which displays the string verbatim without localization.

## The Fix

Change the parameter type from `String` to `LocalizedStringKey`:

```swift
struct CardView: View {
    let title: LocalizedStringKey

    var body: some View {
        Text(title)  // Now performs localization lookup
    }
}

// Usage -- the literal is now interpreted as a LocalizedStringKey
CardView(title: "welcome_title")  // Looks up "welcome_title" in String Catalog
```

## How This Works

When the parameter type is `LocalizedStringKey`, Swift uses `ExpressibleByStringLiteral` to convert the literal `"welcome_title"` into a `LocalizedStringKey` at the call site. Then `Text(title)` uses the `LocalizedStringKey` initializer, which performs the localization lookup.

## Following Apple's Pattern

This is exactly how Apple's own SwiftUI views work. For example, `Button` accepts a `LocalizedStringKey` for its title:

```swift
// Apple's Button initializer
public init(_ titleKey: LocalizedStringKey, action: @escaping () -> Void)
```

You should follow the same pattern for any custom view that displays user-facing text.

## If You Need Both Localized and Non-Localized

If your view sometimes needs a localized key and sometimes a raw string, you can provide two initializers:

```swift
struct CardView: View {
    let title: LocalizedStringKey

    var body: some View { Text(title) }
}

extension CardView {
    init(verbatim title: String) {
        self.title = LocalizedStringKey(title)
    }
}
```

Or accept `LocalizedStringKey` as the default and let callers use `Text(verbatim:)` patterns when needed.
