# Custom SwiftUI View with String Parameter Skipping Localization

The problem is that your `CardView` accepts a `String` parameter. When the caller writes `CardView(title: "welcome_title")`, the literal `"welcome_title"` is inferred as a `String`, not a `LocalizedStringKey`. Inside the view, `Text(title)` receives a `String` variable, which uses the `StringProtocol` overload — **no localization lookup occurs**. The raw key text "welcome_title" is displayed literally.

## The Problem

```swift
// ❌ String parameter prevents LocalizedStringKey auto-localization
struct CardView: View {
    let title: String
    var body: some View { Text(title) }
}

CardView(title: "welcome_title")  // Shows "welcome_title" literally
```

SwiftUI only performs localization lookup when a **string literal** is passed directly to a view that accepts `LocalizedStringKey`. Once the literal is captured as a `String` type, the localization path is lost.

## The Fix: Accept LocalizedStringKey

Change the parameter type to `LocalizedStringKey`:

```swift
// ✅ LocalizedStringKey — auto-localization works
struct CardView: View {
    let title: LocalizedStringKey
    var body: some View { Text(title) }
}

CardView(title: "welcome_title")  // Looks up "welcome_title" in String Catalog
```

Now when the caller passes `"welcome_title"`, Swift infers it as `LocalizedStringKey` (because that is the expected type), and `Text(title)` performs the localization lookup.

## Alternative: Generic Approach (Like Apple's Views)

Apple's own views (like `Button`, `Label`, `Toggle`) use a generic approach that accepts any `StringProtocol`:

```swift
struct CardView<Title: StringProtocol>: View {
    let title: Title
    init(_ title: Title) { self.title = title }
    var body: some View { Text(title) }
}
```

However, this approach also does **not** auto-localize, because `StringProtocol` is not `LocalizedStringKey`. Apple's views have additional initializers that accept `LocalizedStringKey` specifically. For custom views where localization is desired, the `LocalizedStringKey` approach is simpler and more direct.

## When to Use Which Type

- **`LocalizedStringKey`** — for user-facing text that should be localized (titles, labels, buttons)
- **`String`** — for programmatic/dynamic text that is already resolved (e.g., user names, computed values)
- **`Text(verbatim:)`** — for non-localizable content (version numbers, URLs, identifiers)

If your custom view's title will always be a localized UI label, `LocalizedStringKey` is the right choice. If it sometimes needs to display dynamic non-localized content, consider providing two initializers — one for `LocalizedStringKey` and one for `String` with `verbatim`.
