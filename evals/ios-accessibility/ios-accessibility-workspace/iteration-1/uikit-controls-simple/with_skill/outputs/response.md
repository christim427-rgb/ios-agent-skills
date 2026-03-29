# Why VoiceOver Doesn't Read Anything Useful

## Root Cause: F8 — accessibilityIdentifier vs accessibilityLabel Confusion

**Severity: CRITICAL**
**WCAG:** 4.1.2 Name, Role, Value | **HIG:** Accessibility — Labels

`accessibilityIdentifier` and `accessibilityLabel` are two completely different properties that serve completely different purposes. You're using the wrong one for VoiceOver.

| Property | Purpose | Read by VoiceOver? |
|---|---|---|
| `accessibilityIdentifier` | UI testing automation (XCTest, XCUITest) — a machine-readable string for finding elements in tests | No — never spoken aloud |
| `accessibilityLabel` | The human-readable name VoiceOver announces to the user | Yes — this is what the user hears |

When you set only `accessibilityIdentifier`, VoiceOver has no label to speak. Depending on the button's content, it will either say nothing useful, read the button title if one exists, or announce "Button" with no descriptive context.

---

## The Fix

Set **both** properties independently — they serve different jobs:

```swift
// ❌ Current — identifier is invisible to VoiceOver
button.accessibilityIdentifier = "favoriteButton"

// ✅ Corrected — label for VoiceOver, identifier for UI tests
button.accessibilityLabel = "Add to favorites"      // VoiceOver reads this
button.accessibilityIdentifier = "favoriteButton"   // XCTest finds this
```

**VoiceOver reads:** "Add to favorites. Button."

The identifier `"favoriteButton"` remains intact so your UI tests keep working. Nothing breaks — you're just adding what was missing.

---

## Label Quality Rules

Now that you're setting `accessibilityLabel`, write it well:

- **Describe the action, not the icon:** "Add to favorites" not "Heart icon"
- **Don't include the element type:** Say "Add to favorites" not "Add to favorites button" — VoiceOver appends "Button" automatically from the `.button` trait
- **Update when state changes:** If the button toggles, change the label to match:

```swift
// Update label when state changes
button.accessibilityLabel = isFavorited ? "Remove from favorites" : "Add to favorites"
```

- **Avoid developer jargon:** Never use internal identifiers as labels. `accessibilityLabel = "btn_favorite_123"` would cause VoiceOver to read "btn underscore favorite underscore one two three"

---

## Optionally Add a Hint

If the action outcome isn't obvious from the label alone, add an `accessibilityHint` with the result (not the action — the action is in the label):

```swift
button.accessibilityLabel = "Add to favorites"
button.accessibilityHint = "Saves this item to your favorites list"
button.accessibilityIdentifier = "favoriteButton"
```

**VoiceOver reads:** "Add to favorites. Button. Saves this item to your favorites list."

Hints are optional but useful when the consequence of the action is not immediately clear.

---

## Complete Corrected Code

```swift
// Full accessible button setup
button.accessibilityLabel = "Add to favorites"
button.accessibilityHint = "Saves this item to your favorites list"  // Optional
button.accessibilityIdentifier = "favoriteButton"  // Keep for UI testing
button.accessibilityTraits = .button  // Already set if using UIButton; verify it's present
```

**VoiceOver announcement:** "Add to favorites. Button. Saves this item to your favorites list."

---

## Summary

Your button was missing `accessibilityLabel` — the only property VoiceOver actually reads aloud. `accessibilityIdentifier` is exclusively a test automation hook; VoiceOver ignores it entirely. Set both independently: `accessibilityLabel` for the user, `accessibilityIdentifier` for your tests.
