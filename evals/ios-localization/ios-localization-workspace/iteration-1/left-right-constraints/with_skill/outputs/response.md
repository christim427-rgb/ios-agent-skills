# Localization Issue: Left/Right Constraints

This code has a **critical RTL localization bug**. You are using `leftAnchor` and `rightAnchor`, which are absolute and **never flip** for right-to-left (RTL) languages like Arabic and Hebrew. This affects over **400 million users** who read and write in RTL scripts.

## The Problem

```swift
// ❌ Never flips for RTL languages (Arabic, Hebrew)
NSLayoutConstraint.activate([
    label.leftAnchor.constraint(equalTo: view.leftAnchor, constant: 16),
    label.rightAnchor.constraint(equalTo: view.rightAnchor, constant: -16)
])
```

When an Arabic or Hebrew user runs your app, the text will still be pinned to the left side of the screen instead of the right side where it belongs. The layout appears mirrored and broken — text that should start from the right edge stays stuck on the left.

## The Fix

Replace `leftAnchor`/`rightAnchor` with `leadingAnchor`/`trailingAnchor`:

```swift
// ✅ Flips automatically for RTL languages
NSLayoutConstraint.activate([
    label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
    label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16)
])
```

- **Leading** = left in LTR (English), right in RTL (Arabic, Hebrew)
- **Trailing** = right in LTR, left in RTL

## Why This Matters

`left`/`right` anchors are absolute — they refer to the physical left and right edges of the screen regardless of language direction. `leading`/`trailing` are semantic — they adapt automatically based on the user's language. Arabic and Hebrew users expect the entire interface to mirror, with content starting from the right edge. Using `left`/`right` locks the layout into an LTR arrangement that feels completely backwards for RTL users.

This is a silent bug — the app does not crash; it just looks wrong for every RTL user. It affects Arabic (420M+ speakers), Hebrew, Persian, Urdu, and other RTL scripts.

## Additional Considerations

Also watch for these related RTL issues:
- Use `NSDirectionalEdgeInsets` (with `leading`/`trailing`) instead of `UIEdgeInsets` (with `left`/`right`)
- Set text alignment to `.natural` instead of `.left`
- In SwiftUI, `HStack` and `.padding(.leading)` already handle RTL correctly

You can test RTL layout without translations by using Xcode's **Right to Left Pseudolanguage** (Edit Scheme -> Options -> Application Language -> Right to Left Pseudolanguage).
