import { test, expect } from '@playwright/test';

// Helper function for login
async function login(page) {
  await page.goto('/login');
  await page.fill('input[type="email"]', 'test@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 10000 });
}

test.describe('Dashboard', () => {
  test('dashboard home page', async ({ page }) => {
    await login(page);
    await page.waitForSelector('.dashboard-stats-grid', { timeout: 10000 });
    await expect(page).toHaveScreenshot('dashboard-home.png', { fullPage: true });
  });

  test('dashboard - mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await login(page);
    await page.waitForSelector('.dashboard-stats-grid');
    await expect(page).toHaveScreenshot('dashboard-mobile.png', { fullPage: true });
  });
});