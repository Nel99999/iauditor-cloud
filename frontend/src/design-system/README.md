# Design System - v2.0 Operational Management Platform

## Overview

This design system provides a token-driven, theme-able, and maintainable UI foundation for the entire platform.

## Architecture

```
/design-system
├── /tokens              # Design tokens (source of truth)
│   ├── tokens.json      # All design tokens
│   ├── style-dictionary.config.js
│   └── /build           # Generated CSS/JS
├── /theme               # Theme overlays
│   └── light.json       # Light theme overrides
├── /components          # Token-driven components
└── /animations          # Motion utilities
```

## Token System

### Color Philosophy - Dark Mode First

We use **OKLCH color space** for perceptual uniformity and accessibility:

- **Background**: `oklch(18% 0.015 250)` - Deep Space
- **Primary**: `oklch(70% 0.18 230)` - Electric Blue
- **Accent**: `oklch(75% 0.20 145)` - Neon Green
- **Text**: `oklch(98% 0.01 250)` - Soft White

### Usage

```jsx
import tokens from '@/design-system/tokens/build/tokens';

// In components
const styles = {
  backgroundColor: tokens.color.surface.base,
  color: tokens.color.text.primary,
  padding: tokens.spacing['4'],
  borderRadius: tokens.radius.md,
};
```

### CSS Variables

```css
/* Import in your CSS */
@import '@/design-system/tokens/build/tokens.css';

/* Use variables */
.button {
  background-color: var(--color-brand-primary);
  padding: var(--spacing-4);
  border-radius: var(--radius-md);
}
```

## Building Tokens

```bash
cd design-system/tokens
npm run build
```

This generates:
- `build/tokens.css` - CSS variables
- `build/tokens.js` - JavaScript constants

## Changing the Design

### Update Colors (2 minutes)

1. Edit `tokens/tokens.json`
2. Change the `value` of any color
3. Run `npm run build`
4. Entire app updates automatically

### Add a New Component

1. Create component in `/components`
2. Use tokens for all styling
3. Export from `index.js`
4. Use anywhere in the app

## Theme Switching

```jsx
// Toggle between dark and light
setTheme('light'); // or 'dark'
```

Theme overlays automatically replace token values.

## Guidelines

### ✅ DO
- Use tokens for ALL styling
- Build semantic components
- Test dark AND light modes
- Ensure accessibility (WCAG AA)

### ❌ DON'T
- Hardcode colors, spacing, or sizes
- Bypass the token system
- Create one-off styles
- Ignore accessibility

## Benefits

1. **Consistency**: Single source of truth
2. **Maintainability**: Change once, update everywhere
3. **Themeable**: Switch themes instantly
4. **Accessible**: Built-in contrast standards
5. **Scalable**: Easy to add new components
6. **Future-proof**: Platform-agnostic tokens

## Questions?

Refer to the main blueprint: `/app/HYBRID_UI_UX_BLUEPRINT.md`
