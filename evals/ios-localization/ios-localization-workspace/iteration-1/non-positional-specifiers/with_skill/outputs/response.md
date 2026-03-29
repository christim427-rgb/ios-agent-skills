There is a significant localization defect in this format string. The non-positional `%@` specifiers prevent translators from reordering the arguments, which many languages require.

## The Problem

```swift
let format = NSLocalizedString("invite_format", comment: "Invitation message")
// English: "%@ invited %@ to the group"
let message = String(format: format, senderName, receiverName)
```

With non-positional `%@`, the first `%@` always maps to `senderName` and the second always maps to `receiverName`. The translator cannot change this order.

This breaks languages where sentence structure differs from English. For example, in Korean the typical sentence structure places the object before the verb, and the subject/object order may reverse relative to English:

- **English:** "Alice invited Bob to the group"
- **Korean:** "Bob을(를) Alice이(가) 그룹에 초대했습니다" (Bob-object Alice-subject invited-to-the-group)

With non-positional `%@`, a Korean translator would be forced to write `"%@이(가) %@을(를) 그룹에 초대했습니다"` — but the first `%@` is always the sender, so the sentence would read "Alice-subject Bob-object invited" which puts the arguments in the English order, producing awkward or incorrect Korean.

Similar reordering is needed in Japanese, Arabic, and many other languages.

## The Fix

Use **positional format specifiers** — `%1$@` and `%2$@`:

```swift
let format = NSLocalizedString(
    "invite_format",
    comment: "Invitation message. %1$@ = sender's name, %2$@ = receiver's name. Example: 'Alice invited Bob to the group'"
)
let message = String(format: format, senderName, receiverName)
```

The English translation:
```
"invite_format" = "%1$@ invited %2$@ to the group";
```

The Korean translator can now freely reorder:
```
"invite_format" = "%2$@을(를) %1$@이(가) 그룹에 초대했습니다";
```

Here `%2$@` (receiver) comes first, and `%1$@` (sender) comes second — matching natural Korean word order.

## Additional Improvements

1. The comment `"Invitation message"` is too vague. Include what each placeholder represents and an example value, as shown in the fix above.

2. On iOS 15+, prefer `String(localized:)` over `NSLocalizedString`:

```swift
let message = String(
    localized: "invite_format \(senderName) \(receiverName)",
    comment: "Invitation message. First variable = sender name, second = receiver name"
)
```

Always use positional specifiers in any format string with two or more arguments. Even with a single argument, using `%1$@` is a good habit that protects against future changes.
