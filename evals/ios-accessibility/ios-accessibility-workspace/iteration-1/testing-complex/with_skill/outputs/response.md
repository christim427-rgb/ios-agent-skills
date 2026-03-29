# Comprehensive VoiceOver Manual Testing Protocol

This protocol covers what to check and in what order when performing manual VoiceOver testing on iOS. Automated tools (Xcode Accessibility Inspector, XCTest `performAccessibilityAudit`) catch roughly 30% of accessibility issues. The remaining 70% requires structured manual testing with VoiceOver enabled on a real device or simulator.

---

## Before You Begin: Setup

**Enable VoiceOver:**
- Fastest: Triple-click the side button (requires Accessibility Shortcut configured in Settings > Accessibility > Accessibility Shortcut)
- Manual: Settings > Accessibility > VoiceOver > On
- Simulator: Hardware menu > Toggle Accessibility Inspector, or use Xcode Accessibility Inspector with Auto-Navigate

**Pre-test automated sweep (do this first — block critical issues before manual testing):**
1. Open Xcode > Open Developer Tool > Accessibility Inspector
2. Select target (Simulator or device)
3. Click "Audit" tab > Run Audit — fix any findings before proceeding to manual testing
4. Run `performAccessibilityAudit()` in XCTest if available (Xcode 15+):
   ```swift
   try app.performAccessibilityAudit(for: .all)
   ```

---

## Phase 1: Linear Navigation (Start Here)

**What:** Swipe right with one finger through the entire screen from top to bottom.

**What to check:**
- Every interactive element is reachable (nothing is skipped or unreachable)
- The navigation order matches the visual reading order — left to right, top to bottom
- No element is announced twice or never announced
- The number of focus stops feels correct — too many stops means over-exposure; too few means elements are hidden

**Common failures found here:**
- Elements using `onTapGesture` instead of `Button` are completely skipped by VoiceOver
- Custom views without accessibility modifiers are invisible
- Absolute positioning or z-index stacking breaks expected swipe order
- Elements with `.accessibilityHidden(true)` that shouldn't be hidden

**Pass criteria:** VoiceOver traverses all content and controls in a logical order with no gaps or repetition.

---

## Phase 2: Element Identification — Label, Role, State

**What:** Focus each interactive element individually. Listen to the full announcement.

**What VoiceOver announces (in order):** Label → Value (if any) → Role/Trait → Hint (if any)

**Check each element type against this table:**

| Element Type | Expected Announcement |
|---|---|
| Button (text) | "[Action label]. Button." |
| Button (icon-only) | "[Explicit accessibilityLabel]. Button." |
| Link | "[Destination label]. Link." |
| Toggle (On) | "[Label]. On. Switch." |
| Toggle (Off) | "[Label]. Off. Switch." |
| Text field (empty) | "[Placeholder or label]. Text field." |
| Text field (filled) | "[Label]. [Current value]. Text field." |
| Slider | "[Label]. [Current value]. Adjustable." |
| Checkbox / custom toggle | "[Label]. [Checked/Unchecked]. Button." or similar |
| Image (informative) | "[Meaningful description of content]." |
| Image (decorative) | Complete silence — nothing announced |
| Section heading | "[Heading text]. Heading." |
| List cell | "[Combined label]. [Hint if applicable]." |
| Tab bar item | "[Label]. Tab. [X] of [Y]." |
| Alert | Title + message announced automatically when presented |
| Modal sheet | Focus moves into modal; background is silent |

**Red flags — fix immediately:**
- "Image" announced with no label (missing `accessibilityLabel` on informative image)
- Raw filename announced: "icon_heart_outline_24" (image using filename as label)
- "[SF Symbol name]" announced: "heart.fill. Button." (missing `accessibilityLabel` on image button)
- "Submit button. Button." — redundant type in label (remove "button" from `accessibilityLabel`)
- "Dimmed" on a control that should not exist at all (rather than being disabled)
- Decorative images speaking their content (add `Image(decorative:)` or `.accessibilityHidden(true)`)

---

## Phase 3: Heading Navigation via Rotor

**What:** Open VoiceOver Rotor (two-finger twist gesture) > select "Headings." Then swipe down to jump between headings.

**What to check:**
- Every major section has at least one heading
- Heading hierarchy is logical (H1 → H2, not jumping from H1 to H3)
- Screen title / navigation bar title is reachable as a heading
- No visual heading elements are missing the `.isHeader` trait

**SwiftUI implementation to verify is present:**
```swift
Text("Section Title")
    .accessibilityAddTraits(.isHeader)
```

**Pass criteria:** A user can navigate the entire screen structure using only heading jumps. No section is unreachable via heading navigation.

---

## Phase 4: Custom Actions on List Cells

**What:** Navigate to a list cell that has secondary actions (delete, favorite, share, etc.). With VoiceOver focused on the cell, swipe up or down to cycle through available actions.

**What to check:**
- All secondary actions on a cell are reachable via swipe up/down without leaving the cell
- Action names are descriptive verbs: "Delete", "Add to favorites", "Share" — not "Action 1"
- The default tap action (opening the item) still works via double-tap
- Actions that would be destructive are clearly labeled as such

**Why this matters:** Without custom actions, VoiceOver users must focus individual "Delete" buttons scattered through the cell, which breaks reading flow and reveals implementation details. Custom actions group them cleanly.

**Pass criteria:** Every secondary action on a list cell is accessible via the rotor or swipe up/down gesture without needing to navigate inside the cell.

---

## Phase 5: Modal Dialogs and Sheets — Focus Trapping

**What:** Trigger every modal in the app (alerts, sheets, full-screen modals, action sheets, popovers). Navigate with VoiceOver while the modal is open.

**What to check:**
- Focus moves INTO the modal immediately when it appears (no double-swipe required)
- Swiping beyond the last element in the modal wraps back to the first element in the modal — focus does NOT leak to background content
- Background content is completely silent while the modal is open
- The modal can be dismissed with the standard escape gesture (two-finger Z gesture)
- After dismissal, focus returns to the element that triggered the modal

**UIKit note to verify:** `accessibilityViewIsModal = true` must be set on the modal view. This only hides sibling views at the same hierarchy level — verify it is placed on the correct view.

**SwiftUI note:** `.sheet`, `.alert`, `.fullScreenCover` handle focus trapping automatically. Custom modal implementations need explicit verification.

**Pass criteria:** VoiceOver is fully contained inside the modal. No background content is audible. Escape gesture dismisses and returns focus correctly.

---

## Phase 6: Dynamic Content — Announcements and State Changes

**What:** Trigger every state change that updates the UI asynchronously: loading states, success/error messages, empty states, badge updates, progress indicators.

**What to check:**
- A loading state announces something (e.g., "Loading" or an activity indicator that reads "In progress")
- When content loads, the new content is reachable without restarting navigation
- Error states announce themselves — the user does not need to stumble upon the error visually
- Success confirmations announce (e.g., "Added to favorites" after a tap)
- Badge counts on tabs or buttons are reflected in the accessibility value
- Progress indicators have meaningful `accessibilityValue` reflecting current progress

**Implementation to verify is present:**
```swift
// UIAccessibility post for announcements
UIAccessibility.post(notification: .announcement, argument: "3 items loaded")

// SwiftUI using accessibilityValue on stateful controls
Slider(value: $volume, in: 0...1)
    .accessibilityValue("\(Int(volume * 100)) percent")
```

**Pass criteria:** A VoiceOver user with the screen off (Screen Curtain on) can understand every state the app enters without needing visual feedback.

---

## Phase 7: Screen Curtain Test — The Gold Standard

**What:** Triple-tap with three fingers to activate Screen Curtain (turns the display completely off while VoiceOver remains active). Attempt to complete each key user flow using only audio.

**Why:** This is the only test that truly replicates the experience of a blind user. Visual shortcuts and workarounds that partially compensate for accessibility gaps become impossible.

**User flows to attempt (cover all primary flows in your app):**
1. Sign in / sign up
2. Core content browsing (list navigation, detail view)
3. The primary action in the app (purchase, post, submit, etc.)
4. Settings changes
5. Error recovery (submit a form with intentional errors)

**What to check:**
- Every step is completable using only audio
- No step requires visual confirmation (e.g., no "look for the red button")
- Error messages identify which field failed and how to fix it
- Confirmations announce clearly ("Order placed", "Message sent")
- You never feel "lost" — there is always a next logical action available

**Pass criteria:** A tester with zero visual reference can complete all primary flows end-to-end without assistance.

---

## Phase 8: Redundancy and Quality Audit

**What:** After completing the functional tests above, do a final sweep listening specifically for announcement quality issues.

**Redundancy checks:**
- No label ends with the element type: "Submit button" → should be "Submit" (VoiceOver appends "button" from the trait)
- No label repeats information already in the value: if the value is "50%", the label should not say "Volume 50%"
- No two adjacent elements announce identical labels (distinguish them with context)

**Completeness checks:**
- Elements with `.disabled(true)` / `.notEnabled` trait announce "dimmed" — they are NOT silent
- Every text field has a persistent label, not just a placeholder (placeholders disappear on input)
- Icon-only toolbar buttons have explicit `accessibilityLabel` values
- Segmented controls identify which segment is selected and the total count

**Hint quality (optional but recommended):**
- Hints are present on non-obvious controls
- Hints start with a verb: "Double-tap to expand", "Swipe up for options"
- Hints add information the label does not already convey

---

## Phase 9: Rotor — Full Capability Check

**What:** Open the Rotor and cycle through all available rotor options on each major screen.

**Rotor options to verify are functional:**
| Rotor Option | What to Check |
|---|---|
| Headings | All section headings reachable (Phase 3 above) |
| Links | Any hyperlinks in content are listed |
| Form fields | All text fields and form controls are listed in order |
| Actions | Custom actions are listed for focused elements |
| Characters / Words | Text editing in text fields works correctly |
| Containers | Logical grouping of content is correct |

**Pass criteria:** Every rotor option that is listed actually works and produces correct results. No rotor option is present with empty results.

---

## Phase 10: Final Sign-Off Checklist

Run this checklist before marking a screen or flow as VoiceOver-complete:

```
NAVIGATION
[ ] All elements reachable via linear swipe in logical order
[ ] No interactive elements silently skipped
[ ] Reading order matches visual layout

LABELS AND ROLES
[ ] Every button has a meaningful label (no raw icon names, no filenames)
[ ] Every label describes purpose, not appearance
[ ] No label includes the element type ("Play" not "Play button")
[ ] Every text field has a persistent label
[ ] Decorative images are completely silent

STRUCTURE
[ ] All section headings navigable via Rotor > Headings
[ ] Related elements are grouped (product cards, address blocks, metadata rows)
[ ] List cells with multiple actions use Custom Actions

STATE
[ ] Toggles announce current state (On/Off)
[ ] Sliders announce current value
[ ] Disabled controls announce "dimmed" (not hidden)
[ ] Loading / error / success states announce themselves

MODALS AND FOCUS
[ ] Focus moves into modals automatically
[ ] Focus is trapped inside modals (background is silent)
[ ] Focus returns to trigger element after dismissal

DYNAMIC CONTENT
[ ] Async content updates post accessibility notifications
[ ] Badge counts reflected in element values

SCREEN CURTAIN
[ ] All primary flows completable with screen off
[ ] No step requires visual confirmation
```

---

## Prioritization: What Blocks Release vs. What Can Wait

### Blocks Release (Critical)
- Any interactive element unreachable by VoiceOver (typically `onTapGesture` instead of `Button`)
- Any button with no label (image-only button reads as raw symbol name)
- Modal focus not trapped (background content audible while modal is open)
- Core user flow not completable under Screen Curtain

### Fix Before Release (High)
- Incorrect element roles or traits
- Missing state announcements (loading, error, success)
- Section headings not marked as headings
- Redundant label + type ("Submit button. Button.")

### Improve in Next Sprint (Medium)
- Missing hints on non-obvious controls
- Custom actions not present on list cells with multiple buttons
- Rotor options incomplete or empty

### Best Practice — Address When Time Allows (Low)
- Hints not starting with a verb
- Missing `accessibilityCustomContent` for secondary information
- Large Content Viewer not configured on toolbar items

---

## Reference: Severity Mapping

| Severity | Definition |
|---|---|
| Critical | Content or controls invisible to assistive technology |
| High | Breaks under accessibility settings (Dynamic Type, Reduce Motion, Dark Mode) |
| Medium | Degraded but not broken experience |
| Low | Best practice gaps with minimal user impact |

Automated tools (Xcode Inspector, XCTest audit) reliably catch: missing labels, contrast failures, Dynamic Type violations, and small touch targets. They do NOT catch: wrong reading order, incorrect element grouping, missing state announcements, broken modal focus trapping, or poor label quality. Manual VoiceOver testing per this protocol is required to surface all of these.
