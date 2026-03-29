# VoiceOver Labeling for a Product Card

## The Problem

Your current code has several VoiceOver issues:

1. **Each element is announced separately** -- VoiceOver will focus on the name, then the price, then each individual star image one at a time (five separate focus stops). This creates a tedious, fragmented experience.
2. **The star images have no meaningful labels** -- VoiceOver will announce something like "star.fill, image" for each star, which conveys no useful information about the rating.
3. **There is no semantic grouping** -- the card is not presented as a single cohesive item.

## Recommended Approach

Group the entire card into a single accessible element with a combined label:

```swift
VStack {
    Text(product.name)
    Text("$\(product.price)")
    HStack {
        ForEach(0..<5) { i in
            Image(systemName: i < product.rating ? "star.fill" : "star")
        }
    }
}
.accessibilityElement(children: .combine)
.accessibilityLabel("\(product.name), \(product.price) dollars, rated \(product.rating) out of 5 stars")
```

### What This Does

- **`.accessibilityElement(children: .combine)`** -- Merges all child elements into a single focusable element. VoiceOver users land on the card once instead of navigating through each sub-element.
- **`.accessibilityLabel(...)`** -- Provides a clear, human-readable description that conveys all the information in one announcement: the product name, the price, and the rating in plain language.

## A More Robust Version

For production code, consider adding traits and actions:

```swift
VStack {
    Text(product.name)
        .font(.headline)
    Text("$\(product.price, specifier: "%.2f")")
    HStack {
        ForEach(0..<5) { i in
            Image(systemName: i < product.rating ? "star.fill" : "star")
                .foregroundColor(i < product.rating ? .yellow : .gray)
        }
    }
    .accessibilityHidden(true)
}
.accessibilityElement(children: .ignore)
.accessibilityLabel(product.name)
.accessibilityValue("\(product.price, specifier: "%.2f") dollars, \(product.rating) out of 5 stars")
.accessibilityAddTraits(.isButton) // if the card is tappable
```

### Key Differences in This Version

| Modifier | Purpose |
|---|---|
| `.accessibilityElement(children: .ignore)` | Ignores children entirely and uses only the explicitly set label/value. Gives you full control over what is announced. |
| `.accessibilityLabel(...)` | The primary identity of the element (the product name). |
| `.accessibilityValue(...)` | The state or value (price and rating). Separating label from value lets VoiceOver announce them with the right intonation and allows users to hear just the label when swiping quickly. |
| `.accessibilityAddTraits(.isButton)` | Tells VoiceOver this element is interactive, so it announces "button" and users know they can double-tap to activate it. Only add this if the card is tappable. |
| `.accessibilityHidden(true)` on the star `HStack` | Explicitly hides the star images from VoiceOver since the rating is already conveyed through the accessibility value. |

## What VoiceOver Will Announce

With the recommended approach, a user hears a single announcement like:

> "Wireless Headphones, 49.99 dollars, rated 4 out of 5 stars, button"

Instead of the broken experience:

> "Wireless Headphones" ... "49.99 dollars" ... "star.fill, image" ... "star.fill, image" ... "star.fill, image" ... "star.fill, image" ... "star, image"

## Summary of Best Practices

1. **Combine related elements** into a single accessible element using `.accessibilityElement(children: .combine)` or `.accessibilityElement(children: .ignore)`.
2. **Use plain language** for ratings -- say "rated 4 out of 5 stars" instead of letting VoiceOver read each star image.
3. **Separate label from value** when the element has a name (label) and a changeable state (value).
4. **Add traits** like `.isButton` when the element is interactive so users know they can act on it.
5. **Hide decorative elements** that are already described by the parent's accessibility properties.
