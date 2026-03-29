# Western Arabic Digits for Arabic Locale Users

## The Problem

Your app shows Western Arabic digits (1, 2, 3) for Arabic locale users instead of the Eastern Arabic digits (or "Hindi-Arabic" numerals) they expect: ٠, ١, ٢, ٣, ٤, ٥, ٦, ٧, ٨, ٩.

This typically happens when using `String(format:)` or basic string interpolation, which always outputs Western digits regardless of the user's locale:

```swift
// These always produce Western digits:
let text = String(format: "%d", count)      // "42"
let text = "\(count)"                        // "42"
```

## The Fix

### Option 1: String.localizedStringWithFormat()

```swift
let text = String.localizedStringWithFormat("%d", count)
// Arabic locale: "٤٢"
// English locale: "42"
```

### Option 2: NumberFormatter

```swift
let formatter = NumberFormatter()
formatter.numberStyle = .decimal
let text = formatter.string(from: NSNumber(value: count)) ?? ""
// Respects user's locale for digit system
```

### Option 3: .formatted() (iOS 15+)

```swift
let text = count.formatted()
// Automatically uses locale-appropriate digits
```

## Why It Happens

`String(format:)` is a C-based function that always outputs ASCII digits. It does not consult the user's locale. To get locale-aware digit rendering, you must use one of the locale-aware formatting APIs listed above.

## Note on Arabic Digit Preferences

Not all Arabic-speaking regions prefer Eastern Arabic digits. The Maghreb countries (Morocco, Algeria, Tunisia) typically use Western digits. The system respects the user's actual locale setting, so you do not need to make assumptions -- just use locale-aware formatters and iOS handles it correctly.
