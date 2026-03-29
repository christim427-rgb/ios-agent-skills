# Product Card VoiceOver Grouping with Rating Stars

## The Problem

A product card without grouping forces VoiceOver users to swipe through each individual element separately: the name, the price, and then each of the 5 star images one by one — that's 7 or more swipes just to understand one product. Additionally, star images labeled by VoiceOver as "star" or "star fill" give no meaningful rating information.

---

## Strategy: `.accessibilityElement(children: .ignore)` + Custom Label

Use `.ignore` (not `.combine`) because the rating needs a natural language description like "Rated 4 out of 5 stars" rather than the default joined output of combining 5 image labels.

### Step 1: Hide individual star images

Each `Image` inside the star `ForEach` must be hidden from VoiceOver — they are purely decorative within the grouped element.

### Step 2: Provide a natural rating description on the parent

The parent card gets a single coherent `accessibilityLabel` that reads like a sentence.

---

## Complete Implementation

```swift
struct ProductCard: View {
    let name: String
    let price: String
    let rating: Int  // 1-5

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text(name)
                .font(.headline)

            Text(price)
                .font(.subheadline)
                .foregroundStyle(.secondary)

            // Star rating — individual stars are decorative within the group
            HStack(spacing: 2) {
                ForEach(0..<5) { index in
                    Image(systemName: index < rating ? "star.fill" : "star")
                        .foregroundStyle(index < rating ? .yellow : .gray)
                        .accessibilityHidden(true)  // Hide each star from VoiceOver
                }
            }
        }
        .padding()
        // Group the entire card as one element
        .accessibilityElement(children: .ignore)
        // Provide a natural, complete description
        .accessibilityLabel("\(name), \(price), rated \(rating) out of 5 stars")
    }
}
```

**VoiceOver reads:** "Wireless Headphones, $79.99, rated 4 out of 5 stars"

---

## Why `.ignore` Instead of `.combine`

| Approach | VoiceOver Output | Quality |
|---|---|---|
| No grouping | 7 separate swipes: "Wireless Headphones", "$79.99", "star fill", "star fill", "star fill", "star fill", "star" | Poor — star images read individually |
| `.combine` | "Wireless Headphones, $79.99" (stars still hidden) | Acceptable but robotic with comma pauses |
| `.ignore` + custom label | "Wireless Headphones, $79.99, rated 4 out of 5 stars" | Natural sentence, single swipe |

`.combine` joins children's labels with pauses. `.ignore` lets you write a coherent, human-readable sentence. For a product card where the rating needs natural language ("rated 4 out of 5 stars"), `.ignore` is the correct choice.

---

## Accessibility Checklist for This Pattern

- [x] Individual star images hidden with `.accessibilityHidden(true)`
- [x] Card grouped as single element with `.accessibilityElement(children: .ignore)`
- [x] Label is a natural sentence describing name, price, and rating
- [x] Rating expressed as "X out of 5 stars" (not "4 star fill, 1 star")
- [x] No element type in label (VoiceOver will not add a trait announcement since this is a non-interactive static group)

---

## If the Card Is Tappable

If the entire card is a tappable navigation element, wrap it in a `Button` instead:

```swift
Button {
    navigateToProduct()
} label: {
    // card content
}
.accessibilityLabel("\(name), \(price), rated \(rating) out of 5 stars")
// VoiceOver reads: "Wireless Headphones, $79.99, rated 4 out of 5 stars, button"
```
