# accessibilityIdentifier vs accessibilityLabel

## The Confusion

Setting `accessibilityIdentifier` does not make an element visible or readable to VoiceOver. It is a common mistake — and one of the most frequently documented AI coding assistant failures (F8 in the failure pattern catalog).

```swift
// ❌ VoiceOver reads nothing — identifier is testing-only
Image(systemName: "plus")
    .accessibilityIdentifier("add-button")
```

VoiceOver on this element: silence. The element is skipped entirely.

## What Each Property Does

| Property | Purpose | Who Uses It |
|---|---|---|
| `accessibilityIdentifier` | Uniquely identifies a UI element for automation | XCUITest, UI testing frameworks |
| `accessibilityLabel` | Human-readable name announced by assistive technology | VoiceOver, Switch Control, Voice Control |

`accessibilityIdentifier` is a testing hook. It is never surfaced to the user. VoiceOver does not read it. Voice Control cannot target an element using its identifier. It exists solely so test code can locate elements: `app.buttons["add-button"].tap()`.

## The Fix

Replace `accessibilityIdentifier` with `accessibilityLabel` for VoiceOver support:

```swift
// ✅ VoiceOver reads: "Add item. Button."
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

## Setting Both Independently

For elements that need both a test hook and a VoiceOver label, set them independently — they are separate properties and do not conflict:

```swift
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")          // VoiceOver reads this
.accessibilityIdentifier("add-button")   // XCUITest uses this
```

```swift
// XCTest — finds element by identifier, not by label
let addButton = app.buttons["add-button"]
XCTAssertTrue(addButton.exists)
addButton.tap()
```

## Why This Matters

The impact of this confusion is severe:

- **VoiceOver users** encounter a button that reads nothing — they cannot tell what the button does or that it is activatable
- **Voice Control users** cannot say "Tap [name]" because there is no label
- **Switch Control** will highlight the element but announce nothing

This is classified as a **CRITICAL** (🔴) issue — the element's purpose is completely hidden from assistive technology.

## Quick Reference

```swift
// For assistive technology (VoiceOver, Voice Control, Switch Control)
.accessibilityLabel("Human-readable description")

// For UI testing (XCUITest, automation)
.accessibilityIdentifier("machine-readable-id")

// Both can coexist — they serve different purposes
.accessibilityLabel("Add item")
.accessibilityIdentifier("add-button")
```
