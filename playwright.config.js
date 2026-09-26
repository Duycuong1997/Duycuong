'use strict';

const { defineConfig } = require('@playwright/test');

// Allow pointing at a pre-installed Chromium (e.g. Claude Code on the web,
// where PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH is set) so the browser build does
// not have to match the @playwright/test version exactly. Falls back to the
// version Playwright manages itself when the env var is absent.
const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined;

// Serves ./public and runs the E2E specs in tests/e2e against it.
module.exports = defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:4173',
    launchOptions: executablePath ? { executablePath } : {},
  },
  webServer: {
    // Zero-dependency static server (Node built-in) — see scripts/serve.js
    command: 'node scripts/serve.js',
    url: 'http://localhost:4173/',
    reuseExistingServer: !process.env.CI,
  },
});
