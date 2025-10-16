# DARK MODE VISIBILITY FIX - ACTION PLAN

## Issue Summary
User reported "DARK on DARK" text visibility problems across pages and menus in dark mode.

## Root Cause Analysis

### ✅ Design System is Sound
The color system uses OKLCH color space with proper contrast ratios:
- **Primary Text**: oklch(98% ...) - Very light on dark backgrounds
- **Secondary Text**: oklch(75% ...) - Good contrast
- **Backgrounds**: oklch(18-22% ...) - Dark enough for contrast

### ⚠️ Potential Problem Areas

#### 1. Hard-Coded Tailwind Classes
Some components bypass the design system by using hard-coded Tailwind classes:
```tsx
// ❌ Problem: May not adapt properly to dark mode
className="text-gray-600 dark:text-gray-400"

// ✅ Solution: Use design tokens
className="text-secondary"  // Uses var(--color-text-secondary)
```

#### 2. Navigation Menu
- Active/inactive states may have insufficient contrast
- Hover states may be too subtle
- Selected item highlighting may not be visible enough

#### 3. Form Elements
- Placeholder text may be too light
- Disabled inputs may blend with background
- Focus states may not be visible

#### 4. Status Badges
- Success/Warning/Error badges may not have enough contrast
- Custom colored badges may be invisible

## Implementation Plan

### Phase 1: Global CSS Variable Audit (15 min)
1. Search for hard-coded color classes in all components
2. Create list of files needing updates
3. Prioritize by user-facing impact

### Phase 2: Navigation & Menu Fix (20 min)
1. Update LayoutNew.tsx menu colors
2. Ensure active state is highly visible
3. Increase hover state contrast
4. Test menu in dark mode

### Phase 3: Form & Input Fix (15 min)
1. Update placeholder colors
2. Ensure focus rings are visible
3. Fix disabled state contrast
4. Test all form pages

### Phase 4: Badge & Status Fix (10 min)
1. Audit all semantic color usage
2. Ensure success/warning/error colors meet WCAG AA
3. Update custom badge colors

### Phase 5: Testing & Verification (15 min)
1. Screenshot audit of all pages
2. Contrast ratio testing
3. User acceptance verification

## Files to Update

### High Priority
1. `/app/frontend/src/components/LayoutNew.tsx` - Navigation menu
2. `/app/frontend/src/design-system/global-modern-overrides.css` - Global overrides
3. `/app/frontend/src/components/ui/` - UI component library

### Medium Priority
4. Individual page components with hard-coded colors
5. Badge and status indicator components

### Low Priority
6. Auth pages (may already be correct)
7. Settings pages (typically have good contrast)

## Specific Fixes Needed

### Fix 1: Navigation Menu Active State
```css
/* Current (may be too subtle) */
.nav-item-active {
  background: var(--color-surface-elevated);
}

/* Improved */
.nav-item-active {
  background: var(--color-brand-primary);
  color: var(--color-brand-primary-contrast);
  font-weight: var(--typography-weight-semibold);
}
```

### Fix 2: Replace Hard-Coded Colors
```tsx
// Find all instances of:
text-gray-600 dark:text-gray-400
text-slate-600 dark:text-slate-400

// Replace with:
text-secondary  // or var(--color-text-secondary)
```

### Fix 3: Form Placeholders
```css
/* Ensure placeholders are visible */
input::placeholder,
textarea::placeholder {
  color: var(--color-text-disabled);
  opacity: 1;
}
```

### Fix 4: Focus Rings
```css
/* Make focus states more visible in dark mode */
:focus-visible {
  outline: 2px solid var(--color-brand-primary);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px oklch(70% 0.18 230 / 0.2);
}
```

## Testing Checklist

### Manual Testing
- [ ] Navigation menu - all states (default, hover, active)
- [ ] Form inputs - placeholder, focus, disabled, error
- [ ] Buttons - all variants in dark mode
- [ ] Badges - all semantic colors
- [ ] Cards - text readability on dark backgrounds
- [ ] Modals/Dialogs - overlay and content contrast
- [ ] Tables - row striping and headers
- [ ] Dropdowns/Selects - options visibility

### Automated Testing
```bash
# Use accessibility testing tools
npm run test:a11y  # If available

# Or manual contrast checking
# Use browser DevTools > Accessibility panel
# Verify all text meets WCAG AA (4.5:1 for normal text)
```

## Expected Outcomes

### Before
- Some text hard to read in dark mode
- Navigation states unclear
- Form elements blending together
- Status badges invisible

### After
- ✅ All text clearly readable (WCAG AA compliance)
- ✅ Navigation states highly visible
- ✅ Form elements clearly distinguished
- ✅ Status badges prominent and clear
- ✅ Consistent dark mode experience across all pages

## Rollback Plan
If issues arise:
1. Git revert to before dark mode changes
2. Or selectively revert problem files
3. Current state is stable, so rollback is safe

## Timeline
- Total Estimated Time: 75 minutes
- Can be done incrementally
- Each phase is independently testable

---

*Created: October 16, 2025*
*Status: Ready for Implementation*
*Priority: High (User-Reported Issue)*
