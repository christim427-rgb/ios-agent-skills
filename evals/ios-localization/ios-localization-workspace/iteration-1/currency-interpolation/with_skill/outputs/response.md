String interpolation is the wrong way to display prices. The code `"$\(product.price)"` hardcodes the US dollar sign, its position (prefix), decimal separator (period), and digit grouping — all of which vary by locale.

## The Problem

```swift
let priceText = "$\(product.price)"
```

This produces output like `"$9.99"` or `"$1234.56"`, which is only correct for US locale. Currency formatting varies significantly across locales:

| Locale | Format for $1,234.56 |
|---|---|
| en_US (United States) | $1,234.56 |
| de_DE (Germany) | 1.234,56 $ |
| fr_FR (France) | 1 234,56 $ |
| ja_JP (Japan) | $1,234.56 |
| ar_SA (Saudi Arabia) | US$ ١٬٢٣٤٫٥٦ |

Notice that in Germany and France, the dollar sign comes **after** the number. Germany uses a period for thousands grouping and a comma for the decimal separator — the exact opposite of the US. France uses a space for thousands grouping. Arabic locales use Eastern Arabic numerals.

String interpolation gets all of these wrong for non-US users.

## The Fix

### iOS 15+ (Recommended)

```swift
let priceText = product.price.formatted(.currency(code: "USD"))
```

This automatically formats the price according to the user's locale, handling symbol position, decimal separator, digit grouping, and numeral system correctly.

### Pre-iOS 15

```swift
let formatter = NumberFormatter()
formatter.numberStyle = .currency
formatter.currencyCode = "USD"
let priceText = formatter.string(from: NSNumber(value: product.price))
```

### With Explicit Locale (if needed)

If you need to force a specific locale regardless of user settings:

```swift
let priceText = product.price.formatted(
    .currency(code: "USD").locale(Locale(identifier: "en_US"))
)
```

## Key Points

1. **Never hardcode currency symbols.** The position (prefix vs. suffix), spacing, and even the symbol itself ($ vs. US$ vs. USD) vary by locale.

2. **Never hardcode decimal separators.** In many European countries, the comma is the decimal separator and the period (or space) is the thousands separator.

3. **Always use `NumberFormatter` with `.currency` style or `.formatted(.currency(code:))`** for any monetary values. These APIs handle all locale-specific variations automatically.

4. **Pass the currency code, not the symbol.** Use `"USD"`, `"EUR"`, `"JPY"` — the formatter will determine the correct symbol and placement for the user's locale.
