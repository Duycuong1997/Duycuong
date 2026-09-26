# Duycuong

会員情報登録 (member registration) form + automated tests.

## Cấu trúc

```
src/validation.js        # Logic validate (thuần, không phụ thuộc) — dùng chung cho web & test
public/index.html        # Form đăng ký
public/form.js           # Nối validate vào form trên trình duyệt
scripts/serve.js         # Static server tối giản (Node built-in), dùng cho preview & E2E
tests/validation.test.js # Unit test (node:test)
tests/e2e/register.spec.js # E2E test (Playwright)
playwright.config.js
```

## Chạy test

**Unit test** — chạy ngay, không cần cài gì (yêu cầu Node 18+):

```bash
npm test
# hoặc: node --test
```

**E2E test** (Playwright) — cần cài dependency một lần:

```bash
npm install
npx playwright install --with-deps chromium
npm run test:e2e
```

Nếu chạy trong môi trường đã có sẵn Chromium (ví dụ Claude Code on the web), trỏ
Playwright vào binary đó thay vì tải mới:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome npm run test:e2e
```

## Xem form trên trình duyệt

```bash
npm run serve
# mở http://localhost:4173/
```

## Quy tắc validate

- 姓 / 名 (họ / tên): bắt buộc, tối đa 30 ký tự.
- セイ / メイ (katakana): bắt buộc, chỉ chấp nhận **katakana toàn góc (zenkaku)**.
- メールアドレス: bắt buộc, đúng định dạng email.
