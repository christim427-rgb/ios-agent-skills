# Fixing VoiceOver Focus Leaking Behind a Custom Modal

## The Problem

When you present a custom modal by adding a subview manually (not using `UIViewController` presentation or `.sheet`), VoiceOver has no way to know that the rest of the screen should be blocked from interaction. Posting `.screenChanged` moves initial focus but does nothing to prevent VoiceOver from swiping to elements behind the modal.

## The Fix: `accessibilityViewIsModal`

The primary solution is to set `accessibilityViewIsModal = true` on your modal view. This tells VoiceOver to ignore sibling views in the same container.

```swift
func showModal() {
    let modalView = CustomModalView()
    modalView.accessibilityViewIsModal = true
    view.addSubview(modalView)
    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}
```

When `accessibilityViewIsModal` is `true`, VoiceOver will only expose the elements inside that view and ignore everything else at the same level in the view hierarchy.

## Important Caveat: View Hierarchy Matters

`accessibilityViewIsModal` only hides **sibling** views (and their descendants). If your modal view is not a direct child of the same parent as the content you want hidden, it will not work as expected.

For example, if your hierarchy looks like this:

```
view (root)
 +-- contentContainer
 |    +-- label, buttons, etc.
 +-- modalView (accessibilityViewIsModal = true)
```

This works because `modalView` and `contentContainer` are siblings under `view`.

But if your modal is nested deeper, you may need to restructure or apply additional techniques.

## Additional Hardening Techniques

### 1. Make background content inaccessible

For extra safety, you can explicitly disable accessibility on the background content while the modal is showing:

```swift
func showModal() {
    let modalView = CustomModalView()
    modalView.accessibilityViewIsModal = true

    // Disable accessibility on background content
    backgroundContentView.accessibilityElementsHidden = true

    view.addSubview(modalView)
    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}

func dismissModal() {
    modalView.removeFromSuperview()
    backgroundContentView.accessibilityElementsHidden = false
    UIAccessibility.post(notification: .screenChanged, argument: view)
}
```

### 2. Use a container view that fills the screen

Ensure the modal view (or a wrapper around it) has a frame that covers the full screen. VoiceOver uses the view's frame to determine modal boundaries. A small modal frame can cause focus to escape:

```swift
let overlay = UIView(frame: view.bounds)
overlay.accessibilityViewIsModal = true

let modalContent = CustomModalView()
overlay.addSubview(modalContent)
// Center modalContent within overlay as needed

view.addSubview(overlay)
UIAccessibility.post(notification: .screenChanged, argument: modalContent)
```

### 3. Post the correct notification on dismissal

When dismissing, always notify VoiceOver so it re-evaluates the accessibility tree:

```swift
func dismissModal() {
    modalView.removeFromSuperview()
    UIAccessibility.post(notification: .screenChanged, argument: view)
}
```

## SwiftUI Equivalent

If you are building a similar custom overlay in SwiftUI, you can use the `.accessibilityAddTraits(.isModal)` modifier:

```swift
ZStack {
    ContentView()
    if showModal {
        CustomModalOverlay()
            .accessibilityAddTraits(.isModal)
    }
}
```

## Summary

| Technique | Purpose |
|---|---|
| `accessibilityViewIsModal = true` | Tells VoiceOver to ignore sibling views |
| `accessibilityElementsHidden = true` | Explicitly hides background content from VoiceOver |
| Full-screen overlay wrapper | Prevents focus escaping around the modal edges |
| `.screenChanged` notification | Moves VoiceOver focus to the modal on present/dismiss |

The most reliable approach is to combine `accessibilityViewIsModal` with `accessibilityElementsHidden` on the background content and always post `.screenChanged` on both presentation and dismissal.
