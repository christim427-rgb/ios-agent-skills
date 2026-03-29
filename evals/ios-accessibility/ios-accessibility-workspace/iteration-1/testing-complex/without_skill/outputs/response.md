# VoiceOver Manual Testing Protocol for iOS

A comprehensive, ordered protocol for manually testing VoiceOver accessibility on iOS apps.

---

## Phase 1: Setup and Preparation

### 1.1 Enable VoiceOver
- Go to Settings > Accessibility > VoiceOver and toggle it on, OR
- Use the Accessibility Shortcut (triple-click Side/Home button) if configured
- Recommended: Add VoiceOver to the Accessibility Shortcut before testing

### 1.2 Configure Testing Environment
- Set Speech Rate to a comfortable level (Settings > Accessibility > VoiceOver > Speaking Rate)
- Ensure "Speak Hints" is enabled (Settings > Accessibility > VoiceOver > Verbosity > Speak Hints)
- Enable "Speak Screen" and "Speak Selection" for supplemental checks
- Turn off Display Accommodations that might mask visual bugs
- Test on a physical device when possible — simulator VoiceOver behavior can differ

### 1.3 Know the Core Gestures
- **Single tap**: Move focus to element
- **Swipe right/left**: Move to next/previous element
- **Double tap**: Activate focused element
- **Two-finger swipe up**: Read all from top
- **Two-finger swipe down**: Read all from current position
- **Three-finger swipe**: Scroll
- **Swipe up/down with one finger**: Adjust value in adjustable elements
- **Escape (two-finger Z)**: Go back / dismiss modal

---

## Phase 2: Navigation and Focus Order

### 2.1 Linear Navigation (Swipe Navigation)
- Start from the top of each screen
- Swipe right through every interactive and informational element
- Verify that **every meaningful element receives focus** — nothing should be skipped unintentionally
- Verify that **decorative/redundant elements do not receive focus** (pure decorative images, dividers, etc.)
- Verify the **focus order is logical** and follows the visual reading order (top-to-bottom, left-to-right in LTR layouts)
- Check that focus does not jump unexpectedly to distant parts of the screen

### 2.2 Focus Containment in Modals and Sheets
- Open each modal, action sheet, bottom sheet, and popover
- Verify focus is **trapped within the modal** — swiping past the last element should wrap to the first element inside the modal, not escape to background content
- Verify that background content is **not accessible** while a modal is open
- Dismiss the modal and confirm focus returns to a sensible location (typically the element that triggered it)

### 2.3 Focus After Navigation Transitions
- Navigate between screens using the app's navigation (tab bar, push navigation, etc.)
- Verify focus lands at the **top of the new screen** or a logical starting point after each transition
- Verify focus is not lost (i.e., no "VoiceOver focus lost" behavior where nothing is announced)
- Test the back gesture and confirm focus returns to a meaningful element on the previous screen

### 2.4 Dynamic Content Focus Management
- Trigger any action that updates the screen (loading states, search results, errors, toasts, banners)
- Verify VoiceOver announces the update or moves focus appropriately
- Check that focus is not stranded on an element that has disappeared

---

## Phase 3: Element Labels and Descriptions

### 3.1 All Interactive Elements Have Labels
- Focus on every button, link, toggle, segmented control, tab bar item, and gesture-driven element
- Every element must have a **meaningful accessibility label** — not just an icon or image filename
- Labels should be **concise** (1–3 words for buttons where possible) and describe the action or content
- Labels must be **localized** — test in a secondary language if internationalization is in scope

### 3.2 Labels Are Not Redundant or Verbose
- Avoid labels that repeat the element type (e.g., do not say "Button" in the label; VoiceOver appends the trait automatically)
- Avoid labels that state the visual appearance (e.g., "blue circle icon") unless visually descriptive context is required
- Confirm that grouped cells/rows do not announce redundant sub-element labels when the group as a whole is focused

### 3.3 Images and Icons
- Decorative images must have `isAccessibilityElement = false` or `accessibilityHidden = true`
- Informational images must have a descriptive label explaining what they convey
- Product/content images should describe their subject matter, not their technical description

### 3.4 State is Communicated in the Label or Value
- Toggles and checkboxes must announce their current state ("On"/"Off", "Checked"/"Unchecked")
- Buttons that change state (e.g., a "Follow" button that becomes "Unfollow") must reflect the **current state** in their label or value, not the next action
- Loading states must be announced (e.g., "Loading" or use `UIAccessibilityTraitUpdatesFrequently`)

### 3.5 Hint Quality
- Hints should only be present when the action is non-obvious from the label alone
- Hints must describe the **result** of the action, not the gesture (e.g., "Opens profile details", not "Double tap to open")
- Hints are read after a pause; verify they are not confusingly worded

---

## Phase 4: Accessibility Traits

### 4.1 Correct Traits Are Assigned
Verify each element type carries the appropriate trait:
- **Button**: elements that trigger an action
- **Link**: elements that navigate to a URL or deep link
- **Header**: section headers (allows rotor navigation by headings)
- **Image**: standalone images
- **Selected**: currently selected tab, segment, or list item
- **Adjustable**: sliders, steppers, pickers
- **Search Field**: search text inputs

### 4.2 No Incorrect Traits
- Verify no non-interactive element has the button trait
- Verify no decorative element has the image trait
- Verify static text does not have the "adjustable" or "link" trait unless it actually is adjustable/a link

### 4.3 Disabled State
- Disabled buttons must still be focusable with VoiceOver and announce "Dimmed" (the iOS standard trait)
- Verify that disabled elements announce their label so the user understands what is unavailable

---

## Phase 5: Rotor Navigation

### 5.1 Access and Test Rotor Options
- Open the rotor by rotating two fingers on the screen (like turning a dial)
- Verify the following rotor options work as expected if the app has corresponding content:
  - **Headings**: Navigate between section headers using swipe up/down
  - **Links**: Navigate between tappable links
  - **Buttons**: Navigate between buttons
  - **Form Controls**: Navigate between input fields, toggles, pickers
  - **Tables / Rows**: Navigate within list or table content
  - **Words / Characters**: Navigate within editable text

### 5.2 Heading Structure
- The screen should have a logical heading hierarchy (H1 for the page title, H2 for section headers, etc.)
- Avoid skipping heading levels
- Verify all section headers are marked with the `.header` trait

### 5.3 Custom Rotor Actions (if applicable)
- If the app implements custom rotor actions (e.g., swipe up/down for contextual actions on a list item), verify they are announced and functional

---

## Phase 6: Text Input and Forms

### 6.1 Text Field Labels
- Every `UITextField` and `UITextView` must have an accessibility label (either set directly or via a visible label associated to it)
- Placeholder text alone is not an acceptable substitute for a label
- When a field has a permanent visible label, verify the label is programmatically linked (not just visually adjacent)

### 6.2 Keyboard Behavior
- Focus a text field and double-tap to activate
- Verify the keyboard appears and VoiceOver switches to typing mode
- Verify single-character announcement as keys are typed
- Verify deletion announcement when backspace is used

### 6.3 Error Messages and Validation
- Submit a form with intentional errors
- Verify error messages are announced — either through focus being moved to the error or via an accessibility notification
- Error messages must be associated with their respective fields so the user knows which field to correct

### 6.4 Pickers, Steppers, and Sliders
- Focus an adjustable element
- Use swipe up/down to change the value
- Verify the current value is announced after each adjustment
- Verify the label clearly describes what is being adjusted

---

## Phase 7: Tables, Lists, and Collections

### 7.1 List Navigation
- Navigate into a list or table
- Verify each row/cell announces a complete, meaningful description in a single announcement (rather than forcing the user to navigate into sub-elements)
- Avoid exposing sub-elements of a row as separate focusable items unless there is a specific need (e.g., a row with a delete button)

### 7.2 Collection Views and Grids
- Verify grid items announce their position (e.g., "Item 3 of 12") using `accessibilityLabel` or by inheriting from `UICollectionView`
- Verify rows and columns are discernible if the grid has a tabular structure

### 7.3 Section Headers and Footers
- Table section headers must be focusable and labeled
- Section footers with meaningful content must also be accessible

### 7.4 Empty States
- Trigger empty list states (no results, no data)
- Verify the empty state view is announced and describes why the list is empty

---

## Phase 8: Custom Gestures and Interactions

### 8.1 Swipe-Based Custom Gestures
- Identify any custom gesture recognizers (swipe to delete, pull to refresh, drag to reorder, swipe for contextual actions)
- Verify these have VoiceOver equivalents:
  - Swipe to delete: accessible via Edit button or custom action
  - Pull to refresh: accessible via a "Refresh" button or custom rotor action
  - Drag to reorder: accessible via Edit mode with move buttons

### 8.2 Custom Actions
- Activate the Actions rotor option for list items with contextual actions
- Verify all available actions are listed and labeled meaningfully
- Double-tap to trigger an action and confirm it executes correctly

### 8.3 Long Press Actions
- If long press reveals a context menu or peek, verify an accessible alternative exists (custom action or a dedicated button)

---

## Phase 9: Dynamic and Animated Content

### 9.1 Alerts and Notifications
- Trigger in-app alerts (UIAlertController)
- Verify VoiceOver automatically focuses on the alert when it appears
- Verify the alert title, message, and all buttons are announced

### 9.2 Toasts, Banners, and Inline Notifications
- Trigger non-blocking notifications (e.g., success banners, snackbars)
- Verify the message is announced via `UIAccessibility.post(notification: .announcement, argument:)`
- Verify transient messages do not steal persistent focus from the user's current element

### 9.3 Loading States
- Trigger loading (network request, data fetch)
- Verify loading indicators announce a loading state
- Verify when loading completes, VoiceOver announces the result or new content

### 9.4 Animations
- Verify animations do not interfere with VoiceOver focus
- Verify elements that animate in are announced when they appear
- Check behavior with "Reduce Motion" enabled (Settings > Accessibility > Motion > Reduce Motion)

---

## Phase 10: Screen-Specific Checks

### 10.1 Onboarding and Authentication
- Walk through all onboarding steps with VoiceOver
- Test login, signup, and password reset flows end-to-end
- Verify CAPTCHA alternatives are provided if applicable
- Verify social login buttons are properly labeled (e.g., "Sign in with Apple", not just the Apple logo)

### 10.2 Navigation Bars and Tab Bars
- Verify navigation bar title is announced as a heading
- Verify Back button label reflects the previous screen title (e.g., "Back" or "Settings")
- Verify tab bar items announce their label and selected state
- Verify the badge value on tab bar items is included in the announcement (e.g., "Messages, 3 unread")

### 10.3 Search
- Focus the search bar and verify it announces "Search Field" or equivalent
- Type a query and verify results are announced or reachable
- Verify the cancel/clear button is accessible

### 10.4 Media and Rich Content
- Verify video players have accessible play/pause, scrubber, and volume controls
- Verify that media with audio does not conflict with VoiceOver speech (consider offering captions)
- Verify maps and charts have text-based alternatives or descriptions

### 10.5 Web Views (WKWebView)
- Navigate into any embedded web content
- Verify headings, links, and form elements are accessible via the Web rotor option
- Watch for focus being lost at the boundary between native and web content

---

## Phase 11: Edge Cases and Regression Tests

### 11.1 Orientation Changes
- Rotate the device while VoiceOver is active
- Verify focus is maintained or intelligently reassigned after rotation
- Verify layout changes are reflected correctly in the accessibility tree

### 11.2 Interruptions
- Receive a phone call or notification while using the app with VoiceOver
- Dismiss the interruption and verify VoiceOver returns to the correct position in the app

### 11.3 Background and Foreground
- Send the app to the background and bring it back to foreground
- Verify VoiceOver focus is restored to the same or a sensible location

### 11.4 Scroll Behavior
- Scroll through long content with three-finger swipe
- Verify newly revealed elements are navigable
- Verify VoiceOver does not announce off-screen elements as if they were visible

### 11.5 iPad Split View and Multitasking (if applicable)
- Test in Split View and Slide Over modes
- Verify focus is contained within the correct app window

---

## Phase 12: Final "Read All" Pass

### 12.1 Automated Read-Through
- On each screen, use two-finger swipe down to trigger "Read All from Top"
- Listen for the complete readout of the screen
- Flag any elements that are skipped, read nonsensically, or read out of order
- Flag any elements that interrupt the reading flow unexpectedly

### 12.2 Compare Against Visual Layout
- After the read-through, compare what was announced against what is visually present
- Ensure no visual information was omitted from the auditory experience
- Ensure no information was only conveyed through color alone

---

## Common Issues Checklist

| Issue | What to Check |
|---|---|
| Missing label | Button/image has no announcement or announces file name |
| Wrong trait | Static text announced as button, or interactive element not announced as button |
| Focus not trapped in modal | Swiping past last modal element reaches background |
| Focus lost after transition | Nothing is focused on a new screen |
| Focus not returned on dismiss | Focus stays on dismissed element or goes to top of screen |
| Decorative image focused | Image receives focus and announces an unhelpful description |
| Redundant announcement | Element repeats the word "button" in its label |
| State not announced | Toggle does not say "On" or "Off" |
| Custom gesture inaccessible | Swipe action has no alternative for VoiceOver users |
| Error not announced | Form validation error appears visually but is not read |
| Truncated label in cell | Cell sub-elements are exposed separately instead of as a grouped label |
| Badge not read | Tab bar badge count is not included in the item's announcement |

---

## Recommended Testing Order Summary

1. Setup and configure VoiceOver
2. Test each screen's focus order (linear swipe navigation)
3. Test modal and sheet focus containment
4. Test all element labels and traits
5. Test rotor navigation (headings, links, form controls)
6. Test all forms and text inputs
7. Test lists, tables, and collection views
8. Test custom gestures and actions
9. Test dynamic content (alerts, toasts, loading)
10. Test screen-specific flows (onboarding, auth, media, search)
11. Test edge cases (rotation, interruptions, background/foreground)
12. Perform a "Read All" pass on each screen

---

## Tools to Supplement Manual Testing

- **Accessibility Inspector** (Xcode): Run audits and inspect the accessibility tree without a physical device
- **axe DevTools Mobile**: Automated scanning for common issues
- **VoiceOver Recognition**: Enable in Settings > Accessibility > VoiceOver > Recognition to see what VoiceOver is inferring for unlabeled elements
- **UIAccessibility Notifications Logging**: Use Xcode's console to observe `UIAccessibilityPostNotification` calls during testing
