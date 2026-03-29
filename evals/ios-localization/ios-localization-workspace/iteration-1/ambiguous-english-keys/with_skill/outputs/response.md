The word "Water" is a classic example of why you should never use English text as the localization key. In English, "Water" can be both a noun (something to drink) and a verb (to water plants). Many languages use completely different words for these two meanings:

- **Spanish:** "Agua" (drink) vs. "Regar" (to water)
- **German:** "Wasser" (drink) vs. "Gießen" (to water)
- **French:** "Eau" (drink) vs. "Arroser" (to water)

If you use `"Water"` as the key for both, a translator only sees one key and must pick one translation — leaving the other context broken.

## The Fix: Semantic Dot-Notation Keys with Context Comments

Use separate, semantic keys for each meaning, and provide detailed translator comments:

```swift
// Menu feature — "Water" as a beverage
String(localized: "menu.drink.water",
       defaultValue: "Water",
       comment: "Name of water as a beverage option in the drink menu")

// Garden feature — "Water" as an action
String(localized: "garden.action.water",
       defaultValue: "Water",
       comment: "Button label for the action of watering plants in the garden feature")
```

In SwiftUI:

```swift
// Menu
Text("menu.drink.water")  // With comment in String Catalog: "Name of water as a beverage option"

// Garden
Text("garden.action.water")  // With comment in String Catalog: "Button to water plants"
```

## Why This Matters

1. **Separate keys** ensure each context gets its own translation entry. Translators see two distinct keys and can provide the correct translation for each.

2. **Semantic dot-notation keys** (like `menu.drink.water` and `garden.action.water`) make the context immediately clear from the key name alone, avoiding the ambiguity of using the English word directly.

3. **Translator comments** are essential for disambiguation. Even with semantic keys, a translator benefits from knowing exactly where the string appears and what it means. Comments should describe the UI context, the part of the app, and the intended meaning. Never use empty comments (`comment: ""`).

This pattern applies broadly: words like "Post" (noun vs. verb), "Order" (noun vs. verb), "Book" (noun vs. verb), "Set" (noun vs. verb), and "Close" (adjective vs. verb) all need separate keys with distinct comments when used in different contexts.
