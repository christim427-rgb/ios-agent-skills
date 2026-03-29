# Validating a Large .xcstrings File

With 500+ keys, manual inspection is impractical. Use programmatic validation to check completeness and correctness.

## Automated Validation with xcstrings_tool.py

The recommended approach is to use the bundled `xcstrings_tool.py` script:

```bash
# Validate for missing plurals, empty translations, stale entries
python3 scripts/xcstrings_tool.py validate path/to/Localizable.xcstrings
```

This checks for:
- **Missing translations** — keys with state `"new"` (no translation provided yet)
- **Stale entries** — keys with state `"stale"` (no longer found in source code, likely removed)
- **Empty translation values** — keys that have a translation entry but the value is blank
- **Mismatched format specifiers** — source string has `%1$@` but translation has `%@` or different specifier count

## Auditing Plural Completeness Per Language

This is the most critical check. Each language requires specific CLDR plural categories, and missing categories produce silently wrong output:

```bash
# Audit plural completeness for Russian (needs one/few/many/other)
python3 scripts/xcstrings_tool.py audit-plurals path/to/Localizable.xcstrings --lang ru

# Audit for Arabic (needs zero/one/two/few/many/other — all 6)
python3 scripts/xcstrings_tool.py audit-plurals path/to/Localizable.xcstrings --lang ar

# Audit for Polish (needs one/few/many/other — different rules from Russian!)
python3 scripts/xcstrings_tool.py audit-plurals path/to/Localizable.xcstrings --lang pl
```

This verifies that every key with plural variations has all CLDR-required categories for that language. For example, if a Russian entry only has `one` and `other`, the audit will flag the missing `few` and `many` categories.

## Export Translation Status Report

For an overview of completion percentage across all languages:

```bash
python3 scripts/xcstrings_tool.py status path/to/Localizable.xcstrings
```

## What to Look For

1. **State `"new"`** — Key has no translation yet. These will show the source language text (or the key itself) to users of that language.
2. **State `"stale"`** — Key was removed from source code. These can be cleaned up to reduce file size.
3. **Empty values** — Translation entry exists but the string is empty. This can cause blank UI.
4. **Missing plural categories** — A Russian entry with only `one`/`other` is broken for numbers like 2, 3, 4, 22, 23 (which need `few`) and 0, 5-20, 25-30 (which need `many`).
5. **Mismatched format specifiers** — Source has `%1$@ invited %2$@` but translation has only `%@` or different positional arguments.

## Manual Xcode Approach

If you prefer a visual approach, open the `.xcstrings` file in Xcode's String Catalog editor. It shows a progress bar per language and highlights untranslated keys. However, it does not automatically validate CLDR plural completeness — the programmatic approach is more thorough for that.
