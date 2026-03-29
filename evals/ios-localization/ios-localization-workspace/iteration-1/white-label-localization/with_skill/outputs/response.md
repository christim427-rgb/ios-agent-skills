# White-Label App Localization Architecture

For a white-label app with 3 brand variants sharing most UI strings but needing different marketing text, the key architectural decision is how to separate shared vs. brand-specific localization. There are three main approaches, and the best choice depends on your build and deployment workflow.

## Shared + Brand-Specific Catalog Split

Regardless of which architecture you choose, the fundamental pattern is the same: **shared catalog for common UI strings** and **per-brand catalogs for marketing/branded text**.

```
MyApp/
├── Shared/SharedLocalizable.xcstrings       # Common UI: "Cancel", "OK", "Settings"
├── BrandA/BrandLocalizable.xcstrings        # Brand A: welcome text, marketing copy
├── BrandB/BrandLocalizable.xcstrings        # Brand B: welcome text, marketing copy
└── BrandC/BrandLocalizable.xcstrings        # Brand C: welcome text, marketing copy
```

## Architecture 1: Multiple Xcode Targets

Each brand is a separate Xcode target with its own localization files. The shared strings are in a shared folder included by all targets.

```
MyApp/
├── BrandA/Localizable.xcstrings     # Target: BrandA
├── BrandB/Localizable.xcstrings     # Target: BrandB
├── BrandC/Localizable.xcstrings     # Target: BrandC
└── Shared/SharedLocalizable.xcstrings  # All targets
```

**Pros:** Simple, clear separation at build time, no runtime logic needed.
**Cons:** Requires rebuilding for each brand, cannot switch brands dynamically.

## Architecture 2: Runtime Bundle Loading (BrandManager)

A `BrandManager` singleton loads the appropriate brand bundle at runtime. This is the most flexible approach and allows dynamic brand switching:

```swift
class BrandManager {
    static let shared = BrandManager()
    private(set) var bundle: Bundle

    init() {
        bundle = Bundle.main  // Default fallback
    }

    func configure(brand: Brand) {
        let path = Bundle.main.path(forResource: brand.bundleName, ofType: "bundle")!
        bundle = Bundle(path: path)!
    }
}

// Usage throughout the app
String(localized: "welcome_message", bundle: BrandManager.shared.bundle)

// SwiftUI
Text("welcome_title", bundle: BrandManager.shared.bundle)
```

Each brand's strings are packaged in a separate `.bundle` directory. At app launch, the `BrandManager` is configured with the appropriate brand, and all brand-specific string lookups go through its bundle. Shared UI strings can remain in the main bundle.

**Pros:** Single binary for all brands, can switch brands at runtime, easy A/B testing.
**Cons:** All brand bundles are in the binary (larger app size), requires consistent use of BrandManager for brand strings.

## Architecture 3: OTA Localization (Lokalise, Phrase, Crowdin)

Translations are downloaded from a remote service at runtime and stored in a custom bundle. The app ships with compiled default strings and fetches updates over the network.

**Pros:** Update translations without app store release, different brands can be configured server-side.
**Cons:** Network dependency, requires offline fallback logic, more complex caching.

## Recommendation

For 3 brand variants, **Runtime Bundle Loading with a BrandManager** is typically the best balance. It keeps a single codebase and binary while cleanly separating brand-specific text. Use the shared catalog for all common UI strings (buttons, navigation, errors) and per-brand bundles for marketing copy, onboarding text, legal disclaimers, and any brand-specific terminology.

If you need to update translations without an app release, combine the BrandManager approach with an OTA service — use OTA for brand-specific text and compiled bundles for stable UI strings.
