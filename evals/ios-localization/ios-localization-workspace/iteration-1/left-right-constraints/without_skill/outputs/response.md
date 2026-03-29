# Localization Issue with Left/Right Constraints

## The Problem

The code uses `leftAnchor` and `rightAnchor`, which are **absolute** layout anchors. These will always pin the label to the physical left and right sides of the screen, regardless of the user's language direction.

This is a significant problem for **Right-to-Left (RTL) languages** like Arabic and Hebrew. In RTL layouts, the reading direction is reversed, and UI elements should mirror accordingly. Using `leftAnchor`/`rightAnchor` prevents this mirroring from happening.

## The Fix

Replace `leftAnchor`/`rightAnchor` with `leadingAnchor`/`trailingAnchor`:

```swift
NSLayoutConstraint.activate([
    label.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
    label.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16)
])
```

- **`leadingAnchor`** maps to the **left** in LTR languages (English, French, etc.) and to the **right** in RTL languages (Arabic, Hebrew).
- **`trailingAnchor`** maps to the **right** in LTR and to the **left** in RTL.

## Why This Matters

Arabic and Hebrew are spoken by over 400 million people worldwide. If your app does not flip its layout for RTL users, the interface will feel unnatural and broken for a very large user base. Apple's Auto Layout system handles this automatically when you use leading/trailing anchors, so there is no extra work required beyond choosing the correct anchors.

## Additional Notes

- The same principle applies in Interface Builder: use "Leading" and "Trailing" constraints, not "Left" and "Right."
- In SwiftUI, `HStack` and padding modifiers like `.padding(.leading, 16)` already use semantic directions by default.
- Only use `leftAnchor`/`rightAnchor` when you specifically need absolute positioning (e.g., a fixed element that should never flip).
