# Polish vs Russian Plurals -- Why You Cannot Copy the Rules

## Short Answer

No, you should not copy Russian plural rules for Polish. Although both languages have 4 CLDR plural categories (one, few, many, other), the **rules for which numbers fall into which category are different**.

## The Key Difference

The most critical difference is in the **"one"** category:

- **Russian "one"**: any number ending in 1 (except 11). So 1, 21, 31, 41, 51, 101, 121 are all "one".
- **Polish "one"**: **only the integer 1**. Nothing else.

This means the number **21** maps to different categories:

| Number | Russian | Polish |
|--------|---------|--------|
| 1 | one | one |
| 21 | one | few |
| 31 | one | few |
| 101 | one | few |

Wait -- let me correct that. In Polish, 21 actually falls into "few" (2-4 ending, excluding teens) -- actually, let me lay out the Polish rules properly:

## Polish Plural Rules

| Category | Rule | Examples |
|----------|------|----------|
| **one** | exactly 1 | 1 |
| **few** | ends in 2-4, not 12-14 | 2, 3, 4, 22, 23, 24, 32 |
| **many** | everything else (integer) | 0, 5-21, 25-31, 35-41... |
| **other** | fractional numbers | 1.5, 2.7 |

## Russian Plural Rules (for comparison)

| Category | Rule | Examples |
|----------|------|----------|
| **one** | ends in 1, not 11 | 1, 21, 31, 101 |
| **few** | ends in 2-4, not 12-14 | 2, 3, 4, 22, 23, 24 |
| **many** | ends in 0, 5-9, or 11-14 | 0, 5-20, 25-30 |
| **other** | fractional numbers | 1.5, 2.3 |

## Concrete Example

For "files" with the number 21:

- **Russian**: "21 файл" (one form)
- **Polish**: "21 plików" (many form)

## Lesson

Never copy plural logic between languages, even within the same language family. Always consult the CLDR plural rules for each specific language. The number of categories may look the same, but the rules governing which numbers fall into which category can be very different.
