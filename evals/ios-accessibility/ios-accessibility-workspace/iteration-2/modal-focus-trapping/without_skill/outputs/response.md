## Trapping VoiceOver Focus Inside a Custom UIKit Modal

### The Problem

When a custom modal view is presented (e.g., added as a subview rather than using `UIViewController` presentation), VoiceOver can still swipe to elements in the view hierarchy behind the modal. This is a serious accessibility issue — it's like having a visual modal that doesn't dim the background.

---

### Fix 1: `accessibilityViewIsModal = true` (Recommended)

Set `accessibilityViewIsModal` to `true` on the modal's root view. This tells UIKit to **hide all sibling views** from the accessibility tree while the modal is visible.

```swift
class CustomModalView: UIView {
    override init(frame: CGRect) {
        super.init(frame: frame)
        accessibilityViewIsModal = true
    }
}
```

Or set it when presenting:

```swift
func showModal() {
    modalView.accessibilityViewIsModal = true
    view.addSubview(modalView)

    // Move VoiceOver focus into the modal
    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}
```

**How it works:** UIKit walks the view hierarchy and ignores any element that is not a descendant of a view with `accessibilityViewIsModal = true`. Only the modal's subtree is reachable.

---

### Fix 2: Move Focus on Presentation and Dismissal

After presenting the modal, post `.screenChanged` to move VoiceOver focus to the first element inside it:

```swift
// On present
UIAccessibility.post(notification: .screenChanged, argument: modalTitleLabel)

// On dismiss
modalView.accessibilityViewIsModal = false
modalView.removeFromSuperview()
UIAccessibility.post(notification: .screenChanged, argument: triggerButton)
```

Returning focus to the element that triggered the modal (e.g., the button that opened it) is the correct UX pattern.

---

### Fix 3: Ensure the Modal is a Full Screen Presented View Controller

The cleanest architectural fix is to present the modal using a standard `UIViewController` presentation style (`.overFullScreen`, `.formSheet`, etc.). UIKit automatically handles focus trapping for presented view controllers.

```swift
let modalVC = MyModalViewController()
modalVC.modalPresentationStyle = .overFullScreen
present(modalVC, animated: true)
```

With a proper presentation, you don't need `accessibilityViewIsModal` at all.

---

### Common Mistakes

| Mistake | Result |
|---------|--------|
| Not setting `accessibilityViewIsModal` | VoiceOver reads through the dimmed background |
| Not posting `.screenChanged` | VoiceOver focus stays on the element behind the modal |
| Not restoring focus on dismiss | Focus is lost or lands in an unpredictable location |
| Setting `isHidden = true` on background views | Background views hidden from sighted users but may still be in a11y tree |

---

### SwiftUI

In SwiftUI, `.sheet`, `.fullScreenCover`, and `Alert` automatically trap VoiceOver focus. For custom overlays:

```swift
ZStack {
    ContentView()
        .accessibilityHidden(isModalVisible)  // hide background

    if isModalVisible {
        CustomModalView()
    }
}
```

`.accessibilityHidden(true)` removes the background from the accessibility tree when the modal is showing.
