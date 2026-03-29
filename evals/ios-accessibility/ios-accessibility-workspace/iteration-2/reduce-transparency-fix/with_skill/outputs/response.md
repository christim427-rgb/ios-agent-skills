# Fixing .ultraThinMaterial with Reduce Transparency

## The Problem

`.ultraThinMaterial` (and other material backgrounds) use blur and translucency. When Reduce Transparency is enabled in Settings > Accessibility > Display & Text Size > Reduce Transparency, iOS increases opacity across the system UI. Your custom material backgrounds should follow suit.

When left unaddressed, blurred/translucent backgrounds become harder to read and may violate WCAG 1.4.3 (contrast) because the background color is unpredictable.

## Reading the Preference

```swift
@Environment(\.accessibilityReduceTransparency) var reduceTransparency
```

## Basic Fix

```swift
// ❌ Ignores Reduce Transparency — blurred background may be unreadable
.background(.ultraThinMaterial)

// ✅ Replaces material with solid background when Reduce Transparency is on
.background(
    reduceTransparency
        ? AnyShapeStyle(Color(.systemBackground))
        : AnyShapeStyle(.ultraThinMaterial)
)
```

## The Type Mismatch Problem

The reason `AnyShapeStyle` is required: `.ultraThinMaterial` is of type `Material`, while `Color(.systemBackground)` is of type `Color`. They both conform to `ShapeStyle`, but Swift requires the branches of a ternary expression to have the same concrete type. `AnyShapeStyle` type-erases both to a common type.

```swift
// ❌ Type error: "result values in '? :' expression have mismatching types"
.background(
    reduceTransparency ? Color(.systemBackground) : .ultraThinMaterial
)

// ✅ AnyShapeStyle resolves the type mismatch
.background(
    reduceTransparency
        ? AnyShapeStyle(Color(.systemBackground))
        : AnyShapeStyle(.ultraThinMaterial)
)
```

## Full Component Example

```swift
struct FloatingCard: View {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Notification")
                .font(.headline)
            Text("You have a new message from Alex")
                .font(.body)
                .foregroundStyle(.secondary)
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(
                    reduceTransparency
                        ? AnyShapeStyle(Color(.secondarySystemBackground))
                        : AnyShapeStyle(.regularMaterial)
                )
        )
        .shadow(radius: reduceTransparency ? 0 : 4)  // Drop shadow also less useful with solid bg
    }
}
```

## Replace All Material Variants

| Material | Solid Replacement |
|---|---|
| `.ultraThinMaterial` | `Color(.systemBackground)` |
| `.thinMaterial` | `Color(.systemBackground)` |
| `.regularMaterial` | `Color(.secondarySystemBackground)` |
| `.thickMaterial` | `Color(.secondarySystemBackground)` |
| `.ultraThickMaterial` | `Color(.tertiarySystemBackground)` |
| Custom blur overlay | `Color(.systemBackground).opacity(0.95)` |

Always use semantic system colors (not hardcoded `.white`) so the solid background adapts correctly to dark mode.

## Extracting a Helper

For reuse across the app:

```swift
extension ShapeStyle where Self == AnyShapeStyle {
    static func adaptive(
        reduced: some ShapeStyle,
        standard: some ShapeStyle,
        reduceTransparency: Bool
    ) -> AnyShapeStyle {
        AnyShapeStyle(reduceTransparency ? reduced : standard)
    }
}

// Usage
.background(
    .adaptive(
        reduced: Color(.systemBackground),
        standard: .ultraThinMaterial,
        reduceTransparency: reduceTransparency
    )
)
```

## ViewModifier Approach

```swift
struct MaterialBackground: ViewModifier {
    @Environment(\.accessibilityReduceTransparency) var reduceTransparency

    func body(content: Content) -> some View {
        content
            .background(
                reduceTransparency
                    ? AnyShapeStyle(Color(.systemBackground))
                    : AnyShapeStyle(.ultraThinMaterial)
            )
    }
}

extension View {
    func adaptiveMaterial() -> some View {
        modifier(MaterialBackground())
    }
}

// Usage
.adaptiveMaterial()
```
