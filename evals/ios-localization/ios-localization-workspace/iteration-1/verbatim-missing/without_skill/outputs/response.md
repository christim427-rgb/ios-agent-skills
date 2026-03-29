# Preventing Non-Localizable Strings from Appearing in String Catalog

## The Problem

```swift
Text("v2.0.1")
Text("https://example.com/terms")
```

When you pass string literals to `Text()`, SwiftUI treats them as `LocalizedStringKey` and automatically extracts them into your String Catalog. Version strings and URLs should not be translated, so they are cluttering your localization files unnecessarily.

## Solution 1: Use `Text(verbatim:)`

The primary fix is to use the `verbatim:` parameter, which tells SwiftUI the string is not localizable:

```swift
Text(verbatim: "v2.0.1")
Text(verbatim: "https://example.com/terms")
```

`Text(verbatim:)` bypasses the localization system entirely. The string is displayed as-is and will not appear in your String Catalog.

## Solution 2: Conditional Compilation for Debug-Only Text

For strings that should only appear in debug builds (like version info in a debug menu), use `#if DEBUG`:

```swift
#if DEBUG
Text(verbatim: "v2.0.1 (build 42)")
#endif
```

This prevents the text from being compiled into release builds at all, so it cannot be extracted.

## When to Use `verbatim:`

Use `Text(verbatim:)` for any string that should never be translated:

- Version numbers
- URLs
- Email addresses
- Technical identifiers
- Brand names that should remain unchanged
- Code or markup strings

## Summary

`Text("literal")` with a plain string literal always attempts localization and extraction. If the content is not meant for translation, always use `Text(verbatim:)` to keep your String Catalog clean and avoid confusing translators with untranslatable content.
