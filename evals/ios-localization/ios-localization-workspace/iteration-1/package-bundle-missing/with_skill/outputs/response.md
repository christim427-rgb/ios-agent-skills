The problem is that both `Text()` and `String(localized:)` are missing the `bundle: .module` parameter. In a Swift Package, localization resources are in the package's own bundle, not in `Bundle.main`. Without specifying the bundle, the system looks in the main app bundle, finds nothing, and falls back to displaying the raw key.

## The Fix

Add `bundle: .module` to both calls:

```swift
// Inside MyPackage/Sources/FeatureAuth/LoginView.swift

// SwiftUI Text
Text("login_title", bundle: .module)

// String(localized:)
String(localized: "login_subtitle", bundle: .module)
```

`.module` is an auto-generated static property on `Bundle` that points to the correct resource bundle for the Swift Package target. It is generated automatically by SPM when your package has resources.

## Additional Requirement: Package.swift Configuration

Your `Package.swift` must declare `defaultLocalization` for the package to support localized resources:

```swift
let package = Package(
    name: "MyPackage",
    defaultLocalization: "en",  // REQUIRED for localized packages
    platforms: [.iOS(.v16)],
    targets: [
        .target(
            name: "FeatureAuth",
            resources: [.process("Resources")]  // Contains .lproj directories or .xcstrings
        )
    ]
)
```

Without `defaultLocalization: "en"`, SPM does not generate the `Bundle.module` accessor for localization resources.

## Directory Structure

Your localization files must be in the package's resources directory:

```
Sources/FeatureAuth/
├── Resources/
│   ├── en.lproj/
│   │   └── Localizable.strings
│   ├── ru.lproj/
│   │   └── Localizable.strings
│   └── Localizable.xcstrings   // Or use String Catalog
├── Views/
│   └── LoginView.swift
```

## Why This Is Easy to Miss

This is the most common enterprise localization bug. It is silent in English testing because:

1. When the lookup fails (key not found in `Bundle.main`), the system falls back to displaying the key itself
2. If your keys are English text like `"Login"`, the fallback display looks correct in English
3. The bug only surfaces when testing with non-English locales

Using semantic keys like `"login_title"` makes this bug more visible because the raw key is clearly not display text.

## Exposing the Bundle for Consumers

If other modules need to look up strings from your package, expose the bundle:

```swift
public extension Bundle {
    static let featureAuth = Bundle.module
}
```

Then consumers can use:
```swift
String(localized: "login_title", bundle: .featureAuth)
```
