# WCAG Criterion for Text Resizing on iOS

## Primary Criterion: WCAG 1.4.4 Resize Text (Level AA)

**WCAG 1.4.4 Resize Text** is the primary criterion covering text resizing. It requires that text can be resized up to 200% without assistive technology and without loss of content or functionality.

### iOS Implementation

On iOS, this criterion is addressed through **Dynamic Type**, Apple's system-level text scaling feature. Users can adjust text size via:

- Settings > Accessibility > Display & Text Size > Larger Text

Apps that properly support Dynamic Type by using `UIFontMetrics` or Apple's built-in scaled font styles (e.g., `.body`, `.headline`, `.caption`) allow text to resize in response to the user's system preference, satisfying WCAG 1.4.4.

### Related Criterion: WCAG 1.4.12 Text Spacing (Level AA)

**WCAG 1.4.12 Text Spacing** (introduced in WCAG 2.1) is also relevant. It requires that no loss of content or functionality occurs when users override:

- Line height to at least 1.5x the font size
- Letter spacing to at least 0.12x the font size
- Word spacing to at least 0.16x the font size
- Spacing following paragraphs to at least 2x the font size

On iOS, supporting flexible layouts and avoiding fixed-height text containers helps meet this criterion.

## Summary Table

| Criterion | Level | Description |
|-----------|-------|-------------|
| 1.4.4 Resize Text | AA | Text resizable up to 200% without loss of content |
| 1.4.12 Text Spacing | AA | No loss when overriding line/letter/word/paragraph spacing |

## Key iOS APIs

- `UIFontMetrics` — scales custom fonts with Dynamic Type
- `UIFont.preferredFont(forTextStyle:)` — built-in scaled system fonts
- `adjustsFontForContentSizeCategory = true` — enables automatic Dynamic Type updates on labels
