# WCAG 2.2 Criteria: Automatic vs. Manual Implementation on iOS

## Overview

iOS provides substantial built-in accessibility support through UIKit and SwiftUI, but many WCAG 2.2 criteria still require explicit developer attention. This document maps each relevant criterion to its implementation status and highlights the top 5 most commonly missed by developers.

---

## Automatically Handled by Standard UIKit/SwiftUI Controls

These criteria are satisfied by default when using standard system components correctly:

### 1.1.1 Non-text Content (Level A)
- **UIKit**: Standard controls (UIButton, UILabel, UIImageView, UISlider, etc.) expose their role and default label to VoiceOver automatically.
- **SwiftUI**: Text, Button, Toggle, Slider, Image with a label parameter all get default accessibility descriptions.
- **Caveat**: Images require a non-empty `accessibilityLabel` or `Image("name", label: Text(...))` — decorative images must explicitly set `accessibilityHidden(true)`.

### 1.3.1 Info and Relationships (Level A)
- UIKit table views and collection views convey list structure to VoiceOver automatically.
- SwiftUI `List`, `Form`, `Section` structures map to accessibility groupings.
- `UIAccessibilityTraitHeader` is applied to navigation bar titles automatically.

### 1.3.3 Sensory Characteristics (Level A) — Partial
- System controls do not rely solely on shape or color; they include labels. Partial: custom UI can violate this easily.

### 1.4.4 Resize Text (Level AA)
- UIKit: Controls using `UIFont.preferredFont(forTextStyle:)` respond to Dynamic Type automatically.
- SwiftUI: `Font.body`, `.title`, etc., scale with system text size settings by default.

### 2.1.1 Keyboard (Level A) — via Switch Access / Full Keyboard Access
- Standard interactive controls (UIButton, UITextField, UISwitch, etc.) are automatically focusable and operable via Switch Access and Full Keyboard Access on iOS 15+.

### 2.4.6 Headings and Labels (Level AA)
- UINavigationBar titles are exposed as headings automatically.
- SwiftUI `navigationTitle` is treated as a heading by VoiceOver.

### 3.2.1 On Focus (Level A)
- Standard UIKit/SwiftUI controls do not trigger unexpected context changes on focus. VoiceOver focus movement does not navigate away or submit forms.

### 3.3.1 Error Identification (Level A) — Partial
- UITextField validation states do not automatically report errors to VoiceOver. Requires manual announcement.

### 4.1.2 Name, Role, Value (Level A)
- All standard UIKit interactive controls expose their accessibility name (label), role (trait), and state (value) to the Accessibility API automatically.
- UISwitch exposes on/off state; UISlider exposes current value; UIButton exposes enabled/disabled state.

---

## Criteria Requiring Manual Implementation

These are NOT automatically handled and require explicit developer code:

### 1.1.1 Non-text Content — Custom Images and Icons
Custom `SF Symbol` usage without labels, `UIImageView` without `accessibilityLabel`, and decorative images that are not hidden from accessibility all require manual attention.

### 1.3.4 Orientation (Level AA)
The system does not lock orientation. Apps that forcibly lock orientation must provide an accessibility override or ensure all content is accessible regardless. If your app enforces portrait lock via `supportedInterfaceOrientations`, this violates 1.3.4 unless the content type genuinely requires a fixed orientation.

### 1.3.5 Identify Input Purpose (Level AA)
Setting `UITextContentType` (e.g., `.emailAddress`, `.name`, `.telephoneNumber`) on `UITextField` and `UITextView` enables autofill and communicates input purpose. This is NOT set by default — developers must explicitly assign `textContentType`.

### 1.4.1 Use of Color (Level A)
No automatic check exists. Custom views that use color as the only means of conveying information (e.g., red = error, green = success) violate this criterion. Developers must add icons, labels, or patterns.

### 1.4.3 / 1.4.11 Contrast Ratios (Level AA)
iOS does not enforce contrast ratios. All custom colors must be manually verified. Text needs 4.5:1 (or 3:1 for large text); UI components need 3:1. Xcode's Accessibility Inspector helps but is not automatic.

### 1.4.10 Reflow (Level AA)
Content must remain usable at up to 1280 CSS px width equivalent without horizontal scrolling. On iOS this maps to supporting the largest Dynamic Type sizes without truncation or overflow. Custom layouts using fixed sizes or `UILabel.numberOfLines = 1` silently fail here.

### 1.4.12 Text Spacing (Level AA)
iOS does not automatically reformat text when users apply custom text spacing via accessibility settings. Custom text rendering using `CoreText` or fixed-size containers frequently breaks.

### 2.1.1 Keyboard — Custom Gesture Actions
Custom swipe gestures, pan gestures, and multi-finger interactions are not automatically exposed to Switch Access or Full Keyboard Access. Developers must implement `UIAccessibilityCustomAction` alternatives.

### 2.4.3 Focus Order (Level A)
VoiceOver focus order defaults to visual top-left to bottom-right. Complex custom layouts (z-order layers, overlapping views, custom containers) must manually declare `accessibilityElements` order or use `shouldGroupAccessibilityChildren`.

### 2.4.7 Focus Visible (Level AA)
Full Keyboard Access provides a system focus ring, but custom focusable views that override default behavior may suppress the visible focus indicator. Manual implementation of `UIFocusEnvironment` methods may be needed.

### 2.5.3 Label in Name (Level A)
If a button has a visible text label "Submit" but its `accessibilityLabel` is set to something unrelated, voice control users saying "tap Submit" will fail. The `accessibilityLabel` must contain the visible text.

### 2.5.8 Target Size (Level AA) — NEW in WCAG 2.2
Minimum touch target of 24x24 CSS px (approximately 24pt on iOS). UIKit does not enforce this. Small icon buttons, close buttons, and compact navigation items frequently violate this. Must use `accessibilityActivationPoint` or increase the actual frame.

### 3.1.1 Language of Page (Level A)
iOS does not read from the `CFBundleDevelopmentRegion` for VoiceOver language. If your app displays multilingual content, you must set `UIAccessibilityElement.accessibilityLanguage` for text in languages other than the app's primary language.

### 3.3.3 Error Suggestion (Level AA)
Inline form validation errors are not announced automatically. Must use `UIAccessibility.post(notification: .announcement, argument:)` or update the `accessibilityLabel` of the error element and shift VoiceOver focus to it.

### 3.3.7 Redundant Entry (Level A) — NEW in WCAG 2.2
The system does not automatically populate fields from earlier steps. Multi-step forms must not ask users to re-enter information already provided. Requires app-level state management.

### 3.3.8 Accessible Authentication (Level AA) — NEW in WCAG 2.2
Authentication steps that require cognitive tests (e.g., CAPTCHAs without alternatives, puzzles) must offer an accessible alternative. Face ID / Touch ID satisfy this, but fallback flows must not add inaccessible cognitive challenges.

---

## Top 5 WCAG 2.2 Criteria Developers Miss Most

These represent the highest-frequency gaps found in real-world iOS app accessibility audits:

---

### #1 — 1.4.3 / 1.4.11: Contrast Ratios (Level AA)

**Why developers miss it**: Custom brand colors, dark mode variants, and tinted overlays are rarely checked against WCAG contrast requirements. The simulator looks fine visually to sighted developers. Text on gradient backgrounds, disabled-state text, and placeholder text are especially problematic.

**Impact**: Affects users with low vision, color deficiency, and those in bright sunlight.

**Fix**: Use Xcode Accessibility Inspector's contrast checker, or tools like Stark and Colour Contrast Analyser. Set semantic colors using `UIColor(dynamicProvider:)` or SwiftUI `Color` assets to handle light/dark automatically, and verify both modes.

```swift
// Good: semantic color that adapts and meets contrast
label.textColor = UIColor { traitCollection in
    traitCollection.userInterfaceStyle == .dark
        ? UIColor(red: 0.95, green: 0.95, blue: 0.95, alpha: 1)
        : UIColor(red: 0.1, green: 0.1, blue: 0.1, alpha: 1)
}
```

---

### #2 — 2.5.8: Target Size Minimum (Level AA) — NEW in WCAG 2.2

**Why developers miss it**: This criterion is new to WCAG 2.2 (2023) and not yet widely known among iOS developers. Icon-only toolbar buttons, close buttons in sheets, and segmented control segments routinely render at 20pt or smaller. UIKit does not enforce minimum touch target sizes.

**Impact**: Affects users with motor impairments, tremors, or those using the app one-handed.

**Fix**:

```swift
// Option 1: Expand tap area using UIButton.contentEdgeInsets (UIKit)
button.contentEdgeInsets = UIEdgeInsets(top: 12, left: 12, bottom: 12, right: 12)

// Option 2: Use accessibilityFrame to expand the hit area
button.accessibilityFrame = button.frame.insetBy(dx: -10, dy: -10)

// SwiftUI: Use .contentShape to expand tappable area
Button(action: dismiss) {
    Image(systemName: "xmark")
        .frame(width: 24, height: 24)
}
.contentShape(Rectangle().size(CGSize(width: 44, height: 44)))
```

---

### #3 — 1.3.5: Identify Input Purpose (Level AA)

**Why developers miss it**: Developers create text fields without setting `textContentType`, since forms appear to work normally for sighted users. This blocks autofill, password managers, and assistive technology that uses input purpose to offer contextual help.

**Impact**: Affects users with cognitive disabilities who rely on autofill, VoiceOver users who benefit from contextual announcements, and users relying on password managers.

**Fix**:

```swift
// UIKit
emailField.textContentType = .emailAddress
emailField.keyboardType = .emailAddress

passwordField.textContentType = .password
passwordField.isSecureTextEntry = true

newPasswordField.textContentType = .newPassword

// SwiftUI
TextField("Email", text: $email)
    .textContentType(.emailAddress)
    .keyboardType(.emailAddress)
```

---

### #4 — 2.4.3: Focus Order (Level A)

**Why developers miss it**: Default VoiceOver traversal works well for simple single-column layouts but breaks silently in complex custom views, modals, overlapping layers, and animated transitions. Developers rarely test focus order with VoiceOver enabled during development.

**Impact**: Affects all VoiceOver users. An illogical reading order makes the app nearly unusable for blind users — elements are announced out of context or skip critical interactive controls entirely.

**Fix**:

```swift
// UIKit: Explicitly define focus order
containerView.accessibilityElements = [titleLabel, subtitleLabel, actionButton, cancelButton]

// UIKit: Group related elements
headerView.shouldGroupAccessibilityChildren = true

// SwiftUI: Use accessibilitySortPriority
Text("Title").accessibilitySortPriority(2)
Text("Subtitle").accessibilitySortPriority(1)
Button("Action") { }.accessibilitySortPriority(0)
```

When presenting modals, ensure VoiceOver focus moves into the modal:

```swift
UIAccessibility.post(notification: .screenChanged, argument: modalViewController.view)
```

---

### #5 — 2.5.3: Label in Name (Level A)

**Why developers miss it**: Developers set `accessibilityLabel` to improve VoiceOver announcements but inadvertently disconnect the visible label from the accessibility name. This breaks Voice Control (formerly Voice Access) — users who say the visible button text to activate it get no response.

**Impact**: Affects Voice Control users and anyone using speech-based navigation. Also causes confusion for VoiceOver users when the spoken name doesn't match what they see.

**Fix**: The `accessibilityLabel` must contain the visible text, either as-is or as a substring. Adding context is fine; replacing the visible text is not.

```swift
// WRONG: Completely replaces visible text "Buy Now"
button.accessibilityLabel = "Purchase subscription for $9.99 per month"

// CORRECT: Contains the visible text as a substring
button.accessibilityLabel = "Buy Now — $9.99 per month subscription"

// SwiftUI equivalent
Button("Buy Now") { }
    .accessibilityLabel("Buy Now — $9.99 per month subscription")
```

---

## Summary Table

| WCAG 2.2 Criterion | Level | Auto (UIKit/SwiftUI) | Manual Required |
|----|----|----|-----|
| 1.1.1 Non-text Content | A | Partial (standard controls) | Custom images, icons, decorative hiding |
| 1.3.1 Info and Relationships | A | Yes (standard containers) | Custom layouts |
| 1.3.4 Orientation | AA | No | Must not lock orientation arbitrarily |
| 1.3.5 Identify Input Purpose | AA | No | Must set `textContentType` |
| 1.4.1 Use of Color | A | No | Must add non-color indicators |
| 1.4.3 Contrast | AA | No | Must verify all custom colors |
| 1.4.10 Reflow | AA | Partial (Dynamic Type) | Must support largest text sizes |
| 1.4.11 Non-text Contrast | AA | No | Must verify UI component colors |
| 1.4.12 Text Spacing | AA | No | Custom text rendering must adapt |
| 2.1.1 Keyboard | A | Partial (standard controls) | Custom gestures need alternatives |
| 2.4.3 Focus Order | A | Partial (simple layouts) | Complex layouts need explicit order |
| 2.4.6 Headings and Labels | AA | Partial (nav titles) | Custom section headers need traits |
| 2.4.7 Focus Visible | AA | Partial (system ring) | Custom focusable views |
| 2.5.3 Label in Name | A | No | accessibilityLabel must include visible text |
| 2.5.8 Target Size | AA | No | All interactive elements >= 24pt |
| 3.1.1 Language of Page | A | No | Multi-language content needs lang attribute |
| 3.2.1 On Focus | A | Yes | N/A for standard controls |
| 3.3.1 Error Identification | A | No | Must announce validation errors |
| 3.3.3 Error Suggestion | AA | No | Must provide and announce suggestions |
| 3.3.7 Redundant Entry | A | No | App state management required |
| 3.3.8 Accessible Authentication | AA | Partial (Face/Touch ID) | Fallback flows must be accessible |
| 4.1.2 Name, Role, Value | A | Yes (standard controls) | Custom controls need full implementation |

---

## Testing Recommendations

1. **Enable VoiceOver** and navigate your entire app by swipe only — verify reading order, labels, and announcements at each screen.
2. **Enable Full Keyboard Access** (Settings > Accessibility > Keyboards > Full Keyboard Access) and tab through all interactive elements.
3. **Set Dynamic Type to "Accessibility XL"** and verify no text is clipped or truncated.
4. **Run Xcode Accessibility Inspector** for automated contrast and label checks.
5. **Use Voice Control** and attempt to tap every visible button by speaking its label.
6. **Enable Reduce Motion and Increase Contrast** to test adaptive behaviors.
