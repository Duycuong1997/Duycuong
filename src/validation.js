'use strict';

/**
 * Validation rules for the member registration form.
 *
 * Pure, dependency-free functions so they can run both in the browser
 * (bundled into public/form.js) and in Node for unit testing.
 */

// Full-width (zenkaku) katakana, including the long-vowel mark "ー"
// and the full-width space that forms sometimes allow between name parts.
const KATAKANA_RE = /^[゠-ヿー　\s]+$/;

// A deliberately simple, pragmatic email pattern (not full RFC 5322).
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * @param {string} value
 * @returns {boolean}
 */
function isNonEmpty(value) {
  return typeof value === 'string' && value.trim().length > 0;
}

/**
 * Full-width katakana only (used for the furigana / kana fields).
 * Empty strings are considered invalid here; use `required` separately
 * if you want a distinct "required" message.
 * @param {string} value
 * @returns {boolean}
 */
function isFullWidthKatakana(value) {
  return typeof value === 'string' && value.length > 0 && KATAKANA_RE.test(value);
}

/**
 * @param {string} value
 * @returns {boolean}
 */
function isEmail(value) {
  return typeof value === 'string' && EMAIL_RE.test(value);
}

/**
 * @param {string} value
 * @param {number} max
 * @returns {boolean}
 */
function isWithinMaxLength(value, max) {
  return typeof value === 'string' && value.length <= max;
}

/**
 * Validate the whole registration form payload.
 *
 * @param {{lastName?: string, firstName?: string, lastKana?: string,
 *          firstKana?: string, email?: string}} data
 * @returns {{valid: boolean, errors: Record<string, string>}}
 */
function validateRegistration(data = {}) {
  const errors = {};

  if (!isNonEmpty(data.lastName)) {
    errors.lastName = '姓を入力してください。';
  } else if (!isWithinMaxLength(data.lastName, 30)) {
    errors.lastName = '姓は30文字以内で入力してください。';
  }

  if (!isNonEmpty(data.firstName)) {
    errors.firstName = '名を入力してください。';
  } else if (!isWithinMaxLength(data.firstName, 30)) {
    errors.firstName = '名は30文字以内で入力してください。';
  }

  if (!isNonEmpty(data.lastKana)) {
    errors.lastKana = 'セイを入力してください。';
  } else if (!isFullWidthKatakana(data.lastKana)) {
    errors.lastKana = '全角カナで入力してください。';
  }

  if (!isNonEmpty(data.firstKana)) {
    errors.firstKana = 'メイを入力してください。';
  } else if (!isFullWidthKatakana(data.firstKana)) {
    errors.firstKana = '全角カナで入力してください。';
  }

  if (!isNonEmpty(data.email)) {
    errors.email = 'メールアドレスを入力してください。';
  } else if (!isEmail(data.email)) {
    errors.email = 'メールアドレスの形式が正しくありません。';
  }

  return { valid: Object.keys(errors).length === 0, errors };
}

const api = {
  isNonEmpty,
  isFullWidthKatakana,
  isEmail,
  isWithinMaxLength,
  validateRegistration,
};

// Works both as a CommonJS module (Node/tests) and attached to window (browser).
if (typeof module !== 'undefined' && module.exports) {
  module.exports = api;
}
if (typeof window !== 'undefined') {
  window.RegistrationValidation = api;
}
