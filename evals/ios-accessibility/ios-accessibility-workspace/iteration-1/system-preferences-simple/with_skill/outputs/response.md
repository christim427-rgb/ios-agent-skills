# Image(decorative:) vs Image("name").accessibilityHidden(true)

Both hide an image from VoiceOver and other assistive technologies, but they differ in semantics, scope, and intent.

---

## Summary

| | `Image(decorative: "name")` | `Image("name").accessibilityHidden(true)` |
|---|---|---|
| **Intent** | Declares the image is inherently decorative | Hides an image (or any view) from assistive technology at the call site |
| **Scope** | Image only | Any SwiftUI view, including containers with children |
| **API surface** | Image-specific initializer | Generic view modifier, applies to the full view tree rooted at that view |
| **Children hidden?** | N/A (Image has no accessibility children) | Yes — `.accessibilityHidden(true)` hides the view AND all of its accessibility children |
| **Preferred for images** | Yes | No — use `Image(decorative:)` instead |
| **Use on non-image views** | No | Yes — this is the correct API for hiding any non-image view |

---

## Image(decorative:)

`Image(decorative: "name")` is a SwiftUI `Image` initializer that marks the image as intentionally decorative. SwiftUI excludes it from the accessibility tree entirely — VoiceOver never visits it and it contributes nothing to the accessibility label of any containing group.

```swift
// Preferred pattern for decorative images
Image(decorative: "background-gradient")
Image(decorative: "separator-line")
```

**Why it is preferred over `.accessibilityHidden(true)` for images:**

- The intent is encoded at the type level, not as a runtime modifier. Another developer reading the code immediately understands the image has no semantic meaning.
- It cannot be accidentally removed by refactoring the modifier chain.
- The skill's critical rules (Rule 12) and Do's list explicitly require `Image(decorative:)` for decorative images over the modifier form.

---

## Image("name").accessibilityHidden(true)

`.accessibilityHidden(true)` is a general-purpose view modifier that removes a view — and the entire accessibility subtree below it — from assistive technology. It works on any `View`, not just images.

```swift
// Alternative — works, but Image(decorative:) is preferred for images
Image("separator").accessibilityHidden(true)

// Correct non-image use case: hide a redundant label that duplicates grouped content
LabelsView(bars: bars).accessibilityHidden(true)

// Correct non-image use case: hide a visual-only decoration that isn't an Image
Rectangle()
    .fill(Color(.separator))
    .frame(height: 1)
    .accessibilityHidden(true)
```

**When `.accessibilityHidden(true)` is the right choice:**

- The element you want to hide is not an `Image` (a `Rectangle`, `Shape`, custom view, `Text` that duplicates grouped content, etc.).
- You are hiding a container view and want all of its children hidden simultaneously.
- You are conditionally toggling visibility based on accessibility state (e.g., hiding a visual chart when a data table provides the same information).

**When it is the wrong choice:**

- You are hiding a plain `Image` that is purely decorative. Use `Image(decorative:)` instead.

---

## WCAG Mapping

Both approaches satisfy **WCAG 1.1.1 Non-text Content** (Level A) for purely decorative images. The criterion requires that decorative images either have an empty alt text or are implemented so that assistive technology ignores them. Both APIs achieve this.

---

## Practical Rule

```
Is the view you want to hide an Image?
├── YES → Is it purely decorative (removing it does not change meaning)?
│   ├── YES → Image(decorative: "name")          ← preferred
│   └── NO  → Add .accessibilityLabel("…")       ← it is informative, don't hide it
└── NO  → .accessibilityHidden(true)              ← correct API for non-image views
```

---

## Code Examples

```swift
// ✅ Decorative image — use the initializer form
Image(decorative: "background-gradient")

// ✅ Decorative non-image view — use the modifier
Rectangle()
    .fill(Color(.separator))
    .frame(height: 1)
    .accessibilityHidden(true)

// ✅ Hide a redundant label inside a grouped element
VStack {
    ChartView(data: data)          // Has full accessibility representation
    AxisLabelsView(data: data)     // Redundant — hidden so VoiceOver doesn't double-read
        .accessibilityHidden(true)
}

// ❌ Avoid — works but obscures intent; prefer Image(decorative:) for plain images
Image("separator").accessibilityHidden(true)

// ❌ Wrong — informative image should have a label, not be hidden
Image("product-photo").accessibilityHidden(true)
// Fix:
Image("product-photo").accessibilityLabel("Red running shoes, side view")
```
