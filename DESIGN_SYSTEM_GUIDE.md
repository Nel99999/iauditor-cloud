# Design System Guide

## Overview

The v2.0 Operational Management Platform uses a comprehensive, token-driven design system built with Style Dictionary. This guide explains how to use the design system components and patterns.

## Table of Contents

1. [Design Tokens](#design-tokens)
2. [Components](#components)
3. [Theme System](#theme-system)
4. [Best Practices](#best-practices)
5. [Accessibility](#accessibility)

---

## Design Tokens

### What are Design Tokens?

Design tokens are the visual design atoms of the design system. They're platform-agnostic values (colors, spacing, typography) that ensure consistency across the application.

### Token Categories

#### Colors
```css
var(--color-primary)        /* Primary brand color */
var(--color-secondary)      /* Secondary color */
var(--color-success)        /* Success states */
var(--color-danger)         /* Error/danger states */
var(--color-warning)        /* Warning states */
var(--color-text-primary)   /* Primary text */
var(--color-text-secondary) /* Secondary text */
var(--color-surface)        /* Surface background */
```

#### Spacing
```css
var(--spacing-xs)   /* 4px */
var(--spacing-sm)   /* 8px */
var(--spacing-md)   /* 16px */
var(--spacing-lg)   /* 24px */
var(--spacing-xl)   /* 32px */
```

#### Typography
```css
var(--font-size-xs)   /* 12px */
var(--font-size-sm)   /* 14px */
var(--font-size-base) /* 16px */
var(--font-size-lg)   /* 18px */
var(--font-size-xl)   /* 20px */
```

#### Border Radius
```css
var(--radius-sm)  /* 4px */
var(--radius-md)  /* 8px */
var(--radius-lg)  /* 12px */
var(--radius-xl)  /* 24px */
```

### Using Tokens

Always use design tokens instead of hardcoded values:

```jsx
// ❌ Bad
<div style={{ padding: '16px', color: '#3b82f6' }}>

// ✅ Good
<div style={{ padding: 'var(--spacing-md)', color: 'var(--color-primary)' }}>
```

### Modifying Tokens

1. Edit `/frontend/src/design-system/tokens/tokens.json`
2. Run `npm run tokens:build`
3. Tokens are compiled to `/frontend/src/design-system/tokens/base.css`

---

## Components

### Core Components

#### Button

Versatile button component with multiple variants.

```jsx
import { Button } from '@/design-system/components';

// Basic usage
<Button variant="primary">Click me</Button>

// With icon
<Button variant="secondary" icon={<Plus size={20} />}>Create</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// States
<Button disabled>Disabled</Button>
<Button loading>Loading</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg'
- `icon`: React node (icon component)
- `disabled`: boolean
- `loading`: boolean
- `fullWidth`: boolean

#### Card & GlassCard

Containers for grouping content.

```jsx
import { Card, GlassCard } from '@/design-system/components';

// Basic card
<Card padding="lg">
  <h3>Title</h3>
  <p>Content</p>
</Card>

// Glassmorphism card
<GlassCard hover blur="lg">
  <h3>Glass Effect</h3>
</GlassCard>
```

#### Input

Form input with multiple types and states.

```jsx
import { Input } from '@/design-system/components';

<Input
  placeholder="Enter text"
  icon={<Mail size={18} />}
  size="lg"
  error={!!errors.email}
/>
```

#### BottomSheet

Mobile-optimized modal that slides from bottom.

```jsx
import { BottomSheet, useBottomSheet } from '@/design-system/components';

const { isOpen, open, close } = useBottomSheet();

<Button onClick={open}>Open Sheet</Button>
<BottomSheet isOpen={isOpen} onClose={close} title="Details" snapPoint="half">
  <p>Content here</p>
</BottomSheet>
```

**Snap Points:**
- `peek`: 25% height
- `half`: 50% height
- `full`: 90% height

**Features:**
- Swipe gestures (down to close, up to expand)
- Backdrop tap to close
- ESC key to close
- Body scroll lock
- Smooth spring animations

#### FAB (Floating Action Button)

Floating button for primary actions.

```jsx
import { FAB, FABIcons } from '@/design-system/components';

// Simple FAB
<FAB
  variant="simple"
  position="bottom-right"
  icon={<FABIcons.Plus />}
  onClick={handleCreate}
/>

// Speed Dial (multiple actions)
<FAB
  variant="speedDial"
  position="bottom-right"
  icon={<FABIcons.Plus />}
  actions={[
    { icon: <FABIcons.Task />, label: 'New Task', onClick: createTask, color: 'primary' },
    { icon: <FABIcons.Inspection />, label: 'New Inspection', onClick: createInspection },
  ]}
/>
```

**Positions:**
- `bottom-right` (default)
- `bottom-center`
- `bottom-left`

**Colors:**
- `primary`, `secondary`, `success`, `danger`

---

## Theme System

### Dark Mode First

The application uses a "Dark Mode First" approach with seamless theme switching.

### Using ThemeContext

```jsx
import { useTheme } from '@/contexts/ThemeContext';

const { theme, toggleTheme } = useTheme();

<button onClick={toggleTheme}>
  Current: {theme}
</button>
```

### Theme-Aware Styling

Use CSS variables that automatically adapt:

```css
.my-component {
  background: var(--color-surface);
  color: var(--color-text-primary);
}

/* Automatically changes in dark mode! */
```

---

## Best Practices

### Component Composition

✅ **Do:**
- Use semantic components
- Compose smaller components
- Follow single responsibility
- Use design tokens

❌ **Don't:**
- Hardcode colors/spacing
- Create monolithic components
- Mix concerns
- Ignore responsive design

### Performance

- Lazy load components when possible
- Use `React.memo` for expensive renders
- Optimize images and assets
- Minimize bundle size

### Responsive Design

Mobile-first approach:

```css
/* Mobile first (default) */
.component { font-size: 14px; }

/* Tablet */
@media (min-width: 768px) {
  .component { font-size: 16px; }
}

/* Desktop */
@media (min-width: 1024px) {
  .component { font-size: 18px; }
}
```

### Naming Conventions

- Components: PascalCase (`Button`, `BottomSheet`)
- Props: camelCase (`onClick`, `isOpen`)
- CSS classes: kebab-case (`bottom-sheet-content`)
- Files: Match component name (`Button.jsx`, `Button.css`)

---

## Accessibility

### ARIA Labels

Always provide accessible labels:

```jsx
<Button aria-label="Create new task" icon={<Plus />} />
<BottomSheet aria-modal="true" role="dialog" />
```

### Keyboard Navigation

- All interactive elements are keyboard accessible
- Focus indicators are visible
- Tab order is logical
- ESC closes modals

### Focus Management

```jsx
// Auto-focus on open
useEffect(() => {
  if (isOpen) {
    inputRef.current?.focus();
  }
}, [isOpen]);
```

### Screen Readers

Use semantic HTML and ARIA:

```jsx
<nav aria-label="Main navigation">
<button aria-expanded={isOpen}>
<div role="status" aria-live="polite">
```

---

## Additional Resources

- [Storybook](http://localhost:6006) - Component showcase
- [Component API Reference](./COMPONENT_API.md)
- [Mobile UX Guide](./MOBILE_UX_GUIDE.md)
- [Style Dictionary](https://amzn.github.io/style-dictionary/)
- [Framer Motion](https://www.framer.com/motion/)

---

## Contributing

When adding new components:

1. Use design tokens
2. Create Storybook stories
3. Add JSDoc comments
4. Ensure accessibility
5. Test on mobile devices
6. Update this documentation

---

**Questions?** Check the Storybook or reach out to the design system team.
