# Duycuong

Ứng dụng **Đăng ký / Đăng nhập** viết bằng **Python (Flask) + SQLite**.

## Tính năng
- Đăng ký tài khoản (kiểm tra tên đăng nhập, độ dài mật khẩu, xác nhận mật khẩu)
- Đăng nhập / Đăng xuất bằng session (cookie `httpOnly`)
- Mật khẩu được mã hoá bằng `werkzeug.security` (không lưu mật khẩu gốc)
- Chống CSRF bằng token ẩn trong form
- Khoá tài khoản 15 phút sau 5 lần nhập sai
- Trang `/dashboard` chỉ vào được khi đã đăng nhập

## Cách chạy
```bash
python -m venv venv
# Windows: venv\Scripts\activate    |    Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Mở trình duyệt: http://localhost:5000

Biến môi trường (tuỳ chọn): `PORT`, `SECRET_KEY`, `FLASK_DEBUG=1`, `FLASK_ENV=production`.

## Cấu trúc
```
app.py                   # Toàn bộ logic: DB, đăng ký, đăng nhập, đăng xuất
templates/base.html      # Khung chung + hiển thị thông báo
templates/login.html     # Trang đăng nhập
templates/register.html  # Trang đăng ký
templates/dashboard.html # Trang sau khi đăng nhập
static/style.css         # Giao diện
users.db                 # CSDL SQLite (tự tạo khi chạy)
```
