# Fixing HStack Overflow at Accessibility Text Sizes

Your layout breaks at accessibility text sizes because `HStack` distributes space horizontally — when both `Text` views grow large, they overflow and clip. This is a **HIGH severity** Dynamic Type issue (breaks under accessibility settings, affects 25%+ of users who change text size).

## What's Going Wrong

At the five accessibility size categories (`accessibilityMedium` through `accessibilityExtraExtraExtraLarge`), `.headline` and `.subheadline` fonts can grow 2–3x their default sizes. A fixed horizontal layout cannot accommodate this: `user.name` and `user.role` compete for space, one or both get clipped, and the icon may be pushed out entirely.

## The Fix: Three Approaches (Pick One)

### Option 1 — `ViewThatFits` (iOS 16+, Recommended)

`ViewThatFits` automatically measures whether the HStack fits. If it overflows, it falls back to the VStack — no environment variable needed, no manual threshold.

```swift
ViewThatFits {
    // Preferred layout — used when space allows
    HStack {
        Image(systemName: "person.fill")
            .accessibilityHidden(true)
        Text(user.name)
            .font(.headline)
        Spacer()
        Text(user.role)
            .font(.subheadline)
            .foregroundStyle(.secondary)
    }
    // Fallback layout — used at large accessibility sizes
    VStack(alignment: .leading, spacing: 4) {
        HStack(spacing: 8) {
            Image(systemName: "person.fill")
                .accessibilityHidden(true)
            Text(user.name)
                .font(.headline)
        }
        Text(user.role)
            .font(.subheadline)
            .foregroundStyle(.secondary)
    }
}
.accessibilityElement(children: .combine)
```

`ViewThatFits` tries each child in order and picks the first one that fits without clipping. It handles intermediate sizes automatically — you don't need to know the exact threshold.

---

### Option 2 — `AnyLayout` (iOS 16+, preserves state across transitions)

Use `AnyLayout` when your content has `@State` that should survive the layout switch (e.g., a focused text field, an expanded disclosure). `ViewThatFits` re-renders its content; `AnyLayout` does not.

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    let layout = dynamicTypeSize.isAccessibilitySize
        ? AnyLayout(VStackLayout(alignment: .leading, spacing: 4))
        : AnyLayout(HStackLayout())

    layout {
        Image(systemName: "person.fill")
            .accessibilityHidden(true)
        Text(user.name)
            .font(.headline)
        Spacer()
        Text(user.role)
            .font(.subheadline)
            .foregroundStyle(.secondary)
    }
    .accessibilityElement(children: .combine)
}
```

`isAccessibilitySize` returns `true` starting at `accessibilityMedium` (category 8 of 12), which is the Apple-recommended threshold for layout adaptation.

---

### Option 3 — Manual `if/else` (iOS 15 and earlier)

If you must support iOS 15, use an explicit environment check:

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    Group {
        if dynamicTypeSize.isAccessibilitySize {
            VStack(alignment: .leading, spacing: 4) {
                HStack(spacing: 8) {
                    Image(systemName: "person.fill")
                        .accessibilityHidden(true)
                    Text(user.name)
                        .font(.headline)
                }
                Text(user.role)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        } else {
            HStack {
                Image(systemName: "person.fill")
                    .accessibilityHidden(true)
                Text(user.name)
                    .font(.headline)
                Spacer()
                Text(user.role)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        }
    }
    .accessibilityElement(children: .combine)
}
```

---

## Additional Issues in the Original Code

Beyond the layout overflow, there are two more problems in your snippet:

### 1. The icon lacks an accessibility label (CRITICAL)

`Image(systemName: "person.fill")` inside a layout reads as "person fill" to VoiceOver — a meaningless SF Symbol name. Since it's decorative here (the name and role already identify the person), hide it:

```swift
// ❌ Reads "person fill" to VoiceOver
Image(systemName: "person.fill")

// ✅ Hidden from VoiceOver — content already conveyed by Text views
Image(systemName: "person.fill")
    .accessibilityHidden(true)
```

If the icon were informative (e.g., indicating online status), add `.accessibilityLabel("Online")` instead.

### 2. Hardcoded color risk

The original code does not set `foregroundStyle` on `user.role`. If you were using `.foregroundColor(.gray)` elsewhere in this cell, replace it with `.foregroundStyle(.secondary)` — `.secondary` adapts to dark mode and high contrast mode automatically.

---

## VoiceOver Behavior After the Fix

With `.accessibilityElement(children: .combine)` on the container:

- **VoiceOver reads:** "[user.name], [user.role]" as a single focusable element
- Users navigate to this row once, not three times (icon, name, role separately)
- The layout change is invisible to VoiceOver — the reading order stays logical

---

## Checklist

- [x] Layout adapts at accessibility sizes (HStack → VStack)
- [x] Fonts use Dynamic Type styles (`.headline`, `.subheadline`) — already correct
- [x] Decorative icon hidden from VoiceOver with `.accessibilityHidden(true)`
- [x] Semantic color used for secondary text (`.foregroundStyle(.secondary)`)
- [x] Related elements grouped with `.accessibilityElement(children: .combine)`
- [x] No hardcoded font sizes (`.system(size:)`)
- [x] No `onTapGesture` (layout-only view — correct)
