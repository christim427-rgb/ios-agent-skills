# Comprehensive VoiceOver Manual Testing Protocol

## Setup

1. Enable VoiceOver: Settings > Accessibility > VoiceOver > On (or triple-click the side/home button if accessibility shortcut is configured).
2. Learn the essential gestures before testing: single finger swipe right/left (next/previous element), double-tap (activate), two-finger swipe down (read all), three-finger swipe (scroll).
3. Turn off the display (optional): Settings > Accessibility > VoiceOver > Screen Curtain (triple-tap with three fingers) — test as a blind user would.

## Phase 1: Navigation and Focus Order

Check in this order:

- [ ] Swipe right through every element on the screen. Does focus reach every interactive and informative element?
- [ ] Is the reading order logical (top-to-bottom, left-to-right, or in the order that makes sense for the content)?
- [ ] Are decorative elements correctly hidden (no "image" announcements for icons that are purely visual)?
- [ ] Does focus jump unexpectedly? (Custom containers, `zStack` overlays, and modals are common offenders)

## Phase 2: Element Labels and Descriptions

For each focusable element:

- [ ] Does it have a clear, meaningful label? ("Add item" vs. "button" or "plus")
- [ ] Is the label contextual? ("Delete John Smith" not just "Delete")
- [ ] Is the trait correct? (Button, header, image, link, toggle — no mislabeled traits)
- [ ] Is the value announced for stateful controls? (Toggle: "On" / "Off"; Slider: "50%"; Progress: "75%")
- [ ] Is there a hint? For non-obvious controls, VoiceOver should provide a brief usage hint after a pause.

## Phase 3: Interactive Controls

- [ ] Buttons: Double-tap activates the action. The action completes successfully.
- [ ] Toggles / Switches: Value changes and the new state is announced.
- [ ] Text fields: Focus moves to the field; keyboard appears; typed text is echoed; field label is re-read when leaving.
- [ ] Sliders: Swipe up/down changes the value; value is announced continuously.
- [ ] Steppers: Increment and decrement work with swipe up/down; value announced.
- [ ] Pickers: Swipe up/down cycles through options; current selection announced.

## Phase 4: Dynamic Content

- [ ] When new content loads (network request, lazy list), VoiceOver focus stays on a logical element (not lost).
- [ ] When a modal or sheet appears, focus moves into it automatically.
- [ ] When a modal or sheet is dismissed, focus returns to the element that triggered it.
- [ ] Error messages, success messages, and toast notifications are announced (check for `UIAccessibility.post(notification: .announcement)`).
- [ ] Alerts: VoiceOver reads the title and message; focus lands on the first button.
- [ ] Loading indicators: Announced when shown ("Loading"); dismissed state is announced when done.

## Phase 5: Lists and Scrollable Content

- [ ] Lists scroll when VoiceOver focus reaches the last visible item.
- [ ] List items have full context ("John Smith, 3 messages, unread" — not just the name).
- [ ] Section headers are announced as headings (`.isHeader` trait).
- [ ] Swipe-to-delete / swipe actions are accessible via the Actions rotor (not just physical swipe).

## Phase 6: Rotor

Activate the rotor by rotating two fingers on screen:

- [ ] Headings rotor: Navigating by headings moves through section titles correctly.
- [ ] Links rotor: Any inline links are reachable.
- [ ] Actions rotor: Custom actions (move up/down, delete, etc.) appear for relevant elements.
- [ ] Form controls: Text fields and other inputs are navigable via the form controls rotor option.

## Phase 7: Modals, Sheets, and Navigation

- [ ] Pushing a new screen: Focus moves to the new screen's title or first element.
- [ ] Popping back: Focus returns to the initiating element (or top of screen).
- [ ] Modal presented: Focus is trapped inside the modal (can't swipe out to background elements).
- [ ] Modal dismissed: Focus returns to the trigger element.
- [ ] Tab bar: Each tab is labeled and the selected state is announced.

## Phase 8: Edge Cases

- [ ] Empty states: "No results" or placeholder views are announced.
- [ ] Disabled controls: Announced as "dimmed" — not hidden.
- [ ] Long lists: Performance doesn't degrade when swiping through many items.
- [ ] Nested scroll views: Scrolling in embedded scroll areas works.
- [ ] Custom gestures: Any feature requiring a specific gesture (e.g., pull-to-refresh) also has a VoiceOver-accessible alternative.

## Reporting Issues

For each issue found, record:
1. Screen / component name
2. Element description (label, or position if unlabeled)
3. Expected VoiceOver behavior
4. Actual VoiceOver behavior
5. Steps to reproduce
6. Severity: Critical (feature inaccessible), Major (confusing but usable), Minor (polish issue)
