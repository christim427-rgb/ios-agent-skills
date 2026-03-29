# NSLocalizedString with String Interpolation

## The Problem

```swift
let message = NSLocalizedString("Hello \(userName)", comment: "Greeting")
```

This is **incorrect**. The string interpolation is evaluated **before** `NSLocalizedString` receives it. If `userName` is "Alice", the lookup key becomes `"Hello Alice"`. If `userName` is "Bob", the key becomes `"Hello Bob"`.

This means:
1. Every unique username creates a different localization key
2. None of these dynamic keys will exist in your `.strings` file
3. The function falls back to displaying the key itself (e.g., "Hello Alice"), which only works for English by accident
4. Translations are never found

## The Fix

Use a static key with `String(format:)`:

```swift
let format = NSLocalizedString("greeting.hello",
                                comment: "Greeting shown on home screen. %1$@ is the user's display name")
let message = String(format: format, userName)
```

In your Localizable.strings:
```
"greeting.hello" = "Hello, %1$@!";
```

Or with iOS 15+ `String(localized:)`:

```swift
let message = String(localized: "greeting.hello \(userName)",
                     comment: "Greeting shown on home screen with user's name")
```

Note that `String(localized:)` handles interpolation correctly -- it treats interpolated values as format arguments, not as part of the key. This is a key advantage of the modern API over `NSLocalizedString`.

## Rule

Never use string interpolation inside `NSLocalizedString()`. The key must be a static string literal that can be found in your localization files. Use format strings with placeholders to insert dynamic values.
