# Mobile UX Guide

Best practices and patterns for mobile user experience in the v2.0 Operational Management Platform.

## Table of Contents

1. [Mobile-First Philosophy](#mobile-first-philosophy)
2. [Touch Targets](#touch-targets)
3. [Gesture Interactions](#gesture-interactions)
4. [Bottom Sheets](#bottom-sheets)
5. [FAB Usage](#fab-usage)
6. [Responsive Navigation](#responsive-navigation)
7. [Performance](#performance)

---

## Mobile-First Philosophy

### Design Principles

1. **Touch-First**: All interactions are optimized for touch
2. **Thumb-Friendly**: Primary actions within thumb reach
3. **Context-Aware**: Show relevant info without overwhelming
4. **Gesture-Native**: Support common mobile gestures

### Viewport Sizes

Target these key breakpoints:

- **Mobile**: 390x844px (iPhone 13/14 Pro)
- **Tablet**: 768x1024px (iPad)
- **Desktop**: 1920x1080px

---

## Touch Targets

### Minimum Sizes

All interactive elements must meet minimum touch targets:

| Element | Minimum Size | Recommended Size |
|---------|--------------|------------------|
| Button | 44x44px | 48x48px |
| Icon Button | 44x44px | 48x48px |
| FAB | 56x56px | 56-64px |
| Checkbox/Radio | 24x24px (with padding) | 28x28px |
| Input | Height 44px | Height 48px |

### Spacing

Maintain adequate spacing between touch targets:

```css
.touch-elements {
  gap: var(--spacing-md); /* 16px minimum */
}
```

### Example

```jsx
// ✅ Good - adequate size and spacing
<div style={{ display: 'flex', gap: '16px' }}>
  <Button size="lg" icon={<Plus size={20} />}>Create</Button>
  <Button size="lg" icon={<Edit size={20} />}>Edit</Button>
</div>

// ❌ Bad - too small and crowded
<div style={{ display: 'flex', gap: '4px' }}>
  <Button size="sm">Create</Button>
  <Button size="sm">Edit</Button>
</div>
```

---

## Gesture Interactions

### Supported Gestures

The platform supports standard mobile gestures:

1. **Tap** - Primary selection/action
2. **Long Press** - Context menu/details
3. **Swipe** - Navigation/dismissal
4. **Pinch** - Zoom (where applicable)
5. **Pull to Refresh** - Data reload

### Implementation

Using `react-swipeable`:

```jsx
import { useSwipeable } from 'react-swipeable';

const handlers = useSwipeable({
  onSwipedLeft: () => console.log('Swiped left'),
  onSwipedRight: () => console.log('Swiped right'),
  onSwipedDown: () => console.log('Swiped down'),
  trackMouse: false,
  trackTouch: true,
});

<div {...handlers}>Swipeable content</div>
```

### Gesture Feedback

Always provide immediate visual feedback:

```jsx
// Touch state with Framer Motion
<motion.button
  whileTap={{ scale: 0.95 }}
  whileHover={{ scale: 1.05 }}
>
  Tap me
</motion.button>
```

---

## Bottom Sheets

### When to Use

Bottom sheets are ideal for:

- ✅ Task details
- ✅ Forms and input
- ✅ Filter options
- ✅ Quick actions
- ✅ Contextual information

### When NOT to Use

Avoid bottom sheets for:

- ❌ Full-page content
- ❌ Complex multi-step flows
- ❌ Critical warnings (use alerts)
- ❌ Primary navigation

### Usage Patterns

#### Task Details

```jsx
const TaskDetails = ({ task }) => {
  const { isOpen, open, close } = useBottomSheet();

  return (
    <>
      <TaskCard onClick={open} />
      <BottomSheet isOpen={isOpen} onClose={close} snapPoint="half" title={task.title}>
        <TaskDetailsContent task={task} />
      </BottomSheet>
    </>
  );
};
```

#### Filter Options

```jsx
const FilterSheet = () => {
  const { isOpen, open, close } = useBottomSheet();

  return (
    <>
      <Button onClick={open} icon={<Filter />}>Filters</Button>
      <BottomSheet isOpen={isOpen} onClose={close} snapPoint="half" title="Filter Tasks">
        <FilterForm onApply={close} />
      </BottomSheet>
    </>
  );
};
```

#### Quick Form

```jsx
const QuickCreate = () => {
  const { isOpen, open, close } = useBottomSheet();

  return (
    <>
      <FAB icon={<Plus />} onClick={open} />
      <BottomSheet isOpen={isOpen} onClose={close} snapPoint="full" title="Create Task">
        <CreateTaskForm onSubmit={() => { /* handle */ close(); }} />
      </BottomSheet>
    </>
  );
};
```

### Snap Points Guide

- **Peek (25%)**: Quick preview or notification
- **Half (50%)**: Default for most content
- **Full (90%)**: Forms or detailed content

---

## FAB Usage

### Placement

FAB should be placed strategically:

```jsx
// ✅ Primary action on main screen
<FAB
  variant="simple"
  position="bottom-right"
  icon={<Plus />}
  onClick={createTask}
/>

// ✅ Multiple related actions
<FAB
  variant="speedDial"
  position="bottom-right"
  icon={<Plus />}
  actions={[
    { icon: <Task />, label: 'Task', onClick: createTask },
    { icon: <Inspection />, label: 'Inspection', onClick: createInspection },
  ]}
/>
```

### Best Practices

1. **One Per Screen**: Only one FAB per view
2. **Primary Action**: Use for most important action
3. **Persistent**: Keep visible on scroll
4. **Avoid Overlap**: Don't overlap with bottom navigation
5. **Speed Dial**: Max 3-5 actions in speed dial

### Position Strategy

```
┌─────────────────┐
│                 │
│   Content       │
│                 │
│              ┌──┐  <- FAB
│              └──┘
├─────────────────┤
│  Bottom Nav     │  <- Avoid overlap
└─────────────────┘
```

On mobile with bottom navigation, FAB is automatically positioned above:

```css
@media (max-width: 767px) {
  .fab-container {
    bottom: calc(var(--spacing-xl) + 64px); /* 64px = bottom nav height */
  }
}
```

---

## Responsive Navigation

### Adaptive Navigation System

The platform uses adaptive navigation that changes based on viewport:

```
Mobile (< 600px)     -> Bottom Navigation
Tablet (600-1024px)  -> Nav Rail (sidebar)
Desktop (> 1024px)   -> Full Sidebar
```

### Implementation

```jsx
import { AdaptiveNav } from '@/design-system/components';

<AdaptiveNav />  // Automatically adapts
```

### Bottom Navigation

For mobile, bottom navigation provides:

- 4-5 primary menu items
- Icons + labels
- Active state indication
- Easy thumb reach

### Nav Rail (Tablet)

For tablets, nav rail offers:

- Icon-only navigation
- Hover tooltips
- Compact 72px width
- Vertical layout

---

## Performance

### Optimize for Mobile

1. **Lazy Loading**: Load components on-demand

```jsx
const TasksPage = lazy(() => import('./TasksPageNew'));
```

2. **Image Optimization**: Use responsive images

```jsx
<img
  src="/image-small.jpg"
  srcSet="/image-small.jpg 400w, /image-medium.jpg 800w"
  sizes="(max-width: 600px) 400px, 800px"
  alt="Description"
/>
```

3. **Debounce Input**: Reduce API calls

```jsx
const debouncedSearch = useMemo(
  () => debounce(searchHandler, 300),
  []
);
```

4. **Virtual Lists**: For long lists

```jsx
// Use react-window or react-virtualized
import { FixedSizeList } from 'react-window';
```

### Testing on Mobile

Always test on real devices:

1. **Chrome DevTools**: Mobile emulation
2. **Real Devices**: iPhone, Android phones
3. **Network Throttling**: Test on 3G/4G
4. **Touch Testing**: Physical touch interactions

---

## Common Patterns

### Loading States

```jsx
{loading ? (
  <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
    <Spinner size="lg" />
  </div>
) : (
  <Content />
)}
```

### Empty States

```jsx
<EmptyState
  icon={<FileText size={48} />}
  title="No tasks yet"
  description="Create your first task to get started"
  action={<Button onClick={create}>Create Task</Button>}
/>
```

### Pull to Refresh

```jsx
const handlers = useSwipeable({
  onSwipedDown: (eventData) => {
    if (window.scrollY === 0) {
      refreshData();
    }
  },
});
```

### Infinite Scroll

```jsx
useEffect(() => {
  const handleScroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 500) {
      loadMore();
    }
  };
  window.addEventListener('scroll', handleScroll);
  return () => window.removeEventListener('scroll', handleScroll);
}, []);
```

---

## Accessibility on Mobile

### Screen Readers

Ensure mobile screen readers work:

```jsx
<button
  aria-label="Create new task"
  role="button"
  tabIndex={0}
>
  <Plus aria-hidden="true" />
</button>
```

### Focus Management

Manage focus for modals:

```jsx
useEffect(() => {
  if (isOpen) {
    // Focus first input in bottom sheet
    firstInputRef.current?.focus();
  }
}, [isOpen]);
```

### Voice Control

Support voice commands where applicable:

```jsx
<button aria-label="Navigate to tasks page" onClick={navigateToTasks}>
  Tasks
</button>
```

---

## Testing Checklist

- [ ] All touch targets ≥ 44x44px
- [ ] Adequate spacing between interactive elements
- [ ] Gestures work as expected (swipe, tap)
- [ ] Bottom sheets open/close smoothly
- [ ] FAB doesn't overlap bottom nav
- [ ] Navigation adapts to viewport
- [ ] Loading states are clear
- [ ] Empty states provide guidance
- [ ] Works on slow networks
- [ ] Accessible with screen readers

---

For component examples, visit [Storybook](http://localhost:6006).
