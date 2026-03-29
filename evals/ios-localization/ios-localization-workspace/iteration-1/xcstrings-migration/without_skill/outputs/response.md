# Migrating from .strings/.stringsdict to String Catalogs

## Step-by-Step Migration

### 1. Use Xcode's Built-in Migration

Xcode provides a built-in migration tool:

1. In the Project Navigator, right-click on your `.strings` file (e.g., `Localizable.strings`)
2. Select **"Migrate to String Catalog..."**
3. Xcode will create a new `.xcstrings` file containing all your existing keys, translations, and plural definitions from the corresponding `.stringsdict` file

### 2. Verify the Migration

After migration:
- Open the new `.xcstrings` file in Xcode's String Catalog editor
- Verify that all keys are present
- Check that plural variations were migrated correctly
- Confirm that all language translations are intact

### 3. Remove the Old Files

Once you've verified the migration, remove the old `.strings` and `.stringsdict` files from your project.

## Important Warnings

### .strings and .xcstrings Cannot Coexist for the Same Table

You **cannot** have both `Localizable.strings` and `Localizable.xcstrings` in the same project. They use the same table name (`"Localizable"`) and will conflict. The migration must be **complete** for each table -- you either use the old `.strings` format or the new `.xcstrings` format, not both.

### Migrate One Table at a Time

If you have multiple string tables (e.g., `Localizable.strings`, `Errors.strings`, `Settings.strings`), you can migrate them one at a time. Each table must be fully migrated before moving to the next.

### Swift Package Considerations

If your project includes Swift Packages with their own localization files, those need to be migrated separately within each package.

## Benefits of Migrating

- **Visual editor**: Xcode provides a table-based editor for String Catalogs
- **Auto-extraction**: Xcode automatically discovers new strings from your code and adds them to the catalog
- **Translation state tracking**: Each key shows whether it's translated, needs review, or is new
- **Single file**: All languages for a table are in one file, rather than spread across `.lproj` directories

## Minimum Requirements

- Xcode 15 or later
- iOS 16+ / macOS 13+ for runtime support (older deployment targets will use a backward-compatible format)
