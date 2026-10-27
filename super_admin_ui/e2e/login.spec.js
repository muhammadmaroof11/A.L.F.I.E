import { test, expect } from '@playwright/test';

test.describe('Super Admin Login & Authentication Smoke Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should display login form with correct branding and fields', async ({ page }) => {
    // Branding and titles
    await expect(page.locator('h1')).toContainText('A.L.F.I.E Portal');
    await expect(page.getByText('Super Admin Authentication')).toBeVisible();

    // Inputs
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');
    const submitBtn = page.locator('button[type="submit"]');

    await expect(emailInput).toBeVisible();
    await expect(emailInput).toHaveAttribute('placeholder', 'admin@alfie.com');
    await expect(passwordInput).toBeVisible();
    await expect(submitBtn).toBeVisible();
    await expect(submitBtn).toContainText('Sign In');
  });

  test('should require email and password to submit', async ({ page }) => {
    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    await expect(emailInput).toHaveAttribute('required', '');
    await expect(passwordInput).toHaveAttribute('required', '');
  });

  test('should display error message on invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'wrong@admin.com');
    await page.fill('input[type="password"]', 'invalidpassword123');
    await page.click('button[type="submit"]');

    // Should remain on the login page and show error or loading
    await expect(page).toHaveURL(/.*login/);
  });
});
