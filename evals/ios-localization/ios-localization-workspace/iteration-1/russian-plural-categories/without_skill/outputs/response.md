# Russian Plural Categories

## The Problem

Your stringsdict only has two categories:

```
one: "%lld файл"
other: "%lld файлов"
```

This is **incorrect** for Russian. Russian requires **4 plural categories**: `one`, `few`, `many`, and `other`.

## Correct Russian Plural Forms

| Category | Rule | Example Numbers | Form |
|----------|------|-----------------|------|
| **one** | ends in 1, but not 11 | 1, 21, 31, 101, 121 | `%lld файл` |
| **few** | ends in 2-4, but not 12-14 | 2, 3, 4, 22, 23, 24, 32 | `%lld файла` |
| **many** | ends in 0, 5-9, or 11-14 | 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 20, 25 | `%lld файлов` |
| **other** | fractional numbers | 1.5, 2.3 | `%lld файла` |

## The Rules in Detail

- **"one"** applies when the last digit is 1, **except** when the last two digits are 11. So 1, 21, 31, 41, 51, 101, 121 are "one", but 11, 111, 211 are NOT (those are "many").
- **"few"** applies when the last digit is 2, 3, or 4, **except** when the last two digits are 12, 13, or 14. So 2, 3, 4, 22, 23, 24, 102 are "few", but 12, 13, 14, 112 are NOT.
- **"many"** applies to 0, and numbers ending in 5-9, and the "teen" exceptions (11-14). So 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25 are "many".
- **"other"** is for fractional/decimal numbers.

## Verification Test Numbers

Test your implementation with these numbers to cover all categories:

- 1 (one: "1 файл")
- 2 (few: "2 файла")
- 5 (many: "5 файлов")
- 11 (many: "11 файлов")
- 21 (one: "21 файл")
- 22 (few: "22 файла")
- 0 (many: "0 файлов")
- 101 (one: "101 файл")
- 111 (many: "111 файлов")

## Corrected .stringsdict

```xml
<key>files_count</key>
<dict>
    <key>NSStringLocalizedFormatKey</key>
    <string>%#@count@</string>
    <key>count</key>
    <dict>
        <key>NSStringFormatSpecTypeKey</key>
        <string>NSStringPluralRuleType</string>
        <key>NSStringFormatValueTypeKey</key>
        <string>lld</string>
        <key>one</key>
        <string>%lld файл</string>
        <key>few</key>
        <string>%lld файла</string>
        <key>many</key>
        <string>%lld файлов</string>
        <key>other</key>
        <string>%lld файла</string>
    </dict>
</dict>
```
