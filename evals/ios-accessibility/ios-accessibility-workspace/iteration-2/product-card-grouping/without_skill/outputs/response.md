## Labeling a Product Card for VoiceOver

### The Problem with Default Behavior

By default, VoiceOver treats each sub-view (name, price, rating) as a separate focus element, requiring multiple swipes to get through one card. For a list of products this is very tedious.

### Recommended Approach: Combine into a Single Accessible Element

Use `.accessibilityElement(children: .combine)` or craft a custom label that surfaces all relevant information in one focus stop.

#### Option 1 — `.accessibilityElement(children: .combine)` (quick)

```swift
VStack(alignment: .leading) {
    Text(product.name)
    Text(product.price, format: .currency(code: "USD"))
    StarRatingView(rating: product.rating) // must itself have a good label
}
.accessibilityElement(children: .combine)
```

SwiftUI concatenates the accessibility labels of all child views. This works well when each child already has a meaningful label, but the resulting string can be awkward if the rating view produces something like "★★★☆☆".

#### Option 2 — Explicit `.accessibilityLabel` (recommended)

```swift
VStack(alignment: .leading) {
    Text(product.name)
    Text(product.price, format: .currency(code: "USD"))
    StarRatingView(rating: product.rating)
}
.accessibilityElement(children: .ignore)
.accessibilityLabel("\(product.name), \(formattedPrice), \(product.rating) out of 5 stars")
```

This gives full control over what VoiceOver reads and avoids any awkward concatenation.

### Recommended Label Format

```
"<Product name>, <price>, <rating> out of 5 stars"
// e.g. "Running Shoes, $89.99, 4.2 out of 5 stars"
```

### Adding an Accessibility Hint (optional)

If the card is tappable, add a hint:

```swift
.accessibilityHint("Double-tap to view product details")
```

### Key Points

- Merge the card into **one focus element** — users should not need to swipe through name, price, and rating separately.
- Express the rating as a **spoken fraction** ("4 out of 5 stars") rather than relying on star symbols.
- Keep the label order logical: name first (most important), then price, then rating.
- If the card has action buttons (Add to cart, Wishlist), consider `.accessibilityAction` to expose them without breaking the single-focus model.
