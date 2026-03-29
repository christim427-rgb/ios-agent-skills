# WCAG 2.2 Criteria: Auto-Handled vs Manual, Top 5 Developer Misses

## Auto-Handled by iOS / SwiftUI / UIKit

These criteria are largely satisfied when using standard platform controls correctly:

| Criterion | What's automatic |
|---|---|
| **1.3.1 Info and Relationships** | `UILabel`, `UIButton`, `Toggle`, `TextField` expose their roles automatically |
| **1.3.3 Sensory Characteristics** | Platform conventions (tap targets, gestures) are standard |
| **1.4.3 Contrast (Minimum, AA)** | System semantic colors (`.label`, `.systemBackground`) maintain contrast in light/dark mode |
| **1.4.11 Non-text Contrast** | System controls meet contrast requirements |
| **2.4.3 Focus Order** | VoiceOver traversal follows view hierarchy order by default |
| **2.4.7 Focus Visible** | Full Keyboard Access shows focus rings on standard controls |
| **3.2.1 On Focus** | System controls don't trigger context changes on focus alone |
| **4.1.2 Name, Role, Value** | Standard controls expose name, role, state via UIAccessibility automatically |
| **4.1.3 Status Messages** | `UIAccessibility.post(notification: .announcement)` is consistent — but you still need to post |

## Requires Manual Implementation

| Criterion | Why it's manual |
|---|---|
| **1.1.1 Non-text Content** | Developers must set `accessibilityLabel` on images, icons, decorative images must be hidden |
| **1.3.4 Orientation** | App may lock orientation — must unlock or provide equivalent in both orientations |
| **1.4.4 Resize Text** | Must use Dynamic Type; fixed font sizes fail this |
| **1.4.10 Reflow** | Layout must adapt at large text sizes without horizontal scrolling |
| **2.1.1 Keyboard** | Custom gestures (drag, swipe, long-press) need keyboard/switch alternatives |
| **2.4.6 Headings and Labels** | Descriptive labels must be written by developers; `accessibilityAddTraits(.isHeader)` must be added manually |
| **2.5.1 Pointer Gestures** | Drag-and-drop, multi-touch gestures need single-pointer alternatives |
| **3.3.1 Error Identification** | Validation errors must be announced to VoiceOver via `.announcement` notifications |
| **3.3.2 Labels or Instructions** | Form fields need clear, visible labels — not just placeholders |

## Top 5 Criteria Developers Miss Most

### 1. 1.1.1 Non-text Content
Decorative images not hidden from VoiceOver, or meaningful icons with no `accessibilityLabel`. A bare `Image(systemName: "arrow.right")` with no label is a common offender.

### 2. 1.4.4 Resize Text
Hardcoded font sizes (`Font.system(size: 14)`) that don't respond to Dynamic Type. Layouts that clip or overlap at large text sizes.

### 3. 2.1.1 Keyboard / 2.5.1 Pointer Gestures
Custom drag-to-reorder, swipe-to-reveal, or long-press menus with no accessible alternative. VoiceOver and Switch Control users can't access these features.

### 4. 4.1.3 Status Messages (WCAG 2.1)
After form submission, loading completion, or error states: the UI updates visually but VoiceOver is not informed. Developers forget to post `UIAccessibility.post(notification: .announcement, argument: "Form submitted successfully")`.

### 5. 2.4.6 Headings and Labels
Section headers in custom views have no `.isHeader` trait. VoiceOver users cannot navigate by headings. In SwiftUI: `.accessibilityAddTraits(.isHeader)` is omitted from section titles.

## Quick Reference

```swift
// 1.1.1 — label meaningful images
Image("chart").accessibilityLabel("Monthly sales chart")
Image(decorative: "background") // hides decorative images

// 1.4.4 — use Dynamic Type
Text("Hello").font(.body) // scales with system setting

// 2.4.6 — mark headings
Text("Section Title").accessibilityAddTraits(.isHeader)

// 4.1.3 — announce status changes
UIAccessibility.post(notification: .announcement, argument: "Item deleted")

// 2.1.1 — add alternative actions
.accessibilityAction(named: "Move up") { moveUp() }
```
