# Making VoiceOver Announce a Section Heading

To make VoiceOver announce an element as a heading, add the `.isHeader` trait. This causes VoiceOver to say "heading" after the element's label and, critically, enables **rotor heading navigation** -- users can spin the VoiceOver rotor to "Headings" and swipe up/down to jump between sections instead of swiping through every element on screen.

## SwiftUI

Use `.accessibilityAddTraits(.isHeader)` on the text that serves as your section heading:

```swift
Text("Account Settings")
    .font(.headline)
    .accessibilityAddTraits(.isHeader)
```

VoiceOver reads: **"Account Settings, heading"**

A few things to know:

- **`Section` headers in `List` get the `.isHeader` trait automatically.** You only need to add it manually for custom headings outside of `List` sections.
- Always use `.accessibilityAddTraits` (not `.accessibilityTraits`) so you add the header trait without overwriting any existing traits on the element.

```swift
// Automatic -- no extra work needed
List {
    Section("Account") {
        // items
    }
}

// Manual -- custom heading outside a List Section
VStack {
    Text("Recent Orders")
        .font(.title2)
        .accessibilityAddTraits(.isHeader)

    ForEach(orders) { order in
        OrderRow(order: order)
    }
}
```

## UIKit

Set the `.header` trait on the label or view that acts as the section heading:

```swift
let sectionHeader = UILabel()
sectionHeader.text = "Account Settings"
sectionHeader.font = UIFont.preferredFont(forTextStyle: .headline)
sectionHeader.accessibilityTraits = .header
```

If the heading is also interactive (for example, a collapsible section), combine traits:

```swift
headerButton.accessibilityTraits = [.header, .button]
```

**Important UIKit note:** When you need to add a trait to an element that already has traits, use `.insert()` instead of assignment to avoid destroying existing traits:

```swift
// Safe -- preserves existing traits
headerButton.accessibilityTraits.insert(.header)

// Dangerous -- overwrites all existing traits (e.g., .button)
headerButton.accessibilityTraits = .header
```

## Why This Matters

Without the header trait, VoiceOver users must swipe through every single element to find section boundaries. With header traits in place, they can use the rotor's Headings mode to jump directly between sections -- the same way a sighted user scans a page by reading section titles. This maps to WCAG 1.3.1 (Info and Relationships), which requires that structural information conveyed visually is also available programmatically.
