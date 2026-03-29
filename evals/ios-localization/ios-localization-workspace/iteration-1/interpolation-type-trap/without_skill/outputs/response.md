# SwiftUI String Interpolation Type Trap

## The Problem

```swift
let label = "Delete \(Image(systemName: "trash"))"
Text(label)
```

The `Image` disappears because Swift infers `label` as type `String`. The `String` type uses `DefaultStringInterpolation`, which calls `.description` on the `Image` -- it does not know how to embed an image inline. The image information is lost, and you get something like `"Delete Image(...)"` or just `"Delete "`.

## Why It Happens

`LocalizedStringKey` has a custom `StringInterpolation` that knows how to handle special types like `Image`, `Date`, and `Text`. When you use `Text("Delete \(Image(systemName: "trash"))")` with a direct literal, Swift infers the type as `LocalizedStringKey`, and the custom interpolation kicks in.

But when you assign the interpolated string to a variable, Swift infers the variable type as `String` (since that is the default for string literals with interpolation). The `String` type does not have the special interpolation for `Image`.

## The Fix

Explicitly annotate the type as `LocalizedStringKey`:

```swift
let label: LocalizedStringKey = "Delete \(Image(systemName: "trash"))"
Text(label)
```

Now Swift uses `LocalizedStringKey.StringInterpolation`, which properly handles the `Image` type, and the trash icon will appear inline in the text.

## General Rule

Whenever you use string interpolation with SwiftUI-specific types (`Image`, `Date`, `Text`) and store the result in a variable, you must explicitly annotate the type as `LocalizedStringKey`. Otherwise, Swift defaults to `String` and loses the rich interpolation capabilities.
