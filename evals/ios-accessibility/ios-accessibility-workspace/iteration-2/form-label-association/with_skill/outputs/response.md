# Form Label Association for VoiceOver

## The Problem

When labels and TextFields are in separate columns (e.g., `HStack` with two `VStack` children), VoiceOver reads them in DOM order — traversing all labels first, then all fields — breaking the association between each label and its field.

```swift
// ❌ VoiceOver reads: "Username", "Email", "Password", then text fields separately
HStack(alignment: .top) {
    VStack(alignment: .trailing) {
        Text("Username")
        Text("Email")
        Text("Password")
    }
    VStack(alignment: .leading) {
        TextField("", text: $username)
        TextField("", text: $email)
        SecureField("", text: $password)
    }
}
```

VoiceOver navigation: "Username" → "Email" → "Password" → [text field] → [text field] → [text field]. The user has no idea which field is which.

## Fix 1: accessibilityLabel on Each Field (Simplest)

Set `accessibilityLabel` directly on each `TextField` to carry the label text:

```swift
// ✅ Each field announces its own label
VStack {
    HStack {
        Text("Username").frame(width: 100, alignment: .trailing)
        TextField("", text: $username)
            .accessibilityLabel("Username")
            .textContentType(.username)
    }
    HStack {
        Text("Email").frame(width: 100, alignment: .trailing)
        TextField("", text: $email)
            .accessibilityLabel("Email address")
            .textContentType(.emailAddress)
            .keyboardType(.emailAddress)
    }
    HStack {
        Text("Password").frame(width: 100, alignment: .trailing)
        SecureField("", text: $password)
            .accessibilityLabel("Password")
            .textContentType(.password)
    }
}
```

VoiceOver reads on each field: "Username. Text field." / "Email address. Text field." / "Password. Secure text field."

## Fix 2: accessibilityLabeledPair (For True Separation)

When the label and field genuinely must be in separate parts of the view hierarchy, use `accessibilityLabeledPair` with a shared namespace to link them:

```swift
struct LabeledFormField: View {
    @Namespace private var formNamespace

    var body: some View {
        HStack(alignment: .top) {
            // Left column: labels
            VStack(alignment: .trailing, spacing: 16) {
                Text("Username")
                    .accessibilityLabeledPair(role: .label, id: "username", in: formNamespace)
                Text("Email")
                    .accessibilityLabeledPair(role: .label, id: "email", in: formNamespace)
            }
            // Right column: fields
            VStack(alignment: .leading, spacing: 8) {
                TextField("", text: $username)
                    .accessibilityLabeledPair(role: .content, id: "username", in: formNamespace)
                    .textContentType(.username)
                TextField("", text: $email)
                    .accessibilityLabeledPair(role: .content, id: "email", in: formNamespace)
                    .textContentType(.emailAddress)
            }
        }
    }
}
```

## Fix 3: Prompt-Based Label (Simplest for Simple Forms)

The simplest approach: include the label as the `TextField` prompt. SwiftUI uses the prompt string as the `accessibilityLabel` automatically.

```swift
// ✅ Prompt doubles as accessibility label
TextField("Username", text: $username)
    .textContentType(.username)

TextField("Email address", text: $email)
    .textContentType(.emailAddress)
    .keyboardType(.emailAddress)

SecureField("Password", text: $password)
    .textContentType(.password)
```

The prompt placeholder disappears when text is entered — so add `accessibilityLabel` explicitly if the prompt doesn't match the desired label:

```swift
TextField("user@example.com", text: $email)
    .accessibilityLabel("Email address")  // More descriptive than the placeholder
    .textContentType(.emailAddress)
```

## textContentType: Enable Autofill (WCAG 1.3.5)

Always set `textContentType` on form fields. This satisfies **WCAG 1.3.5 Identify Input Purpose** and enables Password AutoFill and Autofill from Contacts:

| Field | `textContentType` |
|---|---|
| Username | `.username` |
| Email | `.emailAddress` |
| Password | `.password` |
| New password | `.newPassword` |
| Phone | `.telephoneNumber` |
| Given name | `.givenName` |
| Family name | `.familyName` |
| Postal code | `.postalCode` |

## Recommendation

For most forms, Fix 1 (`accessibilityLabel` on each field) is the right choice — it is the simplest, most reliable, and most compatible approach. Use `accessibilityLabeledPair` only when design requirements prevent restructuring the view hierarchy to co-locate label and field.
