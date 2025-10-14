import { test, expect } from '@playwright/test';

test.describe('Design System Components', () => {
  test('bottom sheet component', async ({ page }) => {
    await page.goto('/tasks');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    await page.goto('/tasks');
    
    // Click on a task to open bottom sheet
    const taskItem = await page.locator('.task-item').first();
    if (await taskItem.count() > 0) {
      await taskItem.click();
      await page.waitForSelector('.bottom-sheet', { timeout: 5000 });
      await expect(page).toHaveScreenshot('bottom-sheet-open.png');
    }
  });

  test('FAB component', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/tasks');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    await page.goto('/tasks');
    
    await page.waitForSelector('.fab', { timeout: 5000 });
    await expect(page).toHaveScreenshot('fab-mobile.png');
  });
});