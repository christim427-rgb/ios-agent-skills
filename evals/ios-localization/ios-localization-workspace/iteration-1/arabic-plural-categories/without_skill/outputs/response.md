# Arabic Plural Categories

Arabic has the most complex plural system of any commonly supported language. It requires all **6 CLDR plural categories**:

## The Six Categories

| Category | Rule | Example Numbers |
|----------|------|-----------------|
| **zero** | The number 0 | 0 |
| **one** | The number 1 | 1 |
| **two** | The number 2 (dual form) | 2 |
| **few** | Numbers 3-10 and numbers ending in 03-10 | 3, 4, 5, 6, 7, 8, 9, 10, 103, 104 |
| **many** | Numbers 11-99 and numbers ending in 11-99 | 11, 12, 25, 50, 99, 111, 199 |
| **other** | 100, 1000, and other large round numbers; also fractions | 100, 200, 1000, 0.5 |

## The Dual Form

The **"two"** category is particularly noteworthy. Arabic has a grammatical dual form that is specifically and exclusively for the number 2. This is a distinct grammatical construction, not just a variation of plural. For example:

- 1 book = "كتاب واحد" (one form)
- 2 books = "كتابان" (dual form -- two)
- 3 books = "3 كتب" (few form)

## Implementation in .stringsdict

```xml
<key>books_count</key>
<dict>
    <key>NSStringLocalizedFormatKey</key>
    <string>%#@count@</string>
    <key>count</key>
    <dict>
        <key>NSStringFormatSpecTypeKey</key>
        <string>NSStringPluralRuleType</string>
        <key>NSStringFormatValueTypeKey</key>
        <string>lld</string>
        <key>zero</key>
        <string>لا كتب</string>
        <key>one</key>
        <string>كتاب واحد</string>
        <key>two</key>
        <string>كتابان</string>
        <key>few</key>
        <string>%lld كتب</string>
        <key>many</key>
        <string>%lld كتابًا</string>
        <key>other</key>
        <string>%lld كتاب</string>
    </dict>
</dict>
```

## Important Notes

- You must provide **all 6 categories** for Arabic. Omitting any category will cause fallback to the "other" form, which may be grammatically incorrect.
- If you use String Catalogs (Xcode 15+), Xcode will automatically prompt you for all 6 forms when you add Arabic as a language.
- Arabic also uses RTL layout and may use Eastern Arabic numerals (٠١٢٣٤٥٦٧٨٩), which are separate considerations from pluralization.
