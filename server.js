const express = require('express');
const session = require('express-session');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const USERS_FILE = path.join(__dirname, 'data', 'users.json');

// ---------- Lưu trữ người dùng (file JSON) ----------
function loadUsers() {
  try {
    return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
  } catch {
    return [];
  }
}

function saveUsers(users) {
  fs.mkdirSync(path.dirname(USERS_FILE), { recursive: true });
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

// ---------- Mã hoá mật khẩu (scrypt + salt) ----------
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 64).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(':');
  const hashBuffer = Buffer.from(hash, 'hex');
  const candidate = crypto.scryptSync(password, salt, 64);
  return crypto.timingSafeEqual(hashBuffer, candidate);
}

// ---------- Giới hạn số lần đăng nhập sai ----------
const MAX_ATTEMPTS = 5;
const LOCK_TIME_MS = 15 * 60 * 1000;
const failedAttempts = new Map(); // key: username -> { count, lockedUntil }

function isLocked(username) {
  const entry = failedAttempts.get(username);
  return entry && entry.lockedUntil && entry.lockedUntil > Date.now();
}

function recordFailure(username) {
  const entry = failedAttempts.get(username) || { count: 0, lockedUntil: 0 };
  entry.count += 1;
  if (entry.count >= MAX_ATTEMPTS) {
    entry.lockedUntil = Date.now() + LOCK_TIME_MS;
    entry.count = 0;
  }
  failedAttempts.set(username, entry);
}

// ---------- Middleware ----------
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.use(
  session({
    secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      sameSite: 'lax',
      secure: process.env.NODE_ENV === 'production',
      maxAge: 60 * 60 * 1000, // 1 giờ
    },
  })
);
app.use(express.static(path.join(__dirname, 'public'), { index: false }));

function requireLogin(req, res, next) {
  if (req.session.user) return next();
  res.redirect('/login');
}

function redirectIfLoggedIn(req, res, next) {
  if (req.session.user) return res.redirect('/dashboard');
  next();
}

// ---------- Trang ----------
app.get('/', (req, res) => {
  res.redirect(req.session.user ? '/dashboard' : '/login');
});

app.get('/login', redirectIfLoggedIn, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/register', redirectIfLoggedIn, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

app.get('/dashboard', requireLogin, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

// ---------- API ----------
app.post('/api/register', (req, res) => {
  const username = String(req.body.username || '').trim().toLowerCase();
  const password = String(req.body.password || '');
  const confirm = String(req.body.confirm || '');

  if (!/^[a-z0-9_]{3,20}$/.test(username)) {
    return res.status(400).json({ error: 'Tên đăng nhập phải từ 3-20 ký tự (chữ, số, dấu gạch dưới).' });
  }
  if (password.length < 6) {
    return res.status(400).json({ error: 'Mật khẩu phải có ít nhất 6 ký tự.' });
  }
  if (password !== confirm) {
    return res.status(400).json({ error: 'Mật khẩu xác nhận không khớp.' });
  }

  const users = loadUsers();
  if (users.some((u) => u.username === username)) {
    return res.status(409).json({ error: 'Tên đăng nhập đã tồn tại.' });
  }

  users.push({ username, password: hashPassword(password), createdAt: new Date().toISOString() });
  saveUsers(users);
  res.json({ message: 'Đăng ký thành công! Vui lòng đăng nhập.' });
});

app.post('/api/login', (req, res) => {
  const username = String(req.body.username || '').trim().toLowerCase();
  const password = String(req.body.password || '');

  if (!username || !password) {
    return res.status(400).json({ error: 'Vui lòng nhập tên đăng nhập và mật khẩu.' });
  }
  if (isLocked(username)) {
    return res.status(429).json({ error: 'Bạn đã nhập sai quá nhiều lần. Vui lòng thử lại sau 15 phút.' });
  }

  const user = loadUsers().find((u) => u.username === username);
  if (!user || !verifyPassword(password, user.password)) {
    recordFailure(username);
    return res.status(401).json({ error: 'Tên đăng nhập hoặc mật khẩu không đúng.' });
  }

  failedAttempts.delete(username);
  // Tạo session mới để tránh session fixation
  req.session.regenerate((err) => {
    if (err) return res.status(500).json({ error: 'Lỗi máy chủ.' });
    req.session.user = { username: user.username };
    res.json({ message: 'Đăng nhập thành công!', redirect: '/dashboard' });
  });
});

app.get('/api/me', requireLogin, (req, res) => {
  res.json({ username: req.session.user.username });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy(() => {
    res.clearCookie('connect.sid');
    res.json({ message: 'Đã đăng xuất.', redirect: '/login' });
  });
});

app.listen(PORT, () => {
  console.log(`Server đang chạy tại http://localhost:${PORT}`);
});
