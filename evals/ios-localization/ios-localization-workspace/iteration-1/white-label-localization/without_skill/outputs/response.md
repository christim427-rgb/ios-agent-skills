# White-Label App Localization Architecture

## Problem

You have 3 brand variants that share most UI strings but need different marketing/brand-specific text. You need an architecture that avoids duplicating the shared strings while allowing per-brand customization.

## Recommended Architecture

### Split String Catalogs: Shared + Per-Brand

Create a layered localization structure:

```
Localization/
  SharedUI.xcstrings          # Common UI strings (buttons, labels, errors)
  BrandMarketing.xcstrings    # Brand-specific marketing text (overridden per brand)
```

- **SharedUI.xcstrings**: Contains strings like "Save", "Cancel", "Error occurred", navigation labels, etc. These are identical across all brands.
- **BrandMarketing.xcstrings**: Contains brand name, tagline, onboarding text, marketing copy, etc. These differ per brand.

### Approach 1: Multiple Xcode Targets

Create a separate Xcode target for each brand. Each target includes:
- The shared string catalog (same for all)
- Its own brand-specific string catalog

```
Targets/
  BrandA/
    BrandAMarketing.xcstrings
  BrandB/
    BrandBMarketing.xcstrings
  BrandC/
    BrandCMarketing.xcstrings
```

Each target links to the same shared code and shared strings but includes its own brand catalog. This is straightforward and works well at build time.

### Approach 2: Runtime Bundle Loading

For more flexibility (e.g., switching brands without rebuilding), load brand-specific strings from a bundle at runtime:

```swift
class BrandManager {
    static let shared = BrandManager()

    private var brandBundle: Bundle

    init() {
        // Determine brand from config, server, or build setting
        let brandName = Configuration.currentBrand // "BrandA", "BrandB", etc.
        let bundlePath = Bundle.main.path(forResource: brandName, ofType: "bundle")!
        brandBundle = Bundle(path: bundlePath)!
    }

    func localizedString(_ key: String, comment: String) -> String {
        // First check brand bundle, fall back to main bundle
        let brandValue = NSLocalizedString(key, bundle: brandBundle, comment: comment)
        if brandValue != key {
            return brandValue
        }
        return NSLocalizedString(key, comment: comment)
    }
}
```

This approach checks the brand-specific bundle first and falls back to the shared strings if the key isn't found.

### Approach 3: OTA (Over-the-Air) Localization

For apps that need to update brand text without an app update:
- Store brand-specific strings on a server
- Download them at launch and cache locally
- Fall back to bundled strings if the network is unavailable

This is useful for A/B testing marketing copy or updating brand messaging without an App Store release.

## Recommended Structure

For most teams, the **multiple targets** approach combined with a **shared catalog** is the simplest and most maintainable:

```swift
// Shared UI string
Text("save_button", tableName: "SharedUI")

// Brand-specific string
Text("welcome_tagline", tableName: "BrandMarketing")
```

Each target includes `SharedUI.xcstrings` (identical) and its own `BrandMarketing.xcstrings` (unique per brand).

## Summary

| Approach | Best For | Complexity |
|----------|----------|------------|
| Multiple targets | Build-time brand selection | Low |
| Runtime bundle | Dynamic brand switching | Medium |
| OTA localization | Server-controlled updates | High |

Choose the approach that matches your deployment model. Most white-label apps start with multiple targets and add runtime flexibility later if needed.
