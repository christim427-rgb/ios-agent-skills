## Posting a VoiceOver Announcement When an Async Operation Completes

### The Notification to Use

Post `UIAccessibility.Notification.announcement` (UIKit) or use `AccessibilityNotification.Announcement` (SwiftUI iOS 16+).

---

### UIKit

```swift
func uploadComplete() {
    UIAccessibility.post(
        notification: .announcement,
        argument: "Upload complete. Your file has been saved."
    )
}
```

The `argument` is the string VoiceOver will speak immediately, interrupting any current speech.

#### Controlling Interruption (iOS 11+)

By default, announcements interrupt whatever VoiceOver is currently reading. To queue the announcement instead, pass an `NSAttributedString` with the `UIAccessibilityAnnouncementAttribute`:

```swift
let message = NSAttributedString(
    string: "Download finished",
    attributes: [
        UIAccessibility.AnnouncementAttributeKey.priority: UIAccessibility.AnnouncementPriority.high
    ]
)
UIAccessibility.post(notification: .announcement, argument: message)
```

Priority levels: `.low`, `.default`, `.high`

---

### SwiftUI (iOS 16+)

```swift
import SwiftUI

// Inside a View or async context:
AccessibilityNotification.Announcement("Upload complete").post()
```

Or with priority:

```swift
AccessibilityNotification.Announcement(
    "Upload complete",
    priority: .high
).post()
```

---

### SwiftUI — Older Approach (pre-iOS 16)

```swift
DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
    UIAccessibility.post(notification: .announcement, argument: "Upload complete")
}
```

The small delay is sometimes necessary when the announcement fires at the same time as a UI update; without it the announcement can be swallowed.

---

### Other Useful Notifications

| Notification | When to Use |
|-------------|-------------|
| `.announcement` | Speak a status message (async complete, error, confirmation) |
| `.screenChanged` | Major screen change — moves VoiceOver focus to a new element |
| `.layoutChanged` | Partial UI update — moves focus to a specified element |
| `.pageScrolled` | Inform user of scroll position change |

```swift
// Move focus to a newly appeared error message
UIAccessibility.post(notification: .layoutChanged, argument: errorLabel)
```

---

### Best Practices

- Post announcements **on the main thread**.
- Keep messages concise — one sentence is ideal.
- For error states, pair the announcement with moving focus to the error element (`.layoutChanged`).
- Avoid posting announcements too frequently (e.g., on every progress tick) — batch them or post only on completion/failure.
- Test with VoiceOver active to verify the timing and that the announcement is not dropped.
