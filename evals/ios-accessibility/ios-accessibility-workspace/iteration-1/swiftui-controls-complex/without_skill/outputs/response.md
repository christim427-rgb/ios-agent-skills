# VoiceOver Label Association for Split-Column Form Layouts

## The Problem

The layout you have puts labels and text fields in separate `VStack` columns. VoiceOver reads each element independently and has no way to know that "Username" is the label for the first `TextField`. When a user focuses on the text field, VoiceOver will just say "text field" with no context about what data is expected.

## Root Cause

VoiceOver derives a text field's accessible label from:
1. A `label` parameter passed to the view (e.g., `TextField("Username", text: $username)`)
2. An `.accessibilityLabel()` modifier applied directly to the field
3. A `Label` view that wraps both the icon/text and the control together

When the label and field are in completely separate branches of the view hierarchy (different `VStack` containers), there is no implicit association.

## Solutions

### Option 1: Use the TextField Label Parameter (Simplest)

The straightforward fix is to pass the label text directly to `TextField` and `SecureField`, and hide the visual `Text` labels from VoiceOver so they are not read twice. You can then style the placeholder or use `LabeledContent` for visual layout.

```swift
HStack {
    VStack(alignment: .trailing) {
        Text("Username").accessibilityHidden(true)
        Text("Email").accessibilityHidden(true)
        Text("Password").accessibilityHidden(true)
    }
    VStack(alignment: .leading) {
        TextField("Username", text: $username)
        TextField("Email", text: $email)
        SecureField("Password", text: $password)
    }
}
```

Here, each field has its own accessible label via the first parameter, and the visual `Text` labels are hidden from the accessibility tree with `.accessibilityHidden(true)` so VoiceOver does not announce them separately.

### Option 2: Apply `.accessibilityLabel()` to Each Field

If you need the placeholder to remain empty or show different hint text, apply the label explicitly:

```swift
HStack {
    VStack(alignment: .trailing) {
        Text("Username").accessibilityHidden(true)
        Text("Email").accessibilityHidden(true)
        Text("Password").accessibilityHidden(true)
    }
    VStack(alignment: .leading) {
        TextField("", text: $username)
            .accessibilityLabel("Username")
        TextField("", text: $email)
            .accessibilityLabel("Email")
        SecureField("", text: $password)
            .accessibilityLabel("Password")
    }
}
```

### Option 3: Restructure to Use `Label` or `LabeledContent` (Most Idiomatic)

The cleanest SwiftUI approach is to co-locate the label and field using `LabeledContent` (iOS 16+) or a `Label`-based custom row. This eliminates the association problem entirely:

```swift
Form {
    LabeledContent("Username") {
        TextField("", text: $username)
    }
    LabeledContent("Email") {
        TextField("", text: $email)
    }
    LabeledContent("Password") {
        SecureField("", text: $password)
    }
}
```

`LabeledContent` renders the label and content side by side (similar to your two-column layout) and automatically provides VoiceOver with the correct label association.

If you need this outside a `Form`, you can replicate the layout with a custom row view:

```swift
struct FormRow<Content: View>: View {
    let label: String
    let content: Content

    init(_ label: String, @ViewBuilder content: () -> Content) {
        self.label = label
        self.content = content()
    }

    var body: some View {
        HStack {
            Text(label)
                .frame(maxWidth: .infinity, alignment: .trailing)
                .accessibilityHidden(true)
            content
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}

// Usage:
VStack {
    FormRow("Username") {
        TextField("", text: $username)
            .accessibilityLabel("Username")
    }
    FormRow("Email") {
        TextField("", text: $email)
            .accessibilityLabel("Email")
    }
    FormRow("Password") {
        SecureField("", text: $password)
            .accessibilityLabel("Password")
    }
}
```

### Option 4: Group Each Row and Use `.accessibilityElement(children: .combine)`

For a different approach, wrap each label-field pair in an `HStack` and combine them into one accessibility element:

```swift
VStack {
    HStack {
        Text("Username")
        TextField("", text: $username)
    }
    .accessibilityElement(children: .combine)

    HStack {
        Text("Email")
        TextField("", text: $email)
    }
    .accessibilityElement(children: .combine)

    HStack {
        Text("Password")
        SecureField("", text: $password)
    }
    .accessibilityElement(children: .combine)
}
```

Note: `.accessibilityElement(children: .combine)` merges all child elements into one, which means the text field's editing interaction is also wrapped. This can sometimes interfere with text editing focus. Test carefully with VoiceOver before choosing this approach.

## Recommended Approach

For most cases, **Option 1 or Option 2** are the quickest fixes with the least restructuring. **Option 3 with `LabeledContent`** is the most idiomatic SwiftUI solution if you are on iOS 16+ and comfortable refactoring the layout.

The key principle: every interactive control must have its accessible label either passed as the first argument to the initializer, applied via `.accessibilityLabel()`, or derived from a co-located `Label` view. Labels in a sibling view hierarchy branch are never automatically associated.

## Additional Accessibility Improvements

While fixing the label association, consider also adding:

- `.accessibilityHint()` to describe what each field expects (e.g., `.accessibilityHint("Enter your account username")`)
- `.keyboardType(.emailAddress)` on the email field, which also helps VoiceOver users by triggering appropriate keyboard behavior
- `.textContentType(.username)`, `.textContentType(.emailAddress)`, `.textContentType(.password)` for AutoFill integration, which also benefits assistive technology users
