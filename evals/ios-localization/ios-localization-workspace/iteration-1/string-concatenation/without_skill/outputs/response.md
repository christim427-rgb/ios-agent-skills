# String Concatenation Localization Problem

## The Problem

The code concatenates localized and non-localized fragments:

```swift
let message = NSLocalizedString("hello", comment: "") + ", " + userName + "!"
```

This locks the sentence into English word order: `[greeting], [name]!`. Many languages have different word order. For example, in Japanese the name might come first, or in other languages the greeting structure is entirely different. Translators cannot rearrange the pieces because each fragment is a separate string.

Additionally, the `comment` parameter is empty, giving translators no context.

## The Fix

Use a single format string with positional specifiers so translators can reorder the arguments:

```swift
let format = NSLocalizedString("greeting.message",
                                comment: "Greeting shown on home screen. %1$@ is the user's display name")
let message = String(format: format, userName)
```

In your Localizable.strings:

```
/* English */
"greeting.message" = "Hello, %1$@!";
```

A translator for another language can reorder this freely:

```
/* Example: another language where name comes first */
"greeting.message" = "%1$@, hello!";
```

## Why Positional Specifiers (%1$@)

Use `%1$@` instead of plain `%@`. When there are multiple arguments, positional specifiers (like `%1$@` and `%2$@`) allow translators to place arguments in any order without changing the code. Even with a single argument, it is a good habit that prevents problems when strings are later expanded.
