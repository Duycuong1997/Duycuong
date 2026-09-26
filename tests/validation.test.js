'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const {
  isNonEmpty,
  isFullWidthKatakana,
  isEmail,
  isWithinMaxLength,
  validateRegistration,
} = require('../src/validation');

test('isNonEmpty', () => {
  assert.equal(isNonEmpty('山本'), true);
  assert.equal(isNonEmpty('   '), false, 'whitespace-only is empty');
  assert.equal(isNonEmpty(''), false);
  assert.equal(isNonEmpty(undefined), false);
});

test('isFullWidthKatakana accepts zenkaku katakana', () => {
  assert.equal(isFullWidthKatakana('ヤマモト'), true);
  assert.equal(isFullWidthKatakana('ダイキ'), true);
  assert.equal(isFullWidthKatakana('ジョー'), true, 'long-vowel mark allowed');
});

test('isFullWidthKatakana rejects hiragana / halfwidth / latin', () => {
  assert.equal(isFullWidthKatakana('やまもと'), false, 'hiragana rejected');
  assert.equal(isFullWidthKatakana('ﾔﾏﾓﾄ'), false, 'halfwidth katakana rejected');
  assert.equal(isFullWidthKatakana('Yamamoto'), false, 'latin rejected');
  assert.equal(isFullWidthKatakana(''), false);
});

test('isEmail', () => {
  assert.equal(isEmail('user@example.com'), true);
  assert.equal(isEmail('a.b+tag@sub.example.co.jp'), true);
  assert.equal(isEmail('no-at-sign'), false);
  assert.equal(isEmail('foo@bar'), false, 'missing TLD');
  assert.equal(isEmail('foo @bar.com'), false, 'space rejected');
});

test('isWithinMaxLength', () => {
  assert.equal(isWithinMaxLength('abc', 3), true);
  assert.equal(isWithinMaxLength('abcd', 3), false);
});

test('validateRegistration: fully valid payload', () => {
  const result = validateRegistration({
    lastName: '山本',
    firstName: '大輝',
    lastKana: 'ヤマモト',
    firstKana: 'ダイキ',
    email: 'yamamoto@example.com',
  });
  assert.equal(result.valid, true);
  assert.deepEqual(result.errors, {});
});

test('validateRegistration: reports every empty required field', () => {
  const result = validateRegistration({});
  assert.equal(result.valid, false);
  assert.deepEqual(Object.keys(result.errors).sort(), [
    'email',
    'firstKana',
    'firstName',
    'lastKana',
    'lastName',
  ]);
});

test('validateRegistration: kana field rejects non-katakana', () => {
  const result = validateRegistration({
    lastName: '山本',
    firstName: '大輝',
    lastKana: 'やまもと', // hiragana
    firstKana: 'ダイキ',
    email: 'yamamoto@example.com',
  });
  assert.equal(result.valid, false);
  assert.equal(result.errors.lastKana, '全角カナで入力してください。');
  assert.equal(result.errors.firstKana, undefined);
});

test('validateRegistration: enforces max length on name', () => {
  const result = validateRegistration({
    lastName: 'あ'.repeat(31),
    firstName: '大輝',
    lastKana: 'ヤマモト',
    firstKana: 'ダイキ',
    email: 'yamamoto@example.com',
  });
  assert.equal(result.valid, false);
  assert.equal(result.errors.lastName, '姓は30文字以内で入力してください。');
});

test('validateRegistration: invalid email', () => {
  const result = validateRegistration({
    lastName: '山本',
    firstName: '大輝',
    lastKana: 'ヤマモト',
    firstKana: 'ダイキ',
    email: 'not-an-email',
  });
  assert.equal(result.valid, false);
  assert.equal(result.errors.email, 'メールアドレスの形式が正しくありません。');
});
