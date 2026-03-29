# VoiceOver Label Association Fix for Split-Column Form Layout

## Root Cause Analysis

The form uses two separate `VStack` columns — one for labels and one for fields. VoiceOver navigates element by element through the accessibility tree. With this layout, VoiceOver encounters:

1. "Username" (Text)
2. "Email" (Text)
3. "Password" (Text)
4. TextField (no label → reads as empty or skips)
5. TextField (no label → reads as empty or skips)
6. SecureField (no label → reads as empty or skips)

The labels and their corresponding fields are spatially aligned visually but are siblings in separate stacks, so the accessibility tree has no awareness of the intended label-to-field pairing. VoiceOver reads the labels in a group, then the fields in a group, with no connection between them.

---

## Findings

### [CRITICAL] TextFields have no accessible label

**WCAG:** 1.3.1 Info and Relationships, 1.3.5 Identify Input Purpose | **HIG:** Labels for Text Fields

**Issue:** `TextField("", text: $username)` uses an empty string prompt. VoiceOver reads the field as "text field" with no name. The user cannot determine which field they are on.

**VoiceOver Impact:** VoiceOver announces "Text field" three times in a row with no label, making the form completely unusable without sight.

### [CRITICAL] Label-field pairs split across sibling VStacks — no association

**WCAG:** 1.3.1 Info and Relationships | **HIG:** Forms

**Issue:** Labels are in a trailing `VStack` and fields are in a leading `VStack`. VoiceOver has no mechanism to infer the visual alignment. Even if the fields had labels, the reading order would be all labels then all fields — not the natural "label then field" pair order a user expects.

**VoiceOver Impact:** A VoiceOver user hears: "Username, Email, Password, text field, text field, secure text field" — they cannot know which field is which.

---

## Fix Options

### Option 1 (Recommended): Per-row HStack with explicit accessibilityLabel

Restructure into row-per-field `HStack` layout. Each field gets an `.accessibilityLabel` matching the visible text label. The visual `Text` label is hidden from VoiceOver to avoid double-reading.

```swift
// ✅ Corrected — per-row layout with proper accessibility labels
VStack(alignment: .leading, spacing: 12) {
    HStack {
        Text("Username")
            .frame(width: 100, alignment: .trailing)
            .accessibilityHidden(true)  // Hidden: field label covers this
        TextField("Username", text: $username)
            .textContentType(.username)
            .accessibilityLabel("Username")
    }
    HStack {
        Text("Email")
            .frame(width: 100, alignment: .trailing)
            .accessibilityHidden(true)
        TextField("Email address", text: $email)
            .textContentType(.emailAddress)
            .keyboardType(.emailAddress)
            .accessibilityLabel("Email")
    }
    HStack {
        Text("Password")
            .frame(width: 100, alignment: .trailing)
            .accessibilityHidden(true)
        SecureField("Password", text: $password)
            .textContentType(.password)
            .accessibilityLabel("Password")
    }
}
```

**VoiceOver reads (per field when focused):**
- "Username, text field"
- "Email, text field"
- "Password, secure text field"

**Why this works:** Each field carries its own `.accessibilityLabel`. The visual `Text` is hidden from VoiceOver to prevent redundant announcement. Navigation order follows a natural top-to-bottom, label-then-field sequence.

---

### Option 2: `.accessibilityLabeledPair` (keep two-column layout)

If the two-column layout must be preserved for visual design reasons, use `.accessibilityLabeledPair` to explicitly link each label to its field across the view hierarchy. This requires a `@Namespace`.

```swift
// ✅ Two-column layout with explicit label-to-field pairing
struct LoginForm: View {
    @State private var username = ""
    @State private var email = ""
    @State private var password = ""
    @Namespace private var formNamespace

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            VStack(alignment: .trailing, spacing: 12) {
                Text("Username")
                    .accessibilityLabeledPair(
                        role: .label,
                        id: "username",
                        in: formNamespace
                    )
                Text("Email")
                    .accessibilityLabeledPair(
                        role: .label,
                        id: "email",
                        in: formNamespace
                    )
                Text("Password")
                    .accessibilityLabeledPair(
                        role: .label,
                        id: "password",
                        in: formNamespace
                    )
            }
            VStack(alignment: .leading, spacing: 12) {
                TextField("", text: $username)
                    .textContentType(.username)
                    .accessibilityLabeledPair(
                        role: .content,
                        id: "username",
                        in: formNamespace
                    )
                TextField("", text: $email)
                    .textContentType(.emailAddress)
                    .keyboardType(.emailAddress)
                    .accessibilityLabeledPair(
                        role: .content,
                        id: "email",
                        in: formNamespace
                    )
                SecureField("", text: $password)
                    .textContentType(.password)
                    .accessibilityLabeledPair(
                        role: .content,
                        id: "password",
                        in: formNamespace
                    )
            }
        }
    }
}
```

**VoiceOver reads (per field when focused):**
- "Username, text field"
- "Email, text field"
- "Password, secure text field"

**How `.accessibilityLabeledPair` works:** The modifier creates a cross-hierarchy association using a shared `id` and `@Namespace`. The element with `role: .label` supplies the name; the element with `role: .content` becomes the focusable accessible element that announces both the label text and the field role. VoiceOver reads the pair as a single unit.

**Note:** `.accessibilityLabeledPair` requires iOS 14+. The namespace (`@Namespace`) is scoped to the view, so pair IDs only need to be unique within that view.

---

### Option 3: Use SwiftUI `Form` (simplest, most robust)

If there are no strict layout constraints, `Form` with labeled `TextField` initializers is the most robust and maintenance-free approach. All label association and navigation order is handled automatically.

```swift
// ✅ Form-based layout — fully accessible with no extra modifiers needed
Form {
    Section("Account") {
        TextField("Username", text: $username)
            .textContentType(.username)
        TextField("Email", text: $email)
            .textContentType(.emailAddress)
            .keyboardType(.emailAddress)
        SecureField("Password", text: $password)
            .textContentType(.password)
    }
}
```

**VoiceOver reads:**
- "Username, text field"
- "Email, text field"
- "Password, secure text field"

---

## Which Option to Choose

| Situation | Recommended option |
|---|---|
| Visual design requires two-column label + field layout | Option 2 (`.accessibilityLabeledPair`) |
| Flexible layout, custom styling acceptable | Option 1 (per-row HStack) |
| Standard settings or onboarding form | Option 3 (`Form`) |

---

## Additional Issues in the Original Code

These issues are present regardless of which fix is applied:

1. **Empty prompt strings** — `TextField("", ...)` and `SecureField("", ...)` omit the prompt entirely. At minimum, provide a meaningful prompt string even if you also set `.accessibilityLabel`. The prompt is used by autofill heuristics and improves accessibility fallback behavior.

2. **Missing `.textContentType`** — All three fields should declare their content type. This enables Password AutoFill, improves autofill accuracy, and allows VoiceOver to announce the expected content type. Use `.username`, `.emailAddress`, and `.password` respectively.

3. **Missing `.keyboardType`** — The email field should use `.keyboardType(.emailAddress)` to show the `@` key by default.

---

## Confidence Checklist (Post-Fix)

```
[x] No onTapGesture on interactive elements — using TextField/SecureField (standard controls)
[x] No hardcoded font sizes — no .font(.system(size:)) present
[x] No hardcoded colors
[x] Every field has an accessibilityLabel (via .accessibilityLabel or prompt string)
[x] VoiceOver reads label + field role as a pair
[x] Navigation order is logical (top to bottom, label then field)
[x] textContentType declared for autofill and accessibility hints
[ ] Section headings — add .accessibilityAddTraits(.isHeader) if a visible header Text is present
[ ] Form submission button — verify it uses Button with a clear accessibilityLabel
```
