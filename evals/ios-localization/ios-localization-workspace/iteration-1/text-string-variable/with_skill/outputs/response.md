The localization does not work because `key` is a `String` variable, not a string literal. SwiftUI's `Text` has two different initializers, and the compiler selects the wrong one when you pass a variable.

## The Mechanism

```swift
let key = "greeting_key"
Text(key)  // Displays literal "greeting_key" — NO localization
```

SwiftUI's `Text` has two relevant initializers:

1. `Text(_ key: LocalizedStringKey)` — accepts string **literals** and performs localization lookup
2. `Text<S: StringProtocol>(_ content: S)` — accepts `String` variables and displays them verbatim

When you pass a string **literal** like `Text("greeting_key")`, the compiler matches the `LocalizedStringKey` overload because `LocalizedStringKey` conforms to `ExpressibleByStringLiteral`. This triggers localization lookup.

When you pass a `String` **variable** like `Text(key)`, the compiler matches the `StringProtocol` overload instead. The string is displayed as-is with no localization lookup. You see the raw key text "greeting_key" on screen.

This is a subtle but critical distinction: only string **literals** trigger automatic localization in SwiftUI.

## The Fix

Explicitly convert the variable to `LocalizedStringKey`:

```swift
let key = "greeting_key"
Text(LocalizedStringKey(key))  // Performs localization lookup
```

## When Each Pattern is Appropriate

```swift
// Static key known at compile time — use a literal (preferred)
Text("greeting_key")

// Dynamic key from a variable (e.g., from a server or config)
Text(LocalizedStringKey(key))

// Non-localizable content — use verbatim
Text(verbatim: "v2.0.1")
Text(verbatim: someIdentifier)
```

## Why This Matters

This is one of the most common SwiftUI localization traps. It is particularly insidious because:

1. It produces no compiler warning
2. In English testing, the key name might look plausible as display text
3. The fix is a simple wrapper, but you have to know the problem exists

Whenever you see `Text(someVariable)` where `someVariable` is a `String`, check whether localization was intended. If yes, wrap it in `LocalizedStringKey()`. If no (e.g., it is a user-entered value, identifier, or computed non-localizable string), consider using `Text(verbatim:)` to make the intent explicit.
