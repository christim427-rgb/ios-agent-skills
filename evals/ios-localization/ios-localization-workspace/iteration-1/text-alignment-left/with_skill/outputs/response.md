# Text Alignment: `.natural` vs `.left`

In a localized app, you should **always use `.natural`** and **never use `.left`** for text alignment.

## Why `.natural` Is Correct

`.natural` automatically adapts the text alignment based on the user's language direction:

- For **LTR languages** (English, French, German, etc.) — text aligns to the **left**
- For **RTL languages** (Arabic, Hebrew, Persian, Urdu) — text aligns to the **right**

This is exactly what users expect. Arabic readers expect body text to start from the right edge, just as English readers expect it from the left.

## Why `.left` Is Wrong

`.left` is an absolute direction — it pins text to the physical left edge of the screen regardless of the user's language. For Arabic and Hebrew users, this means:

- Body text starts on the wrong side of the screen
- The reading experience feels unnatural and disorienting
- The UI looks like a broken LTR layout, not a proper RTL one

```swift
// ❌ Always left — broken for RTL users
label.textAlignment = .left

// ✅ Auto-adapts to language direction
label.textAlignment = .natural
```

## SwiftUI

In SwiftUI, `.leading` is already direction-aware, so it automatically does the right thing:

```swift
Text("Hello").multilineTextAlignment(.leading)
```

## When to Use `.left` Intentionally

The only time `.left` is appropriate is for content that is inherently left-to-right regardless of language — for example, code snippets or specific technical content where left alignment is semantically meaningful rather than directional. For standard UI text, always use `.natural`.
