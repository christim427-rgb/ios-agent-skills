# Handling Merge Conflicts in .xcstrings Files

## Why This Happens

The `.xcstrings` (String Catalog) file is a **single large JSON file**. When multiple developers add or modify strings in parallel, Git's text-based merge strategy frequently produces conflicts because:

- JSON key ordering may change
- Xcode may reformat the file differently
- Multiple developers adding keys to the same region of the JSON structure causes overlapping changes

## Solutions

### 1. Split Strings Across Multiple Catalogs

Instead of a single `Localizable.xcstrings`, split your strings by feature or module:

```
Strings/
  Authentication.xcstrings
  Dashboard.xcstrings
  Settings.xcstrings
  Common.xcstrings
```

When different developers work on different features, they edit different files, dramatically reducing conflicts.

In code, reference the specific table:

```swift
// SwiftUI
Text("login_title", tableName: "Authentication")

// String(localized:)
String(localized: "login_title", table: "Authentication")
```

### 2. Use Swift Packages for Modularization

If your app is modularized into Swift Packages, each package can have its own String Catalog. This naturally distributes localization files across modules and reduces merge conflicts.

### 3. Resolve Conflicts with the JSON Structure

When you do encounter conflicts, rather than trying to manually merge the JSON:

1. Accept one version entirely (e.g., `git checkout --theirs Localizable.xcstrings`)
2. Open the file in Xcode -- it will re-detect any missing keys from your code
3. Re-add any translations that were in the other branch

### 4. Git Merge Driver

You could set up a custom merge driver in `.gitattributes` for `.xcstrings` files that handles JSON merging more intelligently:

```
*.xcstrings merge=xcstrings
```

However, this requires a custom script and is complex to maintain.

### 5. Coordinate Translation Timing

Have a process where translations are added at specific points (e.g., end of sprint) rather than throughout development, reducing the number of concurrent edits to the catalog.

## Best Practice

The most effective approach is **splitting strings across multiple catalogs** aligned with your feature modules. This scales well and directly addresses the root cause of the conflicts.
