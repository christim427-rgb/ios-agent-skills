Use `UIAccessibility.post(notification:argument:)` with the `.announcement` notification. This is the correct choice because an announcement delivers informational text to VoiceOver without moving focus -- exactly what you want when an async operation finishes and the user should stay where they are.

## UIKit

```swift
UIAccessibility.post(notification: .announcement, argument: "Download complete")
```

## SwiftUI (iOS 17+)

```swift
AccessibilityNotification.Announcement("Download complete").post()
```

## Priority announcements (iOS 17+)

If VoiceOver is already speaking when your async operation completes, a normal announcement can be dropped. Use a high-priority announcement to prevent interruption:

```swift
var announcement = AttributedString("Upload failed")
announcement.accessibilitySpeechAnnouncementPriority = .high
AccessibilityNotification.Announcement(announcement).post()
```

## Why `.announcement` and not the other notifications

There are three post notifications, and each serves a different purpose:

| Notification | Focus change | Use case |
|---|---|---|
| `.screenChanged` | Moves focus to the argument element (or first element) | A completely new screen appeared |
| `.layoutChanged` | Moves focus to the argument element | Part of the screen changed (element added/removed) |
| `.announcement` | **No focus change** | Informational status update |

Since an async completion is a status update and not a navigation event, `.announcement` is the right fit. Using `.screenChanged` or `.layoutChanged` would unexpectedly move the user's VoiceOver cursor away from whatever they are currently focused on.

## Practical tip

Don't over-notify. VoiceOver announcements can be lost if VoiceOver is already speaking. For critical status changes (errors, security alerts), use `.high` priority. For routine confirmations, a normal announcement is fine. SwiftUI also auto-handles many UI changes through state tracking, so you rarely need manual posting for things like showing/hiding views -- reserve `Announcement` for status messages that have no visual counterpart VoiceOver could discover on its own.
