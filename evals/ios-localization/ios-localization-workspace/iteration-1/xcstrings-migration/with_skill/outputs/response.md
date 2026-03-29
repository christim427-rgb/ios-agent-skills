# Migrating from .strings/.stringsdict to String Catalogs

Xcode provides a built-in migration tool that handles the conversion for you.

## Migration Steps

### 1. Use Xcode's Built-In Migration

In the Project Navigator, right-click your `.strings` file and select **"Migrate to String Catalog"**. Xcode will:

- Create a new `.xcstrings` file with the same table name
- Import all existing keys, values, and translations
- Convert `.stringsdict` plural rules into String Catalog plural variations
- Set the extraction state to `"migrated"` for imported entries
- Remove the original `.strings` and `.stringsdict` files

### 2. Verify the Migration

After migration:
- Open the new `.xcstrings` file in Xcode's String Catalog editor
- Verify all languages appear with their translations
- Check that plural variations migrated correctly (especially for Slavic and Arabic languages)
- Run `python3 scripts/xcstrings_tool.py validate` to catch any issues

### 3. Build and Test

Build the project to trigger String Catalog extraction. Xcode will identify any new strings in source code and add them to the catalog.

## Critical Constraints

### .strings and .xcstrings CANNOT Coexist with the Same Table Name

This is the most important constraint: you cannot have both `Localizable.strings` and `Localizable.xcstrings` in the same target. The build system will not know which to use, and one will silently shadow the other.

**Migration must be complete per table.** You cannot partially migrate — once you create `Localizable.xcstrings`, the old `Localizable.strings` and `Localizable.stringsdict` must be removed entirely for that table name.

### Migrate One Table at a Time

If your project uses multiple tables (e.g., `Localizable`, `InfoPlist`, `Errors`), you can migrate them one at a time. Each table is independent.

### .stringsdict May Still Be Needed

There is one edge case where `.stringsdict` remains necessary even after migration: **pluralization without a visible number** (e.g., showing "Day"/"Days" without displaying the count). String Catalogs require the number to appear in the output. For this specific case, keep a `.stringsdict` file with a different table name.

## After Migration

- New strings added in source code will be automatically extracted to the String Catalog on build
- Use Xcode's visual editor to manage translations and track completion progress
- String Catalog entries show translation states: `new`, `needs_review`, `translated`
- Plural variations are managed per-language with Xcode automatically showing the required CLDR categories
