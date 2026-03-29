# Merge Conflicts in .xcstrings Files

This is a well-known pain point with String Catalogs. The root cause is that `.xcstrings` is a **single large JSON file**, and Git's text-based merge cannot understand JSON tree structure. Two developers adding completely unrelated keys to different parts of the file can create textual conflicts even though the changes are semantically non-conflicting.

## Why It Happens

The `.xcstrings` format stores all localization keys in one flat JSON object. When developer A adds key `"feature_a.title"` and developer B adds key `"feature_b.title"`, both changes modify the same `"strings"` JSON object. Git sees overlapping text regions and reports a conflict, even though the keys are independent.

## Mitigation: Split Strings Across Multiple Catalogs

The most effective solution is to **split your strings across multiple String Catalogs**, typically by feature or module:

```
MyApp/
├── Features/
│   ├── Auth/AuthLocalizable.xcstrings        # Auth-related strings only
│   ├── Settings/SettingsLocalizable.xcstrings # Settings strings only
│   └── Chat/ChatLocalizable.xcstrings        # Chat strings only
└── Shared/SharedLocalizable.xcstrings        # Common UI strings
```

When using multiple catalogs, reference the table name in code:

```swift
// SwiftUI
Text("login_title", tableName: "AuthLocalizable")

// UIKit
String(localized: "login_title", table: "AuthLocalizable")
```

## Mitigation: Use Swift Packages

For modular apps, put each feature in its own Swift Package with its own localization catalog. Each package has an independent `.xcstrings` file, so different teams working on different features never touch the same file.

## Known Xcode Bug: Comment Order Randomization

Another source of false-positive dirty Git diffs is an Xcode bug where the **comment order randomizes between builds**. When the same key appears with different comments across source files, Xcode concatenates them with `\n` in random order. This causes spurious diffs even when no actual strings changed.

**Mitigation:** Use one canonical comment per key. Avoid defining the same key in multiple source files with different comments.

## Resolving Conflicts When They Happen

When you do get a merge conflict in `.xcstrings`:
1. Accept either side of the conflict
2. Manually re-add the other side's keys
3. Validate the JSON is well-formed after resolution
4. Run `python3 scripts/xcstrings_tool.py validate` to verify completeness

Since both sides usually added different keys to the same JSON object, the resolution is typically straightforward — you need both sets of keys in the final file.
