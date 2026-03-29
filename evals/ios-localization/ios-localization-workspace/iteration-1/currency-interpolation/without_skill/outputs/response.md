# Currency Display via String Interpolation

## The Problem

```swift
let priceText = "$\(product.price)"
```

This hardcodes the US dollar sign and assumes American number formatting. Currency display varies significantly across locales:

| Locale | $1,234.56 displayed as |
|--------|----------------------|
| US (en_US) | $1,234.56 |
| Germany (de_DE) | 1.234,56 $ |
| France (fr_FR) | 1 234,56 $ |
| Japan (ja_JP) | $1,234.56 |
| Switzerland (de_CH) | $ 1'234.56 |

Differences include:
- **Symbol position**: before or after the number
- **Decimal separator**: period vs comma
- **Grouping separator**: comma, period, space, apostrophe
- **Spacing**: space between symbol and number or not

## The Fix

### iOS 15+ (Recommended)

```swift
let priceText = product.price.formatted(.currency(code: "USD"))
```

This automatically formats the amount according to the user's locale while using the correct currency.

### Pre-iOS 15

```swift
let formatter = NumberFormatter()
formatter.numberStyle = .currency
formatter.currencyCode = "USD"
let priceText = formatter.string(from: NSNumber(value: product.price)) ?? ""
```

### If You Need a Specific Locale

```swift
// Force a specific locale for display (rare)
let priceText = product.price.formatted(
    .currency(code: "EUR").locale(Locale(identifier: "de_DE"))
)
```

## Important

- Always use the actual ISO 4217 currency code (USD, EUR, GBP, JPY, etc.) rather than hardcoding a symbol.
- Let the formatter handle symbol placement, decimal precision, and grouping.
- Different currencies have different decimal place conventions (JPY has 0 decimals, most have 2, some have 3). The formatter handles this automatically.
