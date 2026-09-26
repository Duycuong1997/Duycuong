# Duycuong

Ứng dụng **Đăng ký / Đăng nhập** đơn giản viết bằng Node.js + Express.

## Tính năng
- Đăng ký tài khoản (kiểm tra tên đăng nhập, độ dài mật khẩu, xác nhận mật khẩu)
- Đăng nhập / Đăng xuất bằng session (cookie `httpOnly`)
- Mật khẩu được mã hoá bằng `scrypt` + salt (không lưu mật khẩu gốc)
- Khoá tài khoản 15 phút sau 5 lần nhập sai
- Trang `/dashboard` chỉ vào được khi đã đăng nhập

## Cách chạy
```bash
npm install
npm start
```
Mở trình duyệt: http://localhost:3000

Biến môi trường (tuỳ chọn): `PORT`, `SESSION_SECRET`, `NODE_ENV=production`.

## Cấu trúc
```
server.js            # Server Express: route trang + API đăng ký/đăng nhập
public/login.html    # Trang đăng nhập
public/register.html # Trang đăng ký
public/dashboard.html# Trang sau khi đăng nhập
public/app.js        # Xử lý form phía trình duyệt
public/style.css     # Giao diện
data/users.json      # Dữ liệu người dùng (tự tạo khi đăng ký)
```
