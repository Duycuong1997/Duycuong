'use strict';

// End-to-end tests for the registration form using Playwright.
// Run with:  npx playwright test
const { test, expect } = require('@playwright/test');

test.describe('会員情報登録 form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('shows errors when submitting an empty form', async ({ page }) => {
    await page.click('#submit-btn');
    await expect(page.locator('[data-error-for="lastName"]')).toHaveText('姓を入力してください。');
    await expect(page.locator('[data-error-for="email"]')).toHaveText('メールアドレスを入力してください。');
    await expect(page.locator('#success-msg')).toBeHidden();
  });

  test('rejects hiragana in the kana field', async ({ page }) => {
    await page.fill('#L_NAME', '山本');
    await page.fill('#F_NAME', '大輝');
    await page.fill('#L_KANA', 'やまもと'); // hiragana, should fail
    await page.fill('#F_KANA', 'ダイキ');
    await page.fill('#EMAIL', 'yamamoto@example.com');
    await page.click('#submit-btn');

    await expect(page.locator('[data-error-for="lastKana"]')).toHaveText('全角カナで入力してください。');
    await expect(page.locator('#success-msg')).toBeHidden();
  });

  test('accepts a fully valid submission', async ({ page }) => {
    await page.fill('#L_NAME', '山本');
    await page.fill('#F_NAME', '大輝');
    await page.fill('#L_KANA', 'ヤマモト');
    await page.fill('#F_KANA', 'ダイキ');
    await page.fill('#EMAIL', 'yamamoto@example.com');
    await page.click('#submit-btn');

    await expect(page.locator('#success-msg')).toBeVisible();
    await expect(page.locator('.error')).toHaveText(['', '', '', '', '']);
  });
});
