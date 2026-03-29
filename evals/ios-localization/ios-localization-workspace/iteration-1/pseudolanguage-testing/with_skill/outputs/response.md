# Testing iOS Localization Without Translations

Xcode provides built-in **pseudolanguages** that let you test localization quality without needing actual translations. These are available under Edit Scheme -> Options -> Application Language.

## Xcode Pseudolanguages

### 1. Double Length Pseudolanguage
**What it tests:** Text expansion and truncation.

Doubles every localized string to simulate worst-case translation expansion. German averages 30% longer than English, and short strings can expand 3x (e.g., "OK" becomes "Einverstanden" in German).

**What to check:** Look for truncated text, clipped labels, broken layouts, overlapping text, and horizontal scrolling where none should exist.

### 2. Right to Left Pseudolanguage
**What it tests:** RTL layout correctness.

Flips the entire UI to right-to-left without needing Arabic or Hebrew translations. This is the fastest way to find `left`/`right` constraint issues, `.left` text alignment, and directional content that should or should not flip.

**What to check:** Verify constraints use leading/trailing, text alignment adapts correctly, directional icons flip (arrows, chevrons) while non-directional ones (logos) stay put.

### 3. Accented Pseudolanguage
**What it tests:** Whether all strings go through localization.

Adds diacritical marks to English text (e.g., "Settings" becomes "[Sttgs]" with accented characters). Any text that appears without accented characters is hardcoded and not going through the localization system.

**What to check:** Scan every screen for unaccented text — those are hardcoded strings that need to be localized.

### 4. Bounded Pseudolanguage
**What it tests:** Exact string boundaries and truncation.

Wraps every localized string in `[# #]` brackets. This makes it obvious exactly where localized text starts and ends, revealing truncation and clipping.

**What to check:** Look for strings where the `[# #]` markers are clipped or cut off — those containers are too small for the text.

## Launch Argument: -NSShowNonLocalizedStrings YES

Add this launch argument to your scheme:

```
-NSShowNonLocalizedStrings YES
```

This **uppercases any string that missed localization**, making unlocalized text visually obvious in the running app. Any text that appears in ALL CAPS was not found in the String Catalog or `.strings` file.

Set it in: Edit Scheme -> Run -> Arguments -> Arguments Passed On Launch.

## Additional Launch Arguments for Testing

```bash
# Force specific locale without changing device settings
-AppleLocale ru_RU
-AppleLanguages "(ru)"

# Force Buddhist calendar (tests en_US_POSIX handling)
-AppleCalendar buddhist

# Force 12-hour time (tests HH:mm parsing)
-AppleICUForce12HourTime YES
```

## Recommended Testing Workflow

1. Run with **Double Length** — check every screen for truncation
2. Run with **Right to Left** — check every screen for layout issues
3. Run with **Accented** — scan for unaccented text (hardcoded strings)
4. Run with **Bounded** — check for strings that clip `[# #]` markers
5. Run with `-NSShowNonLocalizedStrings YES` — find uppercased unlocalized text
6. Test date/time with Buddhist calendar and 12-hour time launch arguments
7. Test numbers with Arabic locale for Eastern Arabic numerals
8. Test plural forms with the verification number set: `[0, 1, 2, 3, 4, 5, 10, 11, 12, 14, 20, 21, 22, 25, 100, 101, 111, 1.5]`
