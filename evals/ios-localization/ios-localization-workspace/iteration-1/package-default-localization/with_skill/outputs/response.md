# Swift Package Localized Strings Not Working as Dependency

When a Swift Package's localized strings work within the main app but fail when imported as a dependency in another project, there are three common causes to check.

## 1. Missing `defaultLocalization` in Package.swift

Your `Package.swift` must declare a default localization language. Without this, SPM does not process localization resources:

```swift
let package = Package(
    name: "FeatureAuth",
    defaultLocalization: "en",  // REQUIRED for localized packages
    platforms: [.iOS(.v16)],
    products: [...],
    targets: [
        .target(
            name: "FeatureAuth",
            resources: [.process("Resources")]  // Must include resource processing
        )
    ]
)
```

If `defaultLocalization` is missing, SPM ignores the `.lproj` directories and `.xcstrings` files entirely. The package may appear to work in the host project only if the main app bundle happens to have the same keys.

## 2. Missing `bundle: .module` in Localization Calls

This is the most common enterprise localization bug. Every localization call inside a Swift Package must specify `bundle: .module`:

```swift
// ❌ Defaults to Bundle.main — won't find the package's strings
Text("login_title")
String(localized: "login_subtitle")

// ✅ Looks in the package's own bundle
Text("login_title", bundle: .module)
String(localized: "login_subtitle", bundle: .module)
```

Without `bundle: .module`, the lookup defaults to `Bundle.main` (the host app's bundle). This silently returns the untranslated key. It may appear to work during development if the main app also has a matching key, but fails when the package is consumed by a different project.

## 3. Resource Directory Structure

The `.lproj` directories (or `.xcstrings` file) must be inside the package's Resources folder, and that folder must be declared in the target's `resources` parameter:

```
Sources/FeatureAuth/
├── Resources/
│   ├── en.lproj/
│   │   └── Localizable.strings
│   ├── ru.lproj/
│   │   └── Localizable.strings
│   └── Localizable.xcstrings  // Or use String Catalog
├── Views/
│   └── LoginView.swift
└── ...
```

The target must include:
```swift
.target(
    name: "FeatureAuth",
    resources: [.process("Resources")]
)
```

If the `.lproj` directories are outside the declared resource path, SPM will not include them in the built bundle.

## Exposing the Bundle for Consumers

If other modules need to access your package's localized strings, expose the bundle publicly:

```swift
public extension Bundle {
    static let featureAuth = Bundle.module
}
```

Then consumers can use:
```swift
String(localized: "login_title", bundle: .featureAuth)
```
