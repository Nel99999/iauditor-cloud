import { test, expect } from '@playwright/test';

test.describe('Public Pages', () => {
  test('home redirect to login', async ({ page }) => {
    await page.goto('/');
    // Should redirect to login
    await page.waitForURL('/login', { timeout: 10000 });
    await expect(page).toHaveScreenshot('home-redirect.png', { fullPage: true });
  });
});