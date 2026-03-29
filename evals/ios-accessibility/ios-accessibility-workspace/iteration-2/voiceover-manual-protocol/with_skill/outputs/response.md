# VoiceOver Manual Testing Protocol

Automated accessibility audits catch approximately 30% of real-world accessibility issues. Manual VoiceOver testing with the Screen Curtain is the only way to find the rest — focus order problems, wrong labels, unannounced state changes, broken modal trapping, and navigation dead-ends.

## Enabling VoiceOver

**Quickest method:** Triple-click the side button (if configured in Settings > Accessibility > Accessibility Shortcut).

**Settings path:** Settings > Accessibility > VoiceOver > toggle On.

## 10-Step Manual Testing Protocol

### Step 1: Linear Navigation — Verify Order and Coverage

Swipe right continuously through the entire screen. Every interactive element must be reachable. Verify:
- Elements are announced in logical reading order (top-left to bottom-right matches visual layout)
- No elements are skipped
- No unexpected elements appear (decorative images should be silent)

Expected: all buttons, text fields, labels, and interactive elements appear in order.

### Step 2: Element Identification

For each interactive element, verify it announces:
- A meaningful **label** (not "image", not a filename, not a raw SF Symbol name like "plus")
- The correct **role** ("Button", "Toggle", "Text field", "Link")
- The current **state** for stateful controls ("On", "Off", "Selected", "Dimmed")

### Step 3: Rotor — Heading Navigation

Open the Rotor by rotating two fingers on the screen. Select "Headings". Swipe down to navigate through headings.

Verify:
- Every section has a heading that can be located via rotor
- Heading text accurately describes the section content
- No headings are missing, causing navigation dead-ends in long screens

### Step 4: Custom Actions

Navigate to list cells and other elements that have secondary actions. Swipe up/down to cycle through available actions.

Verify:
- Actions are present for cells with multiple operations (Delete, Share, Archive, etc.)
- Action names are clear and imperative ("Delete message", not "deletion")
- Actions work when double-tapped

### Step 5: Modal Focus Trapping

Present every modal, sheet, alert, and bottom drawer in the app. Verify:
- VoiceOver focus immediately moves into the modal on presentation
- Swiping right/left cycles only through elements inside the modal — background elements are silent
- Swiping left past the first element wraps to the last, not to background content

### Step 6: Escape Gesture

With a modal open, perform the Z-shaped escape gesture (two-finger Z scrub) to dismiss.

Verify:
- Modal dismisses
- VoiceOver focus returns to the element that triggered the modal (or to a logical fallback)
- Background content becomes navigable again

### Step 7: Dynamic Content

Trigger loading states, error conditions, and empty states. Verify:
- Loading indicators are announced
- Error messages are announced when they appear (VoiceOver announcement notification)
- Empty states are readable
- Content updates (new list items, refreshed data) are announced appropriately

### Step 8: Screen Curtain Test — The Gold Standard

Triple-tap with three fingers to toggle Screen Curtain on. The screen goes completely black.

**Complete your primary user tasks using only audio.** If you cannot complete a task blind — creating an account, checking out, sending a message, reading a document — real VoiceOver users cannot either.

This test catches:
- Labels that make sense visually but not aurally
- Navigation sequences that require seeing the screen to understand context
- Actions that have no VoiceOver-discoverable path
- Confirmation dialogs that steal focus without announcement

Triple-tap three fingers again to restore the screen when done.

### Step 9: Redundancy Check

Scan for elements that announce their type in their label:
- "Submit button" → wrong — VoiceOver already adds "Button" from the trait
- "Play button" → wrong
- "Search" → correct
- "Play" → correct

Labels must describe purpose, not include the element type.

### Step 10: Decorative Check

Navigate through any decorative imagery, dividers, background graphics, and icon-only visual indicators. All purely decorative elements must be completely silent — VoiceOver should skip them entirely.

## Element-Specific Verification Checklist

| Element Type | What to Verify |
|---|---|
| Icon-only Button | Meaningful label, "Button" announced, action is clear |
| Toggle | Label + current value ("On"/"Off") + "Toggle" role |
| Text Field | Label announced before "Text field", can enter text, text content readable |
| Section Heading | Label + "Heading" announced — appears in Rotor > Headings |
| List Cell | Label + optional hint + custom actions accessible |
| Tab Bar Item | Label + "Tab, X of Y" |
| Alert | Title and message announced on appearance, focus inside |
| Image | Informative: meaningful label; Decorative: silent |
| Disabled Control | Label + "Dimmed" — not silent |

## Common Failures Found Only by Manual Testing

1. VoiceOver reads fields out of order due to absolute positioning
2. Modal appears but VoiceOver focus stays behind it (missing `accessibilityViewIsModal`)
3. Loading spinner announced but completion is not
4. Custom drawer closes but VoiceOver focus disappears to top of screen
5. Table cells with swipe actions that are unreachable by VoiceOver
6. Labels that name the icon appearance ("Heart icon") not the action ("Add to favorites")
