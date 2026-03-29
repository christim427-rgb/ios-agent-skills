# WCAG 2.2 on iOS: Automatic vs. Manual Handling

## Automatically Handled by Standard UIKit/SwiftUI Controls

When developers use standard controls (UIButton, UISlider, UISwitch, Toggle, Button, Picker, etc.) without customization, the following WCAG 2.2 AA criteria are satisfied for free:

| WCAG | Criterion | Why It's Handled Automatically |
|---|---|---|
| **4.1.2** | Name, Role, Value | Standard controls auto-set accessibility traits, labels derived from title/text, and values (e.g., a UISwitch exposes "on"/"off" as its value) |
| **2.5.2** | Pointer Cancellation | UIKit fires actions on `.touchUpInside` — dragging a finger away before release cancels the action, satisfying the "up-event" requirement |
| **2.1.1 / 2.1.2** | Keyboard / No Keyboard Trap | Standard controls participate in VoiceOver, Switch Control, and Full Keyboard Access by default; focus is never trapped |
| **3.1.1** | Language of Page | iOS reads `NSLocale` / `CFBundleDevelopmentRegion` and announces content in the correct language via VoiceOver |
| **3.2.1 / 3.2.2** | On Focus / On Input | Standard controls do not trigger unexpected context changes when focused or when a value changes (a UISwitch flip doesn't navigate away) |
| **1.3.2** | Meaningful Sequence | Default UIKit/SwiftUI layout follows left-to-right, top-to-bottom reading order, which VoiceOver inherits automatically |

**Key caveat:** These guarantees evaporate the moment a developer deviates from standard controls — using `onTapGesture` instead of `Button`, drawing a custom toggle with `Path`, or building a card with a plain `VStack` + tap gesture. At that point, every criterion above must be re-satisfied manually.

---

## Requires Manual Implementation

The majority of WCAG 2.2 AA compliance on iOS is not automatic. The table below lists all criteria requiring explicit developer action, with the iOS API required and the priority level from the skill's severity model.

| WCAG | Criterion | Required iOS API / Action | Priority |
|---|---|---|---|
| **1.1.1** | Non-text Content | `accessibilityLabel` on images; `Image(decorative:)` or `.accessibilityHidden(true)` for decorative images | CRITICAL |
| **1.3.1** | Info & Relationships | `.accessibilityAddTraits(.isHeader)` on headings; `accessibilityElements` array; `.accessibilityElement(children: .combine/.ignore)` for grouping | HIGH |
| **1.3.4** | Orientation | Do not lock orientation via `Info.plist`; support both portrait and landscape | MEDIUM |
| **1.3.5** | Input Purpose | `.textContentType(.emailAddress/.name/.telephoneNumber/etc.)` on text fields to enable autofill | MEDIUM |
| **1.4.1** | Use of Color | Check `accessibilityDifferentiateWithoutColor`; always pair color with shape/icon/text | HIGH |
| **1.4.3** | Contrast (Minimum) | 4.5:1 for normal text, 3:1 for large text; test in both light and dark mode; adapt via `accessibilityContrast == .increased` | HIGH |
| **1.4.4** | Resize Text | `preferredFont(forTextStyle:)` + `adjustsFontForContentSizeCategory = true` (UIKit); `.font(.body/.title/etc.)` (SwiftUI) | HIGH |
| **1.4.10** | Reflow | Dynamic Type at accessibility sizes; `ViewThatFits` / `AnyLayout` to switch HStack→VStack; `ScrollView` for overflow | HIGH |
| **1.4.11** | Non-text Contrast | 3:1 contrast for UI component borders and graphical objects | MEDIUM |
| **1.4.13** | Content on Hover | Popovers and tooltips must be dismissible (Escape / tap outside) and must not auto-dismiss | MEDIUM |
| **2.2.1** | Timing Adjustable | Session timeout dialogs with extend/disable options; use `AccessibilityNotification.Announcement` to warn | MEDIUM |
| **2.2.2** | Pause, Stop, Hide | Check `isReduceMotionEnabled` / `@Environment(\.accessibilityReduceMotion)`; provide pause/stop controls for auto-playing content | HIGH |
| **2.3.1** | Three Flashes | No UI element may flash more than 3 times per second — seizure risk | CRITICAL |
| **2.4.3** | Focus Order | `accessibilityElements` array override (UIKit); `.accessibilitySortPriority()` (SwiftUI) | HIGH |
| **2.4.6** | Headings and Labels | `.accessibilityAddTraits(.isHeader)` on every section heading; enables VoiceOver rotor heading navigation | HIGH |
| **2.5.1** | Pointer Gestures | Single-tap alternatives for any multi-finger or path-based gesture | MEDIUM |
| **2.5.3** | Label in Name | `accessibilityLabel` must contain (or match) the visible button text — critical for Voice Control activation | HIGH |
| **2.5.7** | Dragging Movements (NEW 2.2) | `accessibilityCustomActions` as single-tap alternatives to drag-to-reorder, drag-to-dismiss, etc. | MEDIUM |
| **2.5.8** | Target Size Minimum (NEW 2.2) | Minimum 24×24pt per WCAG; Apple HIG recommends 44×44pt; enforce with `.frame(minWidth: 44, minHeight: 44)` | MEDIUM |
| **3.3.1** | Error Identification | `AccessibilityNotification.Announcement` to announce validation errors; `accessibilityLabel` on error states | HIGH |
| **3.3.8** | Accessible Authentication (NEW 2.2) | `.textContentType(.password)`; never block paste; support biometric auth (Face ID / Touch ID via LocalAuthentication) | MEDIUM |
| **4.1.2** | Name/Role/Value (custom controls) | Full manual implementation: `accessibilityLabel`, `accessibilityTraits`, `accessibilityValue`, `accessibilityActivate()` | CRITICAL |
| **2.4.11** | Focus Not Obscured (NEW 2.2) | Ensure sticky headers/footers scroll focused elements into view; `scrollRectToVisible` / scroll-to-visible on focus | HIGH |
| **2.4.13** | Focus Appearance (NEW 2.2) | Custom focus rings on non-standard controls must meet 3:1 contrast against adjacent colors | HIGH |

---

## Top 5 WCAG 2.2 Criteria Developers Miss Most

These are the five criteria that consistently appear in accessibility audits as unaddressed, ranked by frequency of omission and real-world impact.

---

### Miss #1 — WCAG 1.1.1: Non-text Content (Missing `accessibilityLabel` on icon buttons)

**Why developers miss it:** Xcode does not warn about missing labels at build time. Icon-only buttons using SF Symbols compile and run without error; VoiceOver simply reads the raw symbol name ("square.and.arrow.up" instead of "Share").

**What breaks:** VoiceOver users hear meaningless or confusing announcements. The button is technically reachable but functionally useless.

**The fix:**
```swift
// WRONG — VoiceOver reads "square.and.arrow.up, button"
Button { share() } label: {
    Image(systemName: "square.and.arrow.up")
}

// CORRECT — VoiceOver reads "Share, button"
Button { share() } label: {
    Image(systemName: "square.and.arrow.up")
}
.accessibilityLabel("Share")
```

**Scope of the problem:** This is the #1 AI code-generation failure. Every AI assistant omits `accessibilityLabel` on image-only buttons by default because the vast majority of training-corpus code omits it too.

---

### Miss #2 — WCAG 1.4.4: Resize Text (Hardcoded font sizes)

**Why developers miss it:** `.font(.system(size: 17))` looks fine in Xcode Preview and on the simulator at default text size. The failure is invisible until a user with large text enabled opens the app — at which point text stays tiny while everything else on the OS scales up.

**What breaks:** Approximately 25–30% of iOS users change their text size. Users who depend on larger text cannot read content in apps that hardcode sizes.

**The fix:**
```swift
// WRONG — never scales with user preference
Text("Account Balance")
    .font(.system(size: 17))

// CORRECT — scales automatically
Text("Account Balance")
    .font(.body)

// CORRECT for custom fonts (UIKit)
label.font = UIFontMetrics(forTextStyle: .body)
    .scaledFont(for: UIFont(name: "CustomFont-Regular", size: 17)!)
label.adjustsFontForContentSizeCategory = true
```

---

### Miss #3 — WCAG 1.3.1: Info & Relationships (Missing heading traits)

**Why developers miss it:** Section headers look like headers visually (larger, bolder text) but without the `.isHeader` trait, VoiceOver cannot identify them as headings. The VoiceOver rotor heading navigation — the primary way many blind users scan long screens — finds nothing.

**What breaks:** Users who navigate by headings (the most common VoiceOver navigation pattern after swiping) cannot jump between sections. A settings screen with 8 sections requires 40+ swipes instead of 8 rotor jumps.

**The fix:**
```swift
// WRONG — looks like a heading visually, but VoiceOver can't identify it
Text("Payment Methods")
    .font(.headline)

// CORRECT — announces "Payment Methods, heading" and appears in rotor
Text("Payment Methods")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
```

```swift
// UIKit
headerLabel.accessibilityTraits.insert(.header)  // insert, never assign
```

---

### Miss #4 — WCAG 2.5.3: Label in Name (accessibilityLabel doesn't contain visible text)

**Why developers miss it:** This WCAG 2.2 criterion is relatively new and less well-known. Developers often set a descriptive `accessibilityLabel` that is more verbose than the visible button label — which accidentally breaks Voice Control. Voice Control users say the word they see on screen to activate a control; if the accessibility label doesn't contain that word, activation fails silently.

**What breaks:** Voice Control users say "Continue" to tap a button labelled "Continue" on screen, but the developer set `accessibilityLabel("Proceed to next step")`. The spoken command "Continue" finds no match. The user is stuck.

**The fix:**
```swift
// WRONG — visible text is "Continue" but label is completely different
Button("Continue") { proceed() }
    .accessibilityLabel("Proceed to the next step")

// CORRECT — label starts with the visible text (additional context is fine)
Button("Continue") { proceed() }
    .accessibilityLabel("Continue to payment")

// ALSO CORRECT — if the button text is already descriptive, no custom label needed
Button("Continue") { proceed() }
```

**Rule:** The `accessibilityLabel` must contain the visible text as a substring. It can add context, but cannot replace the visible word with different text.

---

### Miss #5 — WCAG 2.5.8: Target Size Minimum (NEW in WCAG 2.2) — small tap targets

**Why developers miss it:** This is brand new to WCAG 2.2 and was not in 2.1. Many developers are still working from WCAG 2.1 checklists. Additionally, Xcode's Accessibility Inspector doesn't flag target size failures, and the 24×24pt minimum is easy to violate with compact toolbar buttons, close buttons positioned in corners, or icon-only navigation bar items.

**What breaks:** Users with motor impairments, tremors, or who use assistive touch cannot reliably activate small targets. The Apple HIG recommends 44×44pt; WCAG 2.2 mandates 24×24pt minimum with at least 24pt spacing to adjacent targets.

**The fix:**
```swift
// WRONG — 20x20pt icon button is below the 24pt WCAG minimum
Button { dismiss() } label: {
    Image(systemName: "xmark")
        .frame(width: 20, height: 20)
}

// CORRECT — meet Apple HIG 44pt recommendation, which exceeds WCAG 24pt minimum
Button { dismiss() } label: {
    Image(systemName: "xmark")
}
.frame(minWidth: 44, minHeight: 44)
.accessibilityLabel("Close")

// ALSO CORRECT in UIKit — expand the hit area without changing visual size
override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
    bounds.insetBy(dx: -12, dy: -12).contains(point)
}
```

---

## Summary Reference Table

| Criterion | Auto or Manual | Missed? | Key API |
|---|---|---|---|
| 4.1.2 Name/Role/Value (standard) | AUTO | — | Use standard controls |
| 2.5.2 Pointer Cancellation | AUTO | — | Use standard controls |
| 2.1.1/2.1.2 Keyboard | AUTO | — | Use standard controls |
| 3.1.1 Language | AUTO | — | NSLocale / CFBundleDevelopmentRegion |
| 3.2.1/3.2.2 On Focus/Input | AUTO | — | Use standard controls |
| 1.3.2 Meaningful Sequence | AUTO | — | Default layout order |
| **1.1.1 Non-text Content** | **MANUAL** | **TOP MISS #1** | `accessibilityLabel` |
| **1.4.4 Resize Text** | **MANUAL** | **TOP MISS #2** | Dynamic Type text styles |
| **1.3.1 Info & Relationships** | **MANUAL** | **TOP MISS #3** | `.isHeader` trait |
| **2.5.3 Label in Name** | **MANUAL** | **TOP MISS #4** | Label contains visible text |
| **2.5.8 Target Size (2.2)** | **MANUAL** | **TOP MISS #5** | `.frame(minWidth: 44, minHeight: 44)` |
| 1.4.3 Contrast | MANUAL | Common | Semantic colors + contrast check |
| 1.4.10 Reflow | MANUAL | Common | ViewThatFits, ScrollView |
| 2.4.6 Headings and Labels | MANUAL | Common | `.isHeader` on section headings |
| 2.2.2 Pause/Stop/Hide | MANUAL | Common | `reduceMotion` check |
| 2.5.7 Dragging (2.2) | MANUAL | Less common | `accessibilityCustomActions` |
| 2.4.11 Focus Not Obscured (2.2) | MANUAL | Less common | Scroll-to-visible on focus |
| 3.3.8 Accessible Auth (2.2) | MANUAL | Less common | `.password` textContentType, no paste blocking |
