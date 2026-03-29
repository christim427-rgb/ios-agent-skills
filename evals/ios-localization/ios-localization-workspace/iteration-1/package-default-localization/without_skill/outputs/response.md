# Swift Package Localized Strings Not Working as a Dependency

## Common Causes

There are several things to check when a Swift Package's localized strings work in isolation but break when imported into another project.

### 1. Missing `defaultLocalization` in Package.swift

Your `Package.swift` must declare the default localization:

```swift
let package = Package(
    name: "MyPackage",
    defaultLocalization: "en",  // This is required!
    platforms: [.iOS(.v15)],
    // ...
)
```

Without this, SPM doesn't know which language is the default, and localization resources may not be bundled correctly.

### 2. Missing `bundle: .module` in Localization Calls

Inside a Swift Package, you must specify `bundle: .module` to look up strings from the package's own bundle rather than the main app bundle:

```swift
// Wrong: looks in the main app bundle
Text("login_title")
String(localized: "login_subtitle")

// Correct: looks in the package's bundle
Text("login_title", bundle: .module)
String(localized: "login_subtitle", bundle: .module)
```

Without `bundle: .module`, the runtime searches `Bundle.main` (the host app), which doesn't contain the package's translations.

### 3. Localization Files Must Be in the Right Location

Ensure your `.lproj` directories (or `.xcstrings` file) are inside the package's resources directory and properly declared in `Package.swift`:

```
Sources/
  MyFeature/
    Resources/
      en.lproj/
        Localizable.strings
      de.lproj/
        Localizable.strings
    Views/
      LoginView.swift
```

And in your target definition:

```swift
.target(
    name: "MyFeature",
    resources: [
        .process("Resources")
    ]
)
```

If using String Catalogs (`.xcstrings`), the file should be in the source directory and SPM will process it automatically.

### 4. Clean Build

After making these changes, do a clean build (Product > Clean Build Folder) to ensure Xcode picks up the resource changes.

## Checklist

1. `defaultLocalization: "en"` is set in `Package.swift`
2. All localization calls use `bundle: .module`
3. `.lproj` directories are in the declared resources path
4. Target includes a `resources:` declaration
5. Clean build after changes
