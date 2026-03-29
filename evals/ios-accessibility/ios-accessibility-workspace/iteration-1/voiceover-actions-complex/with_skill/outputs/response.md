# Fixing VoiceOver Focus Leaking Behind a Custom UIKit Modal

## The Problem

Your custom modal is added as a subview, but VoiceOver can still navigate to content behind it. Posting `.screenChanged` moves **initial focus** to the modal, but it does not **trap** focus there. As soon as the user swipes to the next element, VoiceOver escapes to the underlying content.

## Root Cause

VoiceOver focus trapping in UIKit is controlled by the `accessibilityViewIsModal` property. Without it, VoiceOver treats your modal as just another view in the hierarchy and freely navigates to siblings and other content. The `.screenChanged` notification only sets the *starting point* for focus -- it does not restrict where the user can navigate afterward.

There is a critical subtlety: **`accessibilityViewIsModal` only hides the modal view's siblings from VoiceOver, not all other views.** This means your modal's position in the view hierarchy matters enormously. If the modal is deeply nested inside another container, parent-level siblings will not be hidden.

## The Fix

You need three things:

1. **Set `accessibilityViewIsModal = true`** on the modal view.
2. **Ensure the modal is a direct child of the view** (or window) so that its siblings -- which are the views you want hidden -- are at the right level.
3. **Implement `accessibilityPerformEscape`** so the two-finger Z gesture dismisses the modal (expected VoiceOver convention).

```swift
// ❌ Current — focus leaks behind the modal
func showModal() {
    let modalView = CustomModalView()
    view.addSubview(modalView)
    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}
```

```swift
// ✅ Corrected — VoiceOver focus is trapped inside the modal
func showModal() {
    let modalView = CustomModalView()

    // 1. Tell VoiceOver this is a modal — hides sibling views
    modalView.accessibilityViewIsModal = true

    // 2. Add as direct child so siblings (the main content) are hidden
    view.addSubview(modalView)

    // 3. Move VoiceOver focus into the modal
    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}
```

In your `CustomModalView`, implement the escape gesture for dismissal:

```swift
class CustomModalView: UIView {

    // Allow two-finger Z gesture to dismiss (VoiceOver "Escape")
    override func accessibilityPerformEscape() -> Bool {
        dismissModal()
        return true
    }

    private func dismissModal() {
        removeFromSuperview()
        // Post notification so VoiceOver focus returns to the parent
        UIAccessibility.post(notification: .screenChanged, argument: nil)
    }
}
```

## Why This Works

- **`accessibilityViewIsModal = true`**: Tells VoiceOver to hide all **sibling** views of the modal from the accessibility tree. The user can only navigate within the modal and its children.
- **`.screenChanged` notification**: Plays the "beep-boop" screen change sound and moves focus to the modal, signaling to the user that a new context appeared.
- **`accessibilityPerformEscape()`**: Returns `true` to indicate the gesture was handled. VoiceOver users expect the two-finger Z scrub gesture to dismiss modals, alerts, and popovers. Without this, there is no discoverable way to close the modal.

## Common Pitfalls

### Pitfall 1: Modal nested too deep

If your modal is inside a wrapper container, `accessibilityViewIsModal` only hides the wrapper's other children -- not the main content behind the wrapper.

```swift
// ❌ Modal nested inside a container — siblings of containerView are NOT hidden
let containerView = UIView()
view.addSubview(containerView)
containerView.addSubview(dimmingView)
containerView.addSubview(modalView)
modalView.accessibilityViewIsModal = true
// Only dimmingView is hidden, not the rest of the screen
```

```swift
// ✅ Option A: Set modal on the container instead
containerView.accessibilityViewIsModal = true

// ✅ Option B: Add modal as direct child of the main view
view.addSubview(modalView)
modalView.accessibilityViewIsModal = true
```

### Pitfall 2: Forgetting to restore focus on dismiss

When you dismiss the modal, post `.screenChanged` with `nil` (or a specific element to focus) so VoiceOver returns to a sensible location. Without this, focus may land unpredictably.

```swift
func dismissModal() {
    modalView.removeFromSuperview()
    UIAccessibility.post(notification: .screenChanged, argument: self.previouslyFocusedElement)
}
```

### Pitfall 3: Dimming background is still reachable

If you add a semi-transparent dimming view as a separate sibling (not as a child of the modal), make sure it is behind the modal in the view hierarchy. Since `accessibilityViewIsModal` hides siblings, the dimming view will be hidden automatically. But if the dimming view is a **parent** of the modal, it will not be hidden -- restructure so the dimming view is either a sibling or a child of the modal.

## VoiceOver Behavior After Fix

- **On appear**: VoiceOver plays the screen-changed tone and announces the first element inside the modal.
- **Swiping**: Focus stays within the modal's children. Content behind the modal is unreachable.
- **Two-finger Z scrub**: Dismisses the modal and returns focus to the previous screen.

## WCAG Mapping

| Criterion | Requirement |
|---|---|
| 2.4.3 Focus Order | Focus must move to the modal on appear and stay trapped within it |
| 3.2.1 On Focus | Opening a modal must not cause unexpected context changes without user action |
| 1.3.1 Info and Relationships | The modal relationship must be programmatically conveyed (via `accessibilityViewIsModal`) |
