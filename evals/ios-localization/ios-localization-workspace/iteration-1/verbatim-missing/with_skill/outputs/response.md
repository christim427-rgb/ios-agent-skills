Version strings and URLs are appearing in your String Catalog because `Text()` with a string literal automatically treats the literal as a `LocalizedStringKey` and extracts it for localization. Non-localizable content like version numbers and URLs should never be sent to translators.

## The Problem

```swift
Text("v2.0.1")                        // Extracted to String Catalog as a translation key
Text("https://example.com/terms")     // Also extracted
```

Both strings get added to the String Catalog as keys awaiting translation. Translators see them and either:
- Waste time translating things that should not be translated
- Create confusion about what these entries mean
- Accidentally modify them, breaking your version display or URL

## The Fix: Use `Text(verbatim:)`

```swift
Text(verbatim: "v2.0.1")                     // NOT extracted to String Catalog
Text(verbatim: "https://example.com/terms")   // NOT extracted to String Catalog
```

`Text(verbatim:)` tells SwiftUI to display the string exactly as-is without any localization lookup, and Xcode will not extract it into the String Catalog.

## What Should Use `verbatim:`

Use `Text(verbatim:)` for any content that should not be translated:

- Version numbers: `Text(verbatim: "v2.0.1")`
- URLs: `Text(verbatim: "https://example.com")`
- Identifiers and codes: `Text(verbatim: orderNumber)`
- Mathematical expressions: `Text(verbatim: "x + y = z")`
- Debug/development text: wrap in `#if DEBUG`

## Debug-Only Text

For text that only appears during development, combine `verbatim:` with conditional compilation:

```swift
#if DEBUG
Text(verbatim: "TODO: fix this layout")
Text(verbatim: "Debug: \(someValue)")
#endif
```

This ensures debug text never enters your String Catalog even during development, and is completely removed from release builds.

## Summary

- `Text("key")` — literal is treated as a `LocalizedStringKey`, extracted to String Catalog, and looked up at runtime for translation
- `Text(verbatim: "text")` — displayed as-is, never extracted, no localization lookup
- `#if DEBUG` — conditional compilation removes the code entirely from release builds

Any string that a translator should not see must use `Text(verbatim:)` or be guarded by `#if DEBUG`.
