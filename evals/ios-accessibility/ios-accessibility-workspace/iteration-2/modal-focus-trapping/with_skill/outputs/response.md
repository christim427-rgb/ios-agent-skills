# Custom Modal VoiceOver Focus Trapping

## The Problem

When a custom modal view appears, VoiceOver continues to read content behind it. Users can swipe past the modal edges and access buttons, text, and interactive elements from the screen underneath — as if the modal isn't there. This is disorienting and potentially dangerous (users may accidentally activate destructive actions behind the modal without realizing it).

---

## Solution: `accessibilityViewIsModal`

Set `accessibilityViewIsModal = true` on the root view of your modal. This instructs VoiceOver to ignore the modal's siblings in the view hierarchy.

### UIKit

```swift
class CustomModalViewController: UIViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Enable modal focus trapping
        view.accessibilityViewIsModal = true
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // Move VoiceOver focus into the modal
        UIAccessibility.post(notification: .screenChanged, argument: view)
    }
}
```

### SwiftUI

For `.sheet`, `.fullScreenCover`, and `NavigationStack` presentations, SwiftUI handles modal focus trapping automatically.

For a **custom overlay** (e.g., a `ZStack`-based modal), use `.accessibilityAddTraits(.isModal)`:

```swift
struct CustomModalView: View {
    @Binding var isPresented: Bool

    var body: some View {
        ZStack {
            // Background overlay — hidden from VoiceOver
            Color.black.opacity(0.4)
                .accessibilityHidden(true)

            // Modal card
            VStack(spacing: 20) {
                Text("Confirm Action")
                    .font(.headline)
                    .accessibilityAddTraits(.isHeader)

                Text("Are you sure you want to delete this item? This cannot be undone.")
                    .font(.body)

                HStack {
                    Button("Cancel") { isPresented = false }
                    Button("Delete") { performDelete(); isPresented = false }
                        .foregroundStyle(.red)
                }
            }
            .padding(24)
            .background(Color(.systemBackground))
            .clipShape(.rect(cornerRadius: 16))
            .padding(32)
            // Mark as modal — VoiceOver ignores siblings
            .accessibilityAddTraits(.isModal)
        }
    }
}
```

---

## CRITICAL WARNING: `accessibilityViewIsModal` Only Hides SIBLINGS

This is the most commonly misunderstood aspect of modal accessibility. `accessibilityViewIsModal = true` (UIKit) hides **only the siblings** of the modal view in the view hierarchy. It does NOT hide all other views on screen.

### What "Siblings" Means

If your modal is placed at:
```
UIWindow
├── RootViewController.view      ← sibling (HIDDEN from VO)
└── ModalView                    ← your modal (accessibilityViewIsModal = true)
```
The root view IS a sibling → it gets hidden. This works correctly.

But if your modal is placed at:
```
UIWindow
└── RootViewController.view
    ├── ContentView              ← NOT a sibling of modal (NOT hidden!)
    └── ContainerView
        └── ModalView            ← modal is deep in the hierarchy
```
The content view is NOT a sibling of the modal → VoiceOver can still reach it.

### Fix: Present Modal at the Window Level

```swift
// UIKit — add modal as a direct child of the window for correct sibling hiding
func presentCustomModal() {
    guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
          let window = windowScene.windows.first else { return }

    let modalView = CustomModalView()
    modalView.accessibilityViewIsModal = true
    window.addSubview(modalView)

    UIAccessibility.post(notification: .screenChanged, argument: modalView)
}
```

---

## Implement `accessibilityPerformEscape`

VoiceOver users expect a two-finger Z-gesture (escape) to dismiss a modal. Implement it so the gesture works even on custom modals:

```swift
// UIKit — in the modal view controller
override func accessibilityPerformEscape() -> Bool {
    dismiss(animated: true)
    return true
}
```

```swift
// SwiftUI — add a button with a keyboard shortcut equivalent
Button("Close") {
    isPresented = false
}
.keyboardShortcut(.escape)
.accessibilityLabel("Close")
.accessibilityHint("Dismisses this dialog")
```

After dismissing, return focus to the element that triggered the modal:

```swift
// UIKit — return focus to the button that triggered the modal
override func viewDidDisappear(_ animated: Bool) {
    super.viewDidDisappear(animated)
    UIAccessibility.post(notification: .screenChanged, argument: triggeringButton)
}
```

---

## Full UIKit Pattern

```swift
class AlertModalViewController: UIViewController {

    weak var triggeringElement: UIView?

    override func viewDidLoad() {
        super.viewDidLoad()
        view.accessibilityViewIsModal = true
        setupEscapeGesture()
    }

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        // Move VoiceOver into the modal
        UIAccessibility.post(notification: .screenChanged, argument: view)
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        // Return focus to what triggered the modal
        UIAccessibility.post(notification: .screenChanged, argument: triggeringElement)
    }

    override func accessibilityPerformEscape() -> Bool {
        dismiss(animated: true)
        return true
    }
}
```

---

## Checklist for Custom Modals

- [x] `accessibilityViewIsModal = true` (UIKit) or `.accessibilityAddTraits(.isModal)` (SwiftUI)
- [x] Modal is a direct sibling of the content it should hide (window-level if needed)
- [x] `.screenChanged` posted on appearance to move VoiceOver focus into the modal
- [x] `.screenChanged` posted on dismissal to return focus to the triggering element
- [x] `accessibilityPerformEscape()` implemented for two-finger Z dismiss
- [x] Overlay/backdrop behind modal is `accessibilityHidden(true)`
- [x] First element inside modal has a clear label (ideally the title or primary action)
