# List Cell Custom Actions: Fixing the "Too Many Swipes" Problem

## The Problem

When a list cell contains 3 action buttons (Like, Share, Delete) alongside the title, VoiceOver users must swipe through **4 separate elements per cell**: the title, then Like, then Share, then Delete. In a list of 20 items, that's up to 80 swipes just to navigate. Each button is also a swipe target that interrupts the reading flow.

**Severity: 🟢 MEDIUM** — The content is accessible but the experience is significantly degraded.

---

## Solution: `accessibilityCustomActions`

Custom actions let VoiceOver users reach an item in **one swipe**, then access all actions via a dedicated gesture (swipe up/down while focused). This matches the mental model of "focus on this item, then choose what to do."

### How Custom Actions Work for Users

1. User swipes to the list cell — VoiceOver reads the title
2. User swipes up or down (while focused) to cycle through available actions
3. VoiceOver announces each action name: "Like", "Share", "Delete"
4. User double-taps to trigger the selected action

---

## Implementation

```swift
struct FeedItem: Identifiable {
    let id: UUID
    let title: String
}

struct FeedCell: View {
    let item: FeedItem
    var onLike: () -> Void
    var onShare: () -> Void
    var onDelete: () -> Void

    var body: some View {
        // The visible UI can still show buttons for sighted users
        HStack {
            Text(item.title)
                .font(.body)

            Spacer()

            // These buttons remain visible but are hidden from VoiceOver
            // because custom actions handle them accessibly
            HStack(spacing: 12) {
                Button(action: onLike) {
                    Image(systemName: "hand.thumbsup")
                }
                .accessibilityHidden(true)

                Button(action: onShare) {
                    Image(systemName: "square.and.arrow.up")
                }
                .accessibilityHidden(true)

                Button(action: onDelete) {
                    Image(systemName: "trash")
                }
                .accessibilityHidden(true)
            }
        }
        .padding()
        // Group the row as one VoiceOver element
        .accessibilityElement(children: .combine)
        // Register custom actions — each returns Bool to indicate success
        .accessibilityCustomActions([
            AccessibilityCustomAction(name: "Like") {
                onLike()
                return true   // true = action succeeded
            },
            AccessibilityCustomAction(name: "Share") {
                onShare()
                return true
            },
            AccessibilityCustomAction(name: "Delete") {
                onDelete()
                return true
            }
        ])
    }
}
```

**VoiceOver reads on focus:** "Buy groceries" (or whatever the title is)
**User swipes up:** "Like" → "Share" → "Delete" → cycles back
**User double-taps on "Delete":** item deleted

---

## Why Actions Return `Bool`

The return value of each custom action closure indicates whether the action was **successfully handled**:

- Return `true` — action succeeded; VoiceOver plays the standard success tone
- Return `false` — action failed or was not applicable; VoiceOver does not confirm

This matters for conditional actions. For example, if "Delete" is only valid when the user owns the item:

```swift
AccessibilityCustomAction(name: "Delete") {
    guard item.isOwnedByCurrentUser else { return false }
    onDelete()
    return true
}
```

Returning `false` signals to VoiceOver that the action was not available, giving the user appropriate feedback.

---

## UIKit Equivalent

```swift
func tableView(_ tableView: UITableView,
               cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: "FeedCell", for: indexPath)
    let item = items[indexPath.row]

    cell.textLabel?.text = item.title
    cell.accessibilityLabel = item.title

    cell.accessibilityCustomActions = [
        UIAccessibilityCustomAction(name: "Like",
            target: self, selector: #selector(likeItem(_:))),
        UIAccessibilityCustomAction(name: "Share",
            target: self, selector: #selector(shareItem(_:))),
        UIAccessibilityCustomAction(name: "Delete",
            target: self, selector: #selector(deleteItem(_:)))
    ]
    return cell
}

@objc func deleteItem(_ sender: UIAccessibilityCustomAction) -> Bool {
    // Perform deletion
    return true
}
```

---

## Before vs. After

| | Without Custom Actions | With Custom Actions |
|---|---|---|
| Swipes per cell | 4 (title + 3 buttons) | 1 (title, actions via swipe up/down) |
| Swipes for 20-item list | Up to 80 | 20 |
| Navigation flow | Interrupted by action buttons | Linear, purposeful |
| Action discovery | Stumble across buttons | Intentional swipe gesture |
