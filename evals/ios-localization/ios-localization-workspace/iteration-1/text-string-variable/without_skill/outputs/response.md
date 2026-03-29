# SwiftUI Text with String Variable -- Localization Trap

## The Problem

```swift
let key = "greeting_key"
Text(key)
```

This does **not** localize the string. It displays the literal text `"greeting_key"` instead of looking up the translation.

## Why It Happens

SwiftUI's `Text` has two relevant initializers:

1. `Text(_ key: LocalizedStringKey)` -- looks up the key in your localization files
2. `Text(_ content: some StringProtocol)` -- displays the string as-is, no localization

When you pass a **string literal** directly, Swift infers `LocalizedStringKey`:
```swift
Text("greeting_key") // LocalizedStringKey -- DOES localize
```

But when you pass a **String variable**, Swift infers `StringProtocol`:
```swift
let key = "greeting_key"
Text(key) // StringProtocol -- does NOT localize
```

The variable `key` is inferred as type `String`, which conforms to `StringProtocol`, so Swift chooses the non-localizing overload.

## The Fix

Explicitly wrap the variable in `LocalizedStringKey`:

```swift
let key = "greeting_key"
Text(LocalizedStringKey(key))
```

Or annotate the variable type:

```swift
let key: LocalizedStringKey = "greeting_key"
Text(key)
```

## Key Takeaway

In SwiftUI, only string **literals** passed directly to `Text()` trigger automatic localization. Any time you store a localization key in a variable (even if it is a `let` constant), you must explicitly convert it to `LocalizedStringKey` for localization to work.
