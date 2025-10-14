import { test, expect } from '@playwright/test';

test.describe('Authentication Pages', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login');
    await page.waitForSelector('.login-card', { timeout: 10000 });
    await expect(page).toHaveScreenshot('login-page.png', { fullPage: true });
  });

  test('login page - mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/login');
    await page.waitForSelector('.login-card');
    await expect(page).toHaveScreenshot('login-page-mobile.png', { fullPage: true });
  });

  test('register page renders correctly', async ({ page }) => {
    await page.goto('/register');
    await page.waitForSelector('.register-card', { timeout: 10000 });
    await expect(page).toHaveScreenshot('register-page.png', { fullPage: true });
  });
});