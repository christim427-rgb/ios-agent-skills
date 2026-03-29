# Form Labels and TextFields in Separate VStack Columns — VoiceOver Fix

## The Problem

When a label and its corresponding `TextField` are placed in separate `HStack` columns (e.g., a two-column grid layout), VoiceOver reads them as unrelated elements. It might announce "First name" and then separately "Text field" with no connection between them.

```swift
// Problematic layout
HStack {
    VStack(alignment: .leading) {
        Text("First name")
        Text("Last name")
    }
    VStack {
        TextField("", text: $firstName)
        TextField("", text: $lastName)
    }
}
```

## Fix 1: Group Label + Field Together Using `.accessibilityElement`

Pair each label with its field in a single accessible element:

```swift
HStack {
    VStack(alignment: .leading) {
        HStack {
            Text("First name")
            TextField("", text: $firstName)
                .accessibilityLabel("First name")
        }
        HStack {
            Text("Last name")
            TextField("", text: $lastName)
                .accessibilityLabel("Last name")
        }
    }
}
```

The simplest fix is to set `accessibilityLabel` directly on the `TextField`:

```swift
TextField("", text: $firstName)
    .accessibilityLabel("First name")

TextField("", text: $lastName)
    .accessibilityLabel("Last name")
```

## Fix 2: Use a Labeled TextField (iOS 15+)

```swift
LabeledContent("First name") {
    TextField("", text: $firstName)
}
```

`LabeledContent` properly associates the label with the content for both display and accessibility.

## Fix 3: Use `TextField` with a Non-Empty Placeholder or Label

```swift
TextField("First name", text: $firstName)
```

When the placeholder is the field's label, VoiceOver reads it as the label (until the user types). This is acceptable for simple forms.

## Fix 4: Use `Form` with a `Section`

SwiftUI's `Form` automatically handles label association in many cases:

```swift
Form {
    TextField("First name", text: $firstName)
    TextField("Last name", text: $lastName)
}
```

## Best Practice

Restructure the layout so each label and field row is together, rather than in separate columns. This is both more accessible and more maintainable:

```swift
VStack(spacing: 12) {
    VStack(alignment: .leading, spacing: 4) {
        Text("First name").font(.caption)
        TextField("", text: $firstName)
            .textFieldStyle(.roundedBorder)
    }
    VStack(alignment: .leading, spacing: 4) {
        Text("Last name").font(.caption)
        TextField("", text: $lastName)
            .textFieldStyle(.roundedBorder)
    }
}
```

With this structure, VoiceOver navigates naturally from label to field within each group.
