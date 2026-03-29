# Testing Localization Without Actual Translations

## Xcode Pseudolanguages

Xcode provides built-in pseudolanguages specifically designed to test localization issues. You can enable them in your scheme settings:

1. **Edit Scheme** > **Run** > **Options**
2. Under **Application Language**, select one of the pseudolanguages

### Available Pseudolanguages

#### 1. Double Length Pseudolanguage
- **What it does**: Doubles the length of every localized string
- **What it tests**: Text truncation, layout overflow, and UI elements that can't accommodate longer translations (German, Finnish, etc. are often 30-50% longer than English)
- **Example**: "Settings" becomes "Settings Settings"

#### 2. Right to Left Pseudolanguage
- **What it does**: Forces the entire UI into RTL layout mode
- **What it tests**: Whether your layout properly mirrors for RTL languages like Arabic and Hebrew. Catches hardcoded left/right constraints, incorrect text alignment, and directional icons that should flip.

#### 3. Accented Pseudolanguage
- **What it does**: Replaces ASCII characters with accented versions (e.g., "Settings" becomes "[Seettiinngs]")
- **What it tests**: Identifies hardcoded strings that were NOT localized. Localized strings will appear with accents; any string still showing normal ASCII text is hardcoded and was missed.

#### 4. Bounded String Pseudolanguage
- **What it does**: Wraps localized strings in brackets (e.g., "[Settings]")
- **What it tests**: Similar to Accented -- helps visually identify which strings are going through the localization system and which are hardcoded.

## Launch Arguments for Testing

### Show Non-Localized Strings

Add the launch argument `-NSShowNonLocalizedStrings YES` to your scheme:

1. **Edit Scheme** > **Run** > **Arguments**
2. Add `-NSShowNonLocalizedStrings YES` to "Arguments Passed On Launch"

This causes any string that fails localization lookup to appear in **UPPERCASE** in the UI, making it easy to spot strings that are missing from your localization files.

### Force a Specific Locale

You can force the app to run in a specific locale without changing device settings:

```
-AppleLanguages (de)
-AppleLocale de_DE
```

## Testing Checklist

1. Run with **Double Length** to check for truncation
2. Run with **Right to Left** to check layout mirroring
3. Run with **Accented** to find any hardcoded strings
4. Add **-NSShowNonLocalizedStrings YES** to catch missing keys
5. Test with actual target languages once translations are available
