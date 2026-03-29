# Fixing HStack Overflow with Dynamic Type / Accessibility Text Sizes

## The Problem

Your `HStack` is a fixed horizontal layout that doesn't adapt when the user increases text size via iOS Accessibility settings (Dynamic Type). At larger text sizes, the text views grow and the fixed horizontal arrangement causes overflow and clipping.

---

## Solution 1: Use `ViewThatFits` (iOS 16+)

The most idiomatic modern solution is `ViewThatFits`, which automatically switches between a horizontal and vertical layout depending on available space:

```swift
ViewThatFits {
    // Preferred: horizontal layout for normal/moderate text sizes
    HStack {
        Image(systemName: "person.fill")
        Text(user.name).font(.headline)
        Spacer()
        Text(user.role).font(.subheadline)
    }

    // Fallback: vertical layout for large accessibility text sizes
    VStack(alignment: .leading, spacing: 4) {
        HStack {
            Image(systemName: "person.fill")
            Text(user.name).font(.headline)
        }
        Text(user.role).font(.subheadline)
            .foregroundStyle(.secondary)
    }
}
```

`ViewThatFits` tries each child view in order and uses the first one that fits the available space — no manual checks needed.

---

## Solution 2: Detect Large Content Size Categories Manually

If you need iOS 15 support or want explicit control, read the environment's `sizeCategory` and branch your layout:

```swift
@Environment(\.dynamicTypeSize) private var dynamicTypeSize

var body: some View {
    let isAccessibilitySize = dynamicTypeSize.isAccessibilitySize

    if isAccessibilitySize {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Image(systemName: "person.fill")
                Text(user.name).font(.headline)
            }
            Text(user.role)
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    } else {
        HStack {
            Image(systemName: "person.fill")
            Text(user.name).font(.headline)
            Spacer()
            Text(user.role).font(.subheadline)
        }
    }
}
```

`.isAccessibilitySize` returns `true` for the five extra-large accessibility sizes (`.accessibility1` through `.accessibility5`).

---

## Solution 3: Allow Text to Wrap and Constrain the Layout

If a VStack fallback feels like overkill for your design, you can keep the HStack but let text wrap and limit the role label's width:

```swift
HStack(alignment: .top) {
    Image(systemName: "person.fill")
        .padding(.top, 2) // optically align icon with first line of text

    Text(user.name)
        .font(.headline)
        .fixedSize(horizontal: false, vertical: true) // allow vertical growth

    Spacer(minLength: 8)

    Text(user.role)
        .font(.subheadline)
        .fixedSize(horizontal: false, vertical: true)
        .multilineTextAlignment(.trailing)
}
```

`fixedSize(horizontal: false, vertical: true)` tells SwiftUI the view can grow vertically to fit its content instead of truncating.

---

## Recommendation

| Scenario | Best approach |
|---|---|
| iOS 16+ only | `ViewThatFits` — cleanest, no environment reads needed |
| iOS 15 support needed | `dynamicTypeSize.isAccessibilitySize` branch |
| Text is short, wrapping is acceptable | `fixedSize(horizontal: false, vertical: true)` |

For most row/cell layouts, **`ViewThatFits`** is the recommended approach. It handles the breakpoint automatically and keeps your layout logic declarative.

---

## Testing Tip

Test all seven accessibility sizes in the Xcode Canvas by adding the `DynamicTypeVariants` preview modifier:

```swift
#Preview {
    UserRow(user: .example)
        .previewLayout(.sizeThatFits)
        .padding()
}
// Or use the Accessibility Inspector in Simulator:
// Settings > Accessibility > Display & Text Size > Larger Text
```

You can also use the Environment Overrides panel in the Xcode debug bar (the slider icon) to live-change the text size while your app is running on Simulator.
