Use `UIAccessibility.post(notification:argument:)` with the `.announcement` notification type.

Here is how to do it:

```swift
UIAccessibility.post(notification: .announcement, argument: "Download complete")
```

The `argument` parameter is the string that VoiceOver will speak aloud.

**Important timing consideration:** If you post the announcement immediately when returning to the main thread, VoiceOver may not speak it because the system could be busy with other accessibility updates. A common pattern is to add a small delay:

```swift
DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
    UIAccessibility.post(notification: .announcement, argument: "Upload finished successfully")
}
```

**Key points:**

- The notification must be posted on the **main thread**. If your async completion handler runs on a background queue, dispatch to main first.
- The `argument` should be a localized `String` (use `NSLocalizedString` or String Catalogs).
- If multiple announcements are posted in quick succession, VoiceOver may only speak the last one. If you need to queue announcements, use `UIAccessibility.Notification.announcement` with the `NSAttributedString` approach and the `UIAccessibility.announcementDidFinishNotification` to chain them.

**Listening for completion (optional):**

You can observe whether VoiceOver actually finished speaking the announcement:

```swift
NotificationCenter.default.addObserver(
    forName: UIAccessibility.announcementDidFinishNotification,
    object: nil,
    queue: .main
) { notification in
    guard let userInfo = notification.userInfo,
          let message = userInfo[UIAccessibility.announcementStringValueUserInfoKey] as? String,
          let success = userInfo[UIAccessibility.announcementWasSuccessfulUserInfoKey] as? Bool else {
        return
    }
    print("Announcement '\(message)' finished, success: \(success)")
}
```

This is useful if you need to chain announcements or confirm the user received critical information.
