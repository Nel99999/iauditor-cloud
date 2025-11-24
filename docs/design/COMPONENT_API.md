# Component API Reference

Complete API documentation for all design system components.

## Table of Contents

- [Button](#button)
- [Card & GlassCard](#card--glasscard)
- [Input](#input)
- [BottomSheet](#bottomsheet)
- [FAB](#fab)
- [ModernTable](#moderntable)
- [Spinner](#spinner)
- [Toast](#toast)

---

## Button

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'ghost' \| 'danger'` | `'primary'` | Button style variant |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Button size |
| `icon` | `ReactNode` | `undefined` | Icon component to display |
| `disabled` | `boolean` | `false` | Disabled state |
| `loading` | `boolean` | `false` | Loading state with spinner |
| `fullWidth` | `boolean` | `false` | Full width button |
| `onClick` | `() => void` | `undefined` | Click handler |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | HTML button type |

### Usage

```jsx
<Button
  variant="primary"
  size="md"
  icon={<Plus size={20} />}
  onClick={handleClick}
>
  Create
</Button>
```

---

## Card & GlassCard

### Card Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `padding` | `'sm' \| 'md' \| 'lg'` | `'md'` | Internal padding |
| `className` | `string` | `''` | Additional CSS classes |
| `children` | `ReactNode` | - | Card content |

### GlassCard Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `padding` | `'sm' \| 'md' \| 'lg'` | `'md'` | Internal padding |
| `hover` | `boolean` | `false` | Enable hover effect |
| `blur` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Backdrop blur amount |
| `className` | `string` | `''` | Additional CSS classes |
| `children` | `ReactNode` | - | Card content |

---

## Input

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Input size |
| `icon` | `ReactNode` | `undefined` | Left icon |
| `error` | `boolean` | `false` | Error state |
| `disabled` | `boolean` | `false` | Disabled state |
| `type` | `string` | `'text'` | HTML input type |
| `placeholder` | `string` | `''` | Placeholder text |
| `value` | `string` | - | Input value (controlled) |
| `onChange` | `(e) => void` | - | Change handler |

---

## BottomSheet

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `isOpen` | `boolean` | `false` | Controls visibility |
| `onClose` | `() => void` | - | Close callback |
| `snapPoint` | `'peek' \| 'half' \| 'full'` | `'half'` | Initial height |
| `title` | `string` | `undefined` | Optional title |
| `showDragHandle` | `boolean` | `true` | Show drag handle |
| `enableSwipe` | `boolean` | `true` | Enable swipe gestures |
| `children` | `ReactNode` | - | Content |

### Hooks

#### useBottomSheet

```jsx
const {
  isOpen,      // boolean
  snapPoint,   // 'peek' | 'half' | 'full'
  open,        // (snapPoint?) => void
  close,       // () => void
  toggle,      // (snapPoint?) => void
  setSnapPoint // (snapPoint) => void
} = useBottomSheet(initialIsOpen, initialSnapPoint);
```

---

## FAB

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'simple' \| 'speedDial'` | `'simple'` | FAB variant |
| `position` | `'bottom-right' \| 'bottom-center' \| 'bottom-left'` | `'bottom-right'` | Position |
| `icon` | `ReactNode` | - | Icon component |
| `label` | `string` | `'Action'` | Accessible label |
| `color` | `'primary' \| 'secondary' \| 'success' \| 'danger'` | `'primary'` | Color variant |
| `size` | `'default' \| 'large'` | `'default'` | Size |
| `onClick` | `() => void` | - | Click handler (simple) |
| `actions` | `Array<Action>` | `[]` | Actions array (speed dial) |

### Action Type

```typescript
type Action = {
  icon: ReactNode;
  label: string;
  onClick: () => void;
  color?: 'primary' | 'secondary' | 'success' | 'danger' | 'warning' | 'info';
};
```

### Default Icons

Available icons from `FABIcons`:
- `Plus` - Add/create action
- `Edit` - Edit action
- `Task` - Task icon
- `Inspection` - Inspection icon
- `Checklist` - Checklist icon

---

## ModernTable

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `Array<object>` | `[]` | Table data |
| `columns` | `Array<Column>` | - | Column definitions |
| `onRowClick` | `(row) => void` | `undefined` | Row click handler |
| `loading` | `boolean` | `false` | Loading state |

### Column Type

```typescript
type Column = {
  key: string;       // Data key
  label: string;     // Column header
  render?: (value, row) => ReactNode;  // Custom renderer
};
```

---

## Spinner

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Spinner size |
| `color` | `'primary' \| 'secondary' \| 'white'` | `'primary'` | Color |

---

## Toast

### Component

```jsx
import { ToastContainer } from '@/design-system/components';

// Add to root component
<ToastContainer />
```

### Usage

```jsx
// Trigger toast via custom event
const showToast = (type, message) => {
  const event = new CustomEvent('showToast', {
    detail: { type, message }
  });
  window.dispatchEvent(event);
};

// Show toasts
showToast('success', 'Operation successful!');
showToast('error', 'Something went wrong');
showToast('warning', 'Please check your input');
showToast('info', 'Here is some information');
```

---

## Responsive Breakpoints

All components follow these breakpoints:

```css
/* Mobile */
< 768px

/* Tablet */
768px - 1023px

/* Desktop */
>= 1024px
```

---

For live examples and interactive documentation, visit [Storybook](http://localhost:6006).
