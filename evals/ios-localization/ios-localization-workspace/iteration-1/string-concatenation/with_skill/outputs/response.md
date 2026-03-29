The localization problem here is **string concatenation**, which locks the word order into the English pattern and prevents translators from reordering words for other languages.

## The Problem

```swift
let message = NSLocalizedString("hello", comment: "") + ", " + userName + "!"
```

This constructs the greeting by concatenating fragments: a localized "Hello", a comma, the user's name, and an exclamation mark. The resulting word order is always `[greeting], [name]!` — which is English word order.

Many languages need a completely different word order. For example:
- Japanese might need: `[name]さん、こんにちは！` (name comes first)
- Arabic might need the name in a different position relative to the greeting
- Korean: `[name]님, 안녕하세요!`

With concatenation, the translator can only translate the word "hello" — they have no control over where the name appears, what punctuation surrounds it, or the overall sentence structure.

Additionally, the comment is empty (`comment: ""`), giving the translator zero context.

## The Fix

Use a single format string with **positional format specifiers** so translators can reorder arguments:

```swift
let format = NSLocalizedString(
    "greeting_format",
    comment: "Greeting with user name. %1$@ = user's display name, e.g. 'Hello, Maria!'"
)
let message = String(format: format, userName)
```

The English translation string would be:
```
"greeting_format" = "Hello, %1$@!";
```

A Japanese translator could reorder this to:
```
"greeting_format" = "%1$@さん、こんにちは！";
```

### Why positional specifiers matter

Using `%1$@` instead of just `%@` is critical when there are multiple arguments. Positional specifiers (`%1$@`, `%2$@`) allow translators to place arguments in any order. Without them, translators are locked into the argument order defined in the code.

For example, with a two-argument format:
```swift
// English: "%1$@ invited %2$@ to the group"
// Korean:  "%2$@을(를) %1$@이(가) 그룹에 초대했습니다"
```

Korean reverses the subject/object order — this is only possible with positional specifiers.

On iOS 15+, prefer `String(localized:)`:

```swift
let message = String(
    localized: "greeting_format \(userName)",
    comment: "Greeting with user name. Variable is the user's display name, e.g. 'Hello, Maria!'"
)
```
