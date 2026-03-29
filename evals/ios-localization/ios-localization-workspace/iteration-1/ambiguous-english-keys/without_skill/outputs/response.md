# Handling Ambiguous English Words in Localization

## The Problem

The English word "Water" has two completely different meanings in your app:

1. **Menu context**: Water as a beverage (noun -- the drink)
2. **Garden context**: Water as an action (verb -- to water the plants)

In many languages these are entirely different words. For example, in Spanish: "agua" (the drink) vs. "regar" (to water plants). If you use a single localization key, translators can only provide one translation, and it will be wrong in one context.

## Recommended Approach

Use separate keys with dot-notation that reflects the context, and provide translator comments:

```swift
// Menu feature - "Water" as a beverage
String(localized: "menu.drink.water",
       comment: "Name of the beverage 'water' in the drinks menu")

// Garden feature - "Water" as an action
String(localized: "garden.action.water",
       comment: "Button label for the action of watering a plant in the garden feature")
```

## Key Principles

1. **Use semantic, dot-notation keys** -- not the English word itself as the key. Keys like `"menu.drink.water"` and `"garden.action.water"` make the context clear in both code and translation files.

2. **Always provide different translator comments** for each context. Even if the English text is the same, the comments help translators understand what they are translating.

3. **Never assume two identical English words will share a translation.** English is particularly ambiguous with words that serve as both nouns and verbs. Other languages almost always distinguish them.
