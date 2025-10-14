import { test, expect } from '@playwright/test';

test.describe('Design System Components', () => {
  test('component demo page', async ({ page }) => {
    await page.goto('/demo');
    await page.waitForSelector('.component-demo', { timeout: 10000 });
    await expect(page).toHaveScreenshot('component-demo-page.png', { fullPage: true });
  });

  test('component demo - mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/demo');
    await page.waitForSelector('.component-demo', { timeout: 10000 });
    await expect(page).toHaveScreenshot('component-demo-mobile.png', { fullPage: true });
  });
});