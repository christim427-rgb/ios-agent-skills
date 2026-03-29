# Accessibility Problem: Hardcoded Colors Break Dark Mode Contrast

## The Issue

```swift
Text("Hello").foregroundColor(.black)
    .background(Color.white)
```

This code hardcodes both the text color (`.black`) and background color (`.white`). While black-on-white has an excellent contrast ratio (~21:1, well above WCAG AA and AAA requirements), it creates a **critical accessibility failure in Dark Mode**.

## What Goes Wrong

When a user enables Dark Mode on iOS, the system automatically inverts or adapts semantic colors — but hardcoded colors like `.black` and `.white` do **not** adapt. The result:

- **Dark Mode background**: The app's surrounding UI turns dark, but this view's background stays **white** — creating an unwanted bright rectangle.
- **Text color**: The text stays **black** on a white background, which might still be readable — but it breaks the visual design and ignores the user's system preference.
- **High Contrast mode + Dark Mode**: Users who enable both "Increase Contrast" and Dark Mode will see hardcoded colors that completely ignore their accessibility needs.

## Who Is Affected

- Users who rely on Dark Mode to reduce eye strain (including many users with photosensitivity or migraines).
- Users with low vision who configure system-wide display settings.
- Elderly users who commonly use larger text and display accommodations.

## The Fix

Use **adaptive/semantic colors** that automatically respond to the current color scheme:

```swift
// Option 1: Use semantic label color (adapts to light/dark automatically)
Text("Hello")
    .foregroundColor(.primary)
    .background(Color(UIColor.systemBackground))

// Option 2: Use the environment's colorScheme (for custom logic)
@Environment(\.colorScheme) var colorScheme

Text("Hello")
    .foregroundColor(colorScheme == .dark ? .white : .black)
    .background(colorScheme == .dark ? Color.black : Color.white)

// Option 3: Define an asset catalog color with light/dark variants
// Then reference it as:
Text("Hello")
    .foregroundColor(Color("MyTextColor"))
    .background(Color("MyBackgroundColor"))
```

## Best Practice

Prefer semantic system colors whenever possible:

| Instead of | Use |
|---|---|
| `.black` | `.primary` |
| `.white` | `.secondary` or `Color(UIColor.systemBackground)` |
| `Color.gray` | `Color(UIColor.systemGray)` |

Semantic colors like `.primary`, `.secondary`, and `UIColor.systemBackground` are defined by the system and automatically switch between light and dark appearances — no extra code needed.

## Summary

The accessibility problem is not the contrast ratio itself (black on white is high contrast), but the **rigidity of hardcoded colors**, which:
1. Fails to respect the user's Dark Mode preference.
2. Breaks the visual experience for users who depend on system-level display adaptations.
3. Violates Apple's Human Interface Guidelines, which explicitly recommend using dynamic/semantic colors.
