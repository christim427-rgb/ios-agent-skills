# accessibilityIdentifier Set but VoiceOver Reads Nothing — Why?

## Root Cause

`accessibilityIdentifier` is **not** an accessibility attribute in the user-facing sense. It is a testing identifier used exclusively by UI testing frameworks (XCTest, Appium, etc.) to locate elements programmatically. VoiceOver does not read it.

```swift
// This does NOTHING for VoiceOver:
myView.accessibilityIdentifier = "submitButton"

// SwiftUI equivalent — also invisible to VoiceOver:
Button("Submit") { submit() }
    .accessibilityIdentifier("submitButton")
```

## What VoiceOver Actually Uses

| Attribute | Purpose | VoiceOver reads it? |
|---|---|---|
| `accessibilityLabel` | Human-readable name of the element | Yes — reads first |
| `accessibilityValue` | Current value (e.g., "On", "50%") | Yes — reads after label |
| `accessibilityHint` | Brief usage instruction | Yes — reads last (optional) |
| `accessibilityTraits` | Element type (button, header, image…) | Yes — informs behavior |
| `accessibilityIdentifier` | Test automation ID | No |

## Fix

Set `accessibilityLabel` instead of (or in addition to) `accessibilityIdentifier`:

```swift
// UIKit
button.accessibilityLabel = "Submit order"
button.accessibilityIdentifier = "submitButton" // keep for tests if needed

// SwiftUI
Button("Submit") { submit() }
    .accessibilityLabel("Submit order")
    .accessibilityIdentifier("submitButton") // keep for tests if needed
```

## When to Use Each

- `accessibilityIdentifier` — use when writing UI tests and you need a stable, non-localized hook to find elements. Survives text changes without breaking tests.
- `accessibilityLabel` — use to describe every interactive or informative element so VoiceOver users can understand and navigate the interface.

These two serve completely different audiences: testers vs. end users.
