The Image disappears because Swift infers the type of `label` as `String`, which uses `DefaultStringInterpolation`. The `Image` is converted to its `.description` text representation instead of being rendered as an actual image.

## The Mechanism

```swift
let label = "Delete \(Image(systemName: "trash"))"
Text(label)
```

When Swift sees this string interpolation, it infers the type of `label` as `String`. The `String` type uses `DefaultStringInterpolation`, which calls `.description` on the interpolated `Image` value. The result is something like `"Delete Image(provider: ...)"` — a text description, not a rendered image.

`LocalizedStringKey`, on the other hand, has a **custom `StringInterpolation`** implementation that knows how to handle `Image`, `Date`, `Text`, and `FormatStyle` types. When a `LocalizedStringKey` encounters an interpolated `Image`, it embeds the image inline in the rendered text.

## The Fix

Explicitly annotate the type as `LocalizedStringKey`:

```swift
let label: LocalizedStringKey = "Delete \(Image(systemName: "trash"))"
Text(label)
```

With the explicit type annotation, Swift uses `LocalizedStringKey.StringInterpolation` instead of `DefaultStringInterpolation`. The `Image` is properly embedded and rendered inline with the text.

## Why This Matters

This trap affects any interpolation of non-String types in SwiftUI localized text:

```swift
// All of these need explicit LocalizedStringKey type annotation:

let dateLabel: LocalizedStringKey = "Created \(date, style: .date)"
let imageLabel: LocalizedStringKey = "Tap \(Image(systemName: "gear")) to open settings"
let styledLabel: LocalizedStringKey = "Hello \(Text(name).bold())"
```

Without the explicit type, Swift defaults to `String` interpolation and these rich content types are flattened to their text descriptions.

## General Rule

Whenever you interpolate `Image`, `Date` (with style), or `Text` into a string that will be used in a SwiftUI `Text` view, explicitly type the variable as `LocalizedStringKey`. If you pass it directly to `Text()` as a literal (without storing in a variable first), this is not an issue because `Text` already expects `LocalizedStringKey`.
