# Posting VoiceOver Announcements for Async Completion

## Three Types of Accessibility Notifications

| Notification | Sound | Focus Change | When to Use |
|---|---|---|---|
| `.announcement` | None | Does NOT move focus | Status updates: "Upload complete", "3 new messages", "Loading finished" |
| `.layoutChanged` | None | Moves to argument element | Part of the screen changed: element added, removed, or replaced |
| `.screenChanged` | "Beep-boop" | Moves to argument or first element | New screen or major context change: view controller push, tab switch |

---

## Posting an Announcement for Async Completion

Use `.announcement` when an async operation finishes and you want to inform VoiceOver without moving focus. The user stays where they are but hears a notification.

### UIKit

```swift
func uploadPhoto(_ photo: UIImage) {
    photoUploadService.upload(photo) { [weak self] result in
        DispatchQueue.main.async {
            switch result {
            case .success:
                UIAccessibility.post(
                    notification: .announcement,
                    argument: "Photo uploaded successfully"
                )
            case .failure(let error):
                UIAccessibility.post(
                    notification: .announcement,
                    argument: "Upload failed: \(error.localizedDescription)"
                )
            }
        }
    }
}
```

### SwiftUI (iOS 17+)

```swift
struct UploadView: View {
    @State private var isUploading = false

    var body: some View {
        Button("Upload Photo") {
            isUploading = true
            Task {
                do {
                    try await photoService.upload(selectedPhoto)
                    // Post announcement on success
                    AccessibilityNotification.Announcement("Photo uploaded successfully").post()
                } catch {
                    AccessibilityNotification.Announcement("Upload failed").post()
                }
                isUploading = false
            }
        }
    }
}
```

### SwiftUI (iOS 15-16) — Use UIKit Bridge

```swift
UIAccessibility.post(notification: .announcement, argument: "Upload complete")
```

---

## Announcement Priority (iOS 17+)

**Critical problem:** Announcements can be **silently dropped** if VoiceOver is already speaking when your notification fires. The new speech is queued and may be discarded if VoiceOver moves on before it runs.

Mitigate this with announcement priority:

```swift
// iOS 17+ — Control announcement priority
var announcement = AttributedString("Download complete")
announcement.accessibilitySpeechAnnouncementPriority = .high
AccessibilityNotification.Announcement(announcement).post()
```

Available priorities:
- `.default` — may be interrupted or dropped if VoiceOver is speaking
- `.high` — interrupts current speech; plays as soon as possible
- `.low` — plays only when VoiceOver is idle

For important async completions (uploads, purchases, critical errors), use `.high` to ensure the user actually hears it.

---

## When to Use `.layoutChanged` vs `.announcement`

### `.layoutChanged` — Element Added or Focused

Use when a new element appears in the current view and you want VoiceOver to focus it:

```swift
// UIKit — new element appeared; focus it
UIAccessibility.post(notification: .layoutChanged, argument: newlyAppearedButton)

// SwiftUI equivalent — use @AccessibilityFocusState
@AccessibilityFocusState private var isErrorFocused: Bool

// After error appears:
isErrorFocused = true
```

### `.screenChanged` — New View Presented

Use when a completely new screen or major context appears:

```swift
// UIKit — new view controller or major UI replacement
UIAccessibility.post(notification: .screenChanged, argument: newViewController.view)
// VoiceOver: plays navigation sound and focuses the new view
```

**SwiftUI auto-handles `.screenChanged`** for `NavigationStack` pushes and `.sheet` presentations — you rarely need to post it manually.

---

## Anti-Patterns to Avoid

```swift
// ❌ Don't post announcements from background threads
DispatchQueue.global().async {
    UIAccessibility.post(notification: .announcement, argument: "Done")
    // May crash or be ignored — must be on main thread
}

// ✅ Always post from the main thread
DispatchQueue.main.async {
    UIAccessibility.post(notification: .announcement, argument: "Done")
}

// ❌ Don't over-announce — spamming announcements confuses users
for item in items {
    UIAccessibility.post(notification: .announcement, argument: "Processed \(item.name)")
}

// ✅ Announce a summary, not every step
UIAccessibility.post(notification: .announcement, argument: "Processed \(items.count) items")
```

---

## SwiftUI: Check VoiceOver State Before Announcing

Some announcements only make sense when VoiceOver is active. Use `UIAccessibility.isVoiceOverRunning` to guard non-essential notifications:

```swift
// Only announce if VoiceOver is running (avoid noise for non-VO users)
if UIAccessibility.isVoiceOverRunning {
    UIAccessibility.post(notification: .announcement, argument: "Background sync complete")
}
```

For critical state changes (errors, completions), post regardless — the notification is silently ignored when VoiceOver is off.
