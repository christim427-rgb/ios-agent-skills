# Validating a Large .xcstrings File

## Approaches for Checking Completeness

### 1. Xcode's Built-in String Catalog Editor

Xcode's String Catalog editor shows the translation state for each key:
- **Green checkmark**: Translated
- **Yellow warning**: Needs review or is stale
- **"New" badge**: Not yet translated

However, with 500+ keys, manually scrolling through the editor is impractical.

### 2. Programmatic Validation

Since `.xcstrings` files are JSON, you can write a script to parse and validate them. Here is an approach using a Python script:

```python
import json
import sys

with open("Localizable.xcstrings", "r") as f:
    catalog = json.load(f)

strings = catalog.get("strings", {})
source_language = catalog.get("sourceLanguage", "en")

missing = {}
empty = {}
stale = {}

for key, value in strings.items():
    localizations = value.get("localizations", {})
    for lang in ["de", "fr", "ja", "ru"]:  # your target languages
        if lang not in localizations:
            missing.setdefault(lang, []).append(key)
        else:
            loc = localizations[lang]
            state = loc.get("stringUnit", {}).get("state", "")
            val = loc.get("stringUnit", {}).get("value", "")
            if state == "new":
                stale.setdefault(lang, []).append(key)
            if val == "":
                empty.setdefault(lang, []).append(key)

# Report
for lang in ["de", "fr", "ja", "ru"]:
    print(f"\n--- {lang} ---")
    print(f"  Missing: {len(missing.get(lang, []))}")
    print(f"  Empty: {len(empty.get(lang, []))}")
    print(f"  Stale (state=new): {len(stale.get(lang, []))}")
```

### 3. Check Plural Completeness

For languages with complex plural rules, you also need to verify that all required plural categories are present. For example:
- **Russian** needs: one, few, many, other
- **Arabic** needs: zero, one, two, few, many, other
- **English** needs: one, other

You can extend the script to check for plural entries and verify the correct categories exist per language based on CLDR rules.

### 4. Xcode Build Warnings

Xcode will generate warnings for missing translations during build time. You can turn these into errors in your build settings to catch issues in CI:

- Check for build warnings related to "Missing translation" in your CI pipeline.

### 5. Export for Review

You can export localizations using:

```bash
xcodebuild -exportLocalizations -localizationPath ./exports -project MyApp.xcodeproj
```

This creates XLIFF files that translation tools can validate for completeness.

## Summary

For a 500+ key catalog, a programmatic approach (parsing the JSON) is the most reliable way to check for missing translations, empty values, stale entries (`state: "new"`), and incomplete plural forms across all target languages.
