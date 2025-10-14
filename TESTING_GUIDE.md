# Testing Guide

Comprehensive testing strategy for the v2.0 Operational Management Platform.

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Test Types](#test-types)
3. [Visual Regression Testing](#visual-regression-testing)
4. [Component Testing](#component-testing)
5. [Integration Testing](#integration-testing)
6. [Mobile Testing](#mobile-testing)

---

## Testing Philosophy

### Testing Pyramid

```
       /\
      /E2E\
     /------\
    /  API   \
   /----------\
  /  Component \
 /--------------\
/     Unit       \
```

- **Unit Tests**: Test individual functions and utilities
- **Component Tests**: Test React components in isolation
- **Integration Tests**: Test component interactions
- **API Tests**: Test backend endpoints
- **E2E Tests**: Test complete user flows

---

## Test Types

### 1. Unit Tests (Jest)

Test individual functions:

```javascript
// utils/formatDate.test.js
import { formatDate } from './formatDate';

describe('formatDate', () => {
  it('formats date correctly', () => {
    const date = '2025-01-01';
    expect(formatDate(date)).toBe('January 1, 2025');
  });
});
```

### 2. Component Tests (React Testing Library)

Test React components:

```javascript
// Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Submit</Button>);
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
  });
});
```

### 3. API Tests (Pytest)

Test backend endpoints:

```python
# tests/test_tasks.py
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_create_task():
    response = client.post(
        "/api/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "priority": "medium",
            "status": "todo"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
```

---

## Visual Regression Testing

### Setup Playwright

**Already Configured** - Ready to use!

```bash
cd frontend
yarn add -D @playwright/test
npx playwright install
```

### Configuration

`playwright.config.js`:

```javascript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/visual',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],
});
```

### Writing Visual Tests

```javascript
// tests/visual/tasks.spec.js
import { test, expect } from '@playwright/test';

test.describe('Tasks Page', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display tasks list', async ({ page }) => {
    await page.goto('/tasks');
    await page.waitForSelector('.tasks-list');
    await expect(page).toHaveScreenshot('tasks-list.png');
  });

  test('should open task details in bottom sheet', async ({ page }) => {
    await page.goto('/tasks');
    await page.click('.task-item:first-child');
    await page.waitForSelector('.bottom-sheet');
    await expect(page).toHaveScreenshot('task-details-bottom-sheet.png');
  });

  test('should show FAB on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/tasks');
    await page.waitForSelector('.fab');
    await expect(page).toHaveScreenshot('tasks-mobile-with-fab.png');
  });

  test('should match dark theme', async ({ page }) => {
    await page.goto('/tasks');
    await page.click('[data-testid="theme-toggle"]');
    await page.waitForTimeout(500);
    await expect(page).toHaveScreenshot('tasks-dark-theme.png');
  });
});
```

### Running Visual Tests

```bash
# Run all visual tests
yarn test:visual

# Update baselines
yarn test:visual:update

# View HTML report
yarn test:visual:report
```

### Test Structure

Recommended directory structure:

```
tests/visual/
├── auth.spec.js          # Login, Register, Password Reset
├── dashboard.spec.js     # Dashboard home
├── tasks.spec.js         # Tasks page, FAB, BottomSheet
├── inspections.spec.js   # Inspections page
├── checklists.spec.js    # Checklists page
├── settings.spec.js      # Settings pages
├── navigation.spec.js    # Sidebar, bottom nav, responsive
├── themes.spec.js        # Light/dark theme tests
└── components.spec.js    # Individual component tests
```

---

## Component Testing

### Testing with Storybook

Storybook stories double as component documentation and visual tests.

```javascript
// Button.stories.jsx
export const AllStates = () => (
  <div style={{ display: 'flex', gap: '12px' }}>
    <Button>Normal</Button>
    <Button disabled>Disabled</Button>
    <Button loading>Loading</Button>
  </div>
);
```

### Interaction Tests

```javascript
import { within, userEvent } from '@storybook/testing-library';
import { expect } from '@storybook/jest';

export const WithInteraction = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    
    await userEvent.click(button);
    await expect(button).toHaveAttribute('aria-pressed', 'true');
  },
};
```

---

## Integration Testing

### Testing User Flows

```javascript
// tests/integration/task-creation-flow.spec.js
import { test, expect } from '@playwright/test';

test('complete task creation flow', async ({ page }) => {
  // 1. Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  
  // 2. Navigate to tasks
  await page.goto('/tasks');
  
  // 3. Click FAB
  await page.click('.fab');
  
  // 4. Fill form
  await page.fill('[name="title"]', 'New Task');
  await page.fill('[name="description"]', 'Task description');
  await page.selectOption('[name="priority"]', 'high');
  
  // 5. Submit
  await page.click('button[type="submit"]');
  
  // 6. Verify task appears
  await expect(page.locator('.task-item')).toContainText('New Task');
});
```

---

## Mobile Testing

### Device Testing

Test on these key devices:

1. **iPhone SE** (375x667) - Small mobile
2. **iPhone 13 Pro** (390x844) - Standard mobile
3. **iPad** (768x1024) - Tablet
4. **Desktop** (1920x1080) - Desktop

### Mobile-Specific Tests

```javascript
test('mobile navigation works', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/dashboard');
  
  // Test bottom navigation
  await page.click('[data-testid="bottom-nav-tasks"]');
  await expect(page).toHaveURL('/tasks');
  
  // Test hamburger menu
  await page.click('[data-testid="hamburger-menu"]');
  await expect(page.locator('.sidebar')).toBeVisible();
});

test('bottom sheet gestures work', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/tasks');
  
  // Open bottom sheet
  await page.click('.task-item:first-child');
  await expect(page.locator('.bottom-sheet')).toBeVisible();
  
  // Swipe down to close (simulate with drag)
  const sheet = page.locator('.bottom-sheet');
  await sheet.dragTo(sheet, { 
    targetPosition: { x: 0, y: 300 } 
  });
  
  await expect(sheet).not.toBeVisible();
});

test('FAB positioning above bottom nav', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/tasks');
  
  const fab = page.locator('.fab');
  const bottomNav = page.locator('.bottom-nav');
  
  const fabBox = await fab.boundingBox();
  const navBox = await bottomNav.boundingBox();
  
  // FAB should be above bottom nav
  expect(fabBox.y).toBeLessThan(navBox.y);
});
```

### Touch Target Testing

```javascript
test('all touch targets meet minimum size', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/tasks');
  
  const buttons = await page.locator('button').all();
  
  for (const button of buttons) {
    const box = await button.boundingBox();
    expect(box.width).toBeGreaterThanOrEqual(44);
    expect(box.height).toBeGreaterThanOrEqual(44);
  }
});
```

---

## Accessibility Testing

### Automated A11y Tests

```javascript
import { injectAxe, checkA11y } from 'axe-playwright';

test('tasks page is accessible', async ({ page }) => {
  await page.goto('/tasks');
  await injectAxe(page);
  await checkA11y(page);
});
```

### Manual A11y Checklist

- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible
- [ ] ARIA labels on icon-only buttons
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader friendly
- [ ] Semantic HTML used

---

## Performance Testing

### Lighthouse CI

```javascript
// lighthouse.config.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/dashboard', 'http://localhost:3000/tasks'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
      },
    },
  },
};
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: yarn install
      
      - name: Type check
        run: yarn type-check
      
      - name: Run visual tests
        run: yarn test:visual
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## Best Practices

### 1. Test User Behavior, Not Implementation

```javascript
// ❌ Bad - tests implementation
expect(component.state.isOpen).toBe(true);

// ✅ Good - tests behavior
expect(screen.getByRole('dialog')).toBeVisible();
```

### 2. Use Data Test IDs Sparingly

```javascript
// ❌ Bad - fragile
await page.click('.task-item:nth-child(3) .edit-button');

// ✅ Good - semantic
await page.click('[aria-label="Edit task"]');

// ✅ Also Good - data-testid for complex cases
await page.click('[data-testid="edit-task-button"]');
```

### 3. Keep Tests Independent

```javascript
// ✅ Good - each test is independent
test('test A', async ({ page }) => {
  // Setup and test A
});

test('test B', async ({ page }) => {
  // Setup and test B (doesn't depend on A)
});
```

### 4. Use Page Object Model

```javascript
// pageObjects/TasksPage.js
export class TasksPage {
  constructor(page) {
    this.page = page;
  }

  async goto() {
    await this.page.goto('/tasks');
  }

  async createTask(title, description) {
    await this.page.click('.fab');
    await this.page.fill('[name="title"]', title);
    await this.page.fill('[name="description"]', description);
    await this.page.click('button[type="submit"]');
  }

  async getTaskCount() {
    return await this.page.locator('.task-item').count();
  }
}

// Usage in test
const tasksPage = new TasksPage(page);
await tasksPage.goto();
await tasksPage.createTask('Test', 'Description');
```

---

## Debugging Tests

### Debug Mode

```bash
# Run tests in headed mode
yarn test:visual --headed

# Run tests in debug mode
yarn test:visual --debug

# Run specific test
yarn test:visual tests/visual/tasks.spec.js
```

### Screenshots and Videos

```javascript
// playwright.config.js
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',
  },
});
```

---

## Coverage Reports

### Generate Coverage

```bash
# Frontend
yarn test --coverage

# Backend
pytest --cov=. --cov-report=html
```

### Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Component Tests**: 70%+ coverage
- **Critical Paths**: 100% coverage

---

## Next Steps

1. ✅ Setup complete
2. 🔄 Write visual regression tests (Phase 6)
3. 📋 Expand component tests
4. 📋 Add integration tests
5. 📋 Setup CI/CD pipeline

**Estimated Time for Phase 6:** 2-3 hours

---

For examples and templates, check the `/tests` directory.
