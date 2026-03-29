# HStack Layout Overflow at Accessibility Text Sizes

## The Problem

At the five largest Dynamic Type sizes (`accessibilityMedium` through `accessibilityExtraExtraExtraLarge`), text can be 2–4x its default size. An `HStack` with a label and an icon that looks fine at default size will overflow or truncate at accessibility sizes, cutting off content and breaking WCAG 1.4.4 (Resize Text).

---

## Four-Part Solution

### 1. Detect Accessibility Sizes with `dynamicTypeSize.isAccessibilitySize`

The `isAccessibilitySize` property returns `true` for the five accessibility size categories (sizes 8–12 out of 12). Use it to switch layout strategy:

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var body: some View {
    if dynamicTypeSize.isAccessibilitySize {
        VStack(alignment: .leading) { content }
    } else {
        HStack { content }
    }
}
```

---

### 2. `ViewThatFits` — Automatic Layout Switching (iOS 16+)

`ViewThatFits` automatically chooses the first layout that fits in the available space. This is the cleanest approach when you have two layout options:

```swift
struct NotificationRow: View {
    let icon: String
    let title: String
    let subtitle: String

    var body: some View {
        ViewThatFits {
            // Preferred: horizontal layout (used at smaller text sizes)
            HStack(alignment: .top, spacing: 12) {
                iconView
                textContent
            }

            // Fallback: vertical layout (used when HStack would overflow)
            VStack(alignment: .leading, spacing: 8) {
                iconView
                textContent
            }
        }
        .padding()
    }

    @ViewBuilder var iconView: some View {
        Image(systemName: icon)
            .font(.title2)
            .frame(width: iconSize, height: iconSize)
            .foregroundStyle(.tint)
    }

    @ViewBuilder var textContent: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.headline)
            Text(subtitle)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
    }
}
```

`ViewThatFits` measures each option and uses the first one that doesn't clip or overflow. No manual threshold checking needed.

---

### 3. `@ScaledMetric` for Icon Size

When layout switches to vertical and icon size needs to scale proportionally, use `@ScaledMetric`:

```swift
struct NotificationRow: View {
    // @ScaledMetric scales this value proportionally with Dynamic Type
    // relativeTo: .title2 means it scales at the same rate as title2 text
    @ScaledMetric(relativeTo: .title2) private var iconSize: CGFloat = 28

    var body: some View {
        ViewThatFits {
            HStack {
                Image(systemName: "bell.fill")
                    .font(.system(size: iconSize))  // Scaled icon
                    // OR for SF Symbols, let .font() handle it:
                    // .font(.title2)  // SF Symbols scale automatically with font

                VStack(alignment: .leading) {
                    Text("New Message")
                        .font(.headline)
                    Text("You have 3 unread messages")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }

            VStack(alignment: .leading, spacing: 12) {
                Image(systemName: "bell.fill")
                    .font(.system(size: iconSize))

                VStack(alignment: .leading) {
                    Text("New Message")
                        .font(.headline)
                    Text("You have 3 unread messages")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .padding()
    }
}
```

**SF Symbol note:** SF Symbols scale automatically when given a `.font()` modifier. Use `@ScaledMetric` for custom images or non-SF assets. Do NOT use `.resizable()` + `.frame()` with hardcoded values on SF Symbols.

---

### 4. Wrap in `ScrollView` for Overflow Protection

At the largest accessibility sizes, even a vertical layout may overflow a fixed-height container or the screen itself. Wrapping in `ScrollView` ensures content remains reachable:

```swift
// ❌ May clip at the largest accessibility sizes
VStack {
    ForEach(items) { item in
        NotificationRow(...)
    }
}

// ✅ Always scrollable
ScrollView {
    VStack(spacing: 0) {
        ForEach(items) { item in
            NotificationRow(...)
            Divider()
        }
    }
}
```

For a view that only needs to scroll at large sizes (to avoid unnecessary scroll indicators at normal sizes), use `ViewThatFits(in: .vertical)`:

```swift
// Scroll only when content overflows vertically
ViewThatFits(in: .vertical) {
    VStack { content }          // No scroll — fits without scrolling
    ScrollView { VStack { content } }  // Scroll — when it overflows
}
```

---

## Complete Pattern

```swift
struct SettingsRow: View {
    let icon: String
    let title: String
    let value: String

    @ScaledMetric(relativeTo: .body) private var iconSize: CGFloat = 24

    var body: some View {
        ViewThatFits {
            // Horizontal: icon + label on left, value on right
            HStack(spacing: 12) {
                iconView
                Text(title).font(.body)
                Spacer()
                Text(value).font(.body).foregroundStyle(.secondary)
            }

            // Vertical: stack everything
            VStack(alignment: .leading, spacing: 8) {
                HStack(spacing: 8) {
                    iconView
                    Text(title).font(.body)
                }
                Text(value)
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .padding(.leading, iconSize + 8)
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 16)
    }

    private var iconView: some View {
        Image(systemName: icon)
            .font(.system(size: iconSize))
            .foregroundStyle(.tint)
            .frame(width: iconSize, height: iconSize)
    }
}
```

---

## AnyLayout — When You Need State Preservation

If your layout has internal state (e.g., animations, `@State`), `ViewThatFits` recreates the view which resets state. Use `AnyLayout` to switch layout engine while preserving view identity:

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

var layout: AnyLayout {
    dynamicTypeSize.isAccessibilitySize
        ? AnyLayout(VStackLayout(alignment: .leading))
        : AnyLayout(HStackLayout(alignment: .top))
}

var body: some View {
    layout {
        iconView
        textContent
    }
}
```

---

## Summary

| Technique | Use When |
|---|---|
| `dynamicTypeSize.isAccessibilitySize` | Manual threshold check, maximum control |
| `ViewThatFits` | Automatic — best for most cases (iOS 16+) |
| `AnyLayout` | State must be preserved across layout changes |
| `@ScaledMetric(relativeTo:)` | Non-text dimensions: icon sizes, spacing, avatar sizes |
| `ScrollView` | Any content that may overflow at large text sizes |
