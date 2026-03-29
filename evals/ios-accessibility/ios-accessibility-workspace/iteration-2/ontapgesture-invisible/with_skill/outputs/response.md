# onTapGesture Is Invisible to Assistive Technology

## The Problem

```swift
// ❌ CRITICAL — invisible to VoiceOver, Switch Control, and eye tracking
Image(systemName: "plus")
    .onTapGesture { addItem() }
```

This code produces a tappable element that is completely invisible to every assistive technology:

- **VoiceOver** — skips the element entirely during linear swipe navigation
- **Switch Control** — cannot scan to or activate the element
- **Eye tracking** (visionOS) — element is not targetable
- **Voice Control** — has no label to say "Tap [name]"
- **Full Keyboard Access** — element is not keyboard-focusable

`onTapGesture` adds a gesture recognizer to the view, but does **not** add the `.isButton` accessibility trait. Without that trait, assistive technologies have no reason to expose the element to users.

## The Fix

Replace `onTapGesture` with `Button`. `Button` automatically adds the `.isButton` accessibility trait, making it visible to all assistive technologies. Add `accessibilityLabel` because `Image(systemName:)` will otherwise read the raw SF Symbol name ("plus").

```swift
// ✅ Correct — visible to all assistive technology
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

## Why accessibilityLabel Is Required Here

Without the label, VoiceOver reads the raw SF Symbol name: "plus". That is not meaningful to users. The label should describe the **action** the button performs.

```swift
// ❌ VoiceOver reads: "plus. Button."
Button(action: addItem) {
    Image(systemName: "plus")
}

// ✅ VoiceOver reads: "Add item. Button."
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add item")
```

Do not include the word "button" in the label — VoiceOver automatically appends the role from the trait.

## Full Example with Context

```swift
struct ItemListToolbar: View {
    var onAdd: () -> Void

    var body: some View {
        HStack {
            Spacer()
            Button(action: onAdd) {
                Image(systemName: "plus")
                    .font(.title2)
            }
            .accessibilityLabel("Add item")
        }
        .padding()
    }
}
```

VoiceOver announcement: "Add item. Button. Double-tap to activate."

## Voice Control Bonus

Because `Button` has an `accessibilityLabel`, Voice Control users can say "Tap Add item" to activate it. With `onTapGesture`, there is no label and no activatable element — Voice Control cannot target it at all.

## Severity

This is a **CRITICAL** (🔴) accessibility issue. The element is entirely absent from assistive technology — it is as if it does not exist for users who rely on VoiceOver, Switch Control, or eye tracking.
