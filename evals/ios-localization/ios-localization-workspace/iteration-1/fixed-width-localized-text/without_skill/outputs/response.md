# German Translations Getting Truncated

## The Problem

The issue is the **fixed width** of 120 points:

```swift
Text(localizedString).frame(width: 120)
```

German text is significantly longer than English -- on average **30% or more** longer. Some German compound words can be extremely long. A fixed-width frame that fits English text perfectly will often truncate German (and other languages like Finnish, Greek, or Russian).

For example:
- English: "Settings" (8 characters)
- German: "Einstellungen" (13 characters)

## The Fix

Remove the fixed width and use flexible layout instead:

```swift
// Option 1: Let the text size itself naturally
Text(localizedString)

// Option 2: Use a maximum width if you need to constrain it
Text(localizedString)
    .frame(maxWidth: .infinity, alignment: .leading)

// Option 3: Use flexible width with a minimum
Text(localizedString)
    .frame(minWidth: 80, maxWidth: 200)

// Option 4: Allow line wrapping if the text is long
Text(localizedString)
    .lineLimit(nil)
    .fixedSize(horizontal: false, vertical: true)
```

## General Principle

Never apply fixed widths to localized text. Different languages have very different text lengths:

- **German, Finnish, Greek**: 30-50% longer than English
- **Chinese, Japanese, Korean**: Often shorter in character count but may need more height
- **Arabic, Thai**: Different character widths and ligature behavior

## Testing Text Expansion

You can test how your app handles text expansion without actual translations using Xcode's **Double Length Pseudolanguage**:

1. Edit your scheme in Xcode
2. Go to Run > Options
3. Set "Application Language" to "Double Length Pseudolanguage"

This will double the length of all your localized strings, making it easy to spot truncation issues throughout your app.

## UIKit Equivalent

In UIKit, the same principle applies -- avoid fixed-width constraints on localized labels:

```swift
// Bad: fixed width
label.widthAnchor.constraint(equalToConstant: 120)

// Good: let Auto Layout handle it
label.setContentHuggingPriority(.defaultHigh, for: .horizontal)
label.setContentCompressionResistancePriority(.required, for: .horizontal)
```
