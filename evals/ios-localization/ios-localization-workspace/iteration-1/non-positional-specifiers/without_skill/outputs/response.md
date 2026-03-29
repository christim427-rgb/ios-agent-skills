# Non-Positional Format Specifiers Issue

## The Problem

```swift
let format = NSLocalizedString("invite_format", comment: "Invitation message")
// English: "%@ invited %@ to the group"
let message = String(format: format, senderName, receiverName)
```

The format string uses plain `%@` specifiers. These are filled in order: the first `%@` gets `senderName`, the second gets `receiverName`. The translator **cannot** change the order of the arguments.

This is a problem because many languages structure sentences differently. For example, in Korean, the sentence structure might be:

> "%@ 님이 그룹에 %@ 님을 초대했습니다" (receiver, then sender)

With non-positional `%@`, a Korean translator cannot swap the arguments -- they are locked into the English argument order.

## The Fix

Use positional format specifiers `%1$@` and `%2$@`:

```swift
let format = NSLocalizedString("invite_format",
                                comment: "Invitation message. %1$@ is the sender's name, %2$@ is the receiver's name")
let message = String(format: format, senderName, receiverName)
```

English strings file:
```
"invite_format" = "%1$@ invited %2$@ to the group";
```

Korean strings file (reversed order):
```
"invite_format" = "%2$@ 님을 그룹에 %1$@ 님이 초대했습니다";
```

Now translators can place `%1$@` (sender) and `%2$@` (receiver) wherever their language's grammar requires, regardless of the order the arguments are passed in code.

## Rule of Thumb

Always use positional specifiers (`%1$@`, `%2$@`, `%1$lld`, etc.) in any localized format string with two or more arguments. This gives translators full freedom to reorder the placeholders.
