# Labeling a Product Card for VoiceOver

Your product card has three issues to fix: the individual stars create excessive VoiceOver swipes, the card lacks grouping, and the star images will read as raw SF Symbol names. Here is how to make it accessible.

## The Problem

Without any accessibility modifiers, VoiceOver treats each child view as a separate element. A user would have to swipe through:

1. Product name
2. Price
3. "star.fill" (or "star") -- repeated five times

That is seven separate swipe targets for a single conceptual item.

## The Fix

Group the entire card and provide a meaningful custom label using `.accessibilityElement(children: .ignore)`:

```swift
VStack {
    Text(product.name)
        .font(.headline)
    Text(product.price, format: .currency(code: "USD"))
        .font(.subheadline)
    HStack {
        ForEach(0..<5) { i in
            Image(systemName: i < product.rating ? "star.fill" : "star")
                .foregroundStyle(.yellow)
        }
    }
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(product.name), \(product.price.formatted(.currency(code: "USD"))), \(product.rating) out of 5 stars")
```

**VoiceOver reads:** "Running Shoes, $59.99, 4 out of 5 stars"

One swipe, one clear announcement.

## Why `.ignore` Instead of `.combine`

You might think `.accessibilityElement(children: .combine)` is simpler. It merges child labels automatically, but here it produces a poor result:

- `.combine` would join the raw SF Symbol names for each star image, reading something like "Running Shoes, $59.99, star.fill, star.fill, star.fill, star.fill, star" -- meaningless and tedious.
- `.ignore` with a custom label lets you produce a natural sentence: "4 out of 5 stars" instead of listing five individual star icons.

Use `.combine` when the children's labels already make sense joined together. Use `.ignore` with a custom label when you need to rewrite the announcement into something coherent.

## If the Card Is Tappable

If the whole card navigates to a detail screen, wrap it in a `Button` (never `onTapGesture`):

```swift
Button {
    navigateToProduct(product)
} label: {
    VStack {
        Text(product.name)
            .font(.headline)
        Text(product.price, format: .currency(code: "USD"))
            .font(.subheadline)
        HStack {
            ForEach(0..<5) { i in
                Image(systemName: i < product.rating ? "star.fill" : "star")
                    .foregroundStyle(.yellow)
            }
        }
    }
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(product.name), \(product.price.formatted(.currency(code: "USD"))), \(product.rating) out of 5 stars")
.accessibilityHint("Opens product details")
```

**VoiceOver reads:** "Running Shoes, $59.99, 4 out of 5 stars. Button. Opens product details."

Key points:

- `Button` gives the card the `.button` trait automatically -- VoiceOver announces "Button" so do not include "button" in your label.
- The `.accessibilityHint` describes the **result** of activation, not the gesture.
- `onTapGesture` would make this card completely invisible to VoiceOver, Switch Control, and Full Keyboard Access.

## If the Card Has Multiple Actions

If the card also has a favorite button or add-to-cart button, use custom actions to avoid cluttering the swipe order:

```swift
VStack {
    Text(product.name)
        .font(.headline)
    Text(product.price, format: .currency(code: "USD"))
        .font(.subheadline)
    HStack {
        ForEach(0..<5) { i in
            Image(systemName: i < product.rating ? "star.fill" : "star")
                .foregroundStyle(.yellow)
        }
    }
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(product.name), \(product.price.formatted(.currency(code: "USD"))), \(product.rating) out of 5 stars")
.accessibilityCustomActions([
    .init(named: "Add to cart") { addToCart(product); return true },
    .init(named: "Toggle favorite") { toggleFavorite(product); return true }
])
```

VoiceOver users swipe up/down to cycle through actions instead of navigating to separate buttons.

## Additional Notes

- **Dynamic Type**: Use `.font(.headline)` and `.font(.subheadline)` instead of `.font(.system(size: 16))`. Your original code does not specify fonts, so make sure you use text styles when you do.
- **Semantic colors**: Use `.foregroundStyle(.yellow)` rather than a hardcoded color for the stars. If your design uses a custom star color, ensure it meets 3:1 contrast ratio against the background for non-text elements (WCAG 1.4.11).
- **Rating as `accessibilityValue`**: An alternative approach is to set the rating as an `accessibilityValue` rather than baking it into the label, which lets VoiceOver users distinguish the product identity from its attributes:

```swift
.accessibilityLabel("\(product.name), \(product.price.formatted(.currency(code: "USD")))")
.accessibilityValue("\(product.rating) out of 5 stars")
```

This separation is useful if the rating changes dynamically -- VoiceOver re-reads the value without repeating the full label.
