from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

URL = (
    "https://parks2.bandainamco-am.co.jp/"
    "login.html?request=redirect_logon"
    "&redirectTo=member_history.html"
)

# Mỗi tài khoản là một cặp: (email, mật khẩu)
DANH_SACH_ACC = [
    {"email": "email1@hotmail.com", "mat_khau": "matkhau1"},
    {"email": "email2@hotmail.com", "mat_khau": "matkhau2"},
    {"email": "email3@hotmail.com", "mat_khau": "matkhau3"},
    {"email": "email4@hotmail.com", "mat_khau": "matkhau4"},
    {"email": "email5@hotmail.com", "mat_khau": "matkhau5"},
]


def tim_o_nhap(trang, cac_selector):
    """Thử lần lượt các selector, trả về locator đầu tiên tìm thấy."""
    for selector in cac_selector:
        o = trang.locator(selector)
        if o.count() > 0:
            return o.first
    return None


def dang_nhap_mot_acc(trang, email, mat_khau, so_thu_tu):
    trang.goto(URL, wait_until="domcontentloaded", timeout=60000)
    trang.wait_for_timeout(2000)
    print(f"Trang {so_thu_tu} đã mở: {email}")

    # 1) Điền email
    o_email = tim_o_nhap(trang, [
        'input[type="email"]:visible',
        'input[name*="mail" i]:visible',
        'input[id*="mail" i]:visible',
        'input[type="text"]:visible',
        'input:visible',
    ])
    if o_email is None:
        print(f"  [LỖI] Trang {so_thu_tu}: không tìm thấy ô email")
        return False
    o_email.fill(email)

    # 2) Điền mật khẩu
    o_mat_khau = tim_o_nhap(trang, [
        'input[type="password"]:visible',
        'input[name*="pass" i]:visible',
        'input[id*="pass" i]:visible',
    ])
    if o_mat_khau is None:
        print(f"  [LỖI] Trang {so_thu_tu}: không tìm thấy ô mật khẩu")
        return False
    o_mat_khau.fill(mat_khau)
    print(f"  Đã điền email + mật khẩu ở trang {so_thu_tu}")

    # 3) Bấm nút đăng nhập và chờ điều hướng
    o_nut = tim_o_nhap(trang, [
        'button[type="submit"]:visible',
        'input[type="submit"]:visible',
        'button:has-text("ログイン"):visible',   # "Đăng nhập" tiếng Nhật
        'a:has-text("ログイン"):visible',
        'button:has-text("Login"):visible',
    ])

    try:
        if o_nut is not None:
            with trang.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                o_nut.click()
        else:
            # Không có nút rõ ràng -> submit bằng Enter trên ô mật khẩu
            with trang.expect_navigation(wait_until="domcontentloaded", timeout=30000):
                o_mat_khau.press("Enter")
    except PWTimeout:
        # Có trang không điều hướng mà chỉ đổi nội dung -> không coi là lỗi cứng
        print(f"  [CẢNH BÁO] Trang {so_thu_tu}: không thấy điều hướng, kiểm tra thủ công")

    trang.wait_for_timeout(2000)

    # 4) Kiểm tra sơ bộ kết quả: còn ô mật khẩu nghĩa là chưa vào được
    con_o_mat_khau = trang.locator('input[type="password"]:visible').count() > 0
    if con_o_mat_khau:
        print(f"  [THẤT BẠI] Trang {so_thu_tu}: có thể sai thông tin đăng nhập")
        return False

    print(f"  [THÀNH CÔNG] Trang {so_thu_tu}: đã đăng nhập {email}")
    return True


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    cac_phien = []
    cac_trang = []

    for i, acc in enumerate(DANH_SACH_ACC, start=1):
        phien = browser.new_context()
        trang = phien.new_page()
        cac_phien.append(phien)
        cac_trang.append(trang)

        try:
            dang_nhap_mot_acc(trang, acc["email"], acc["mat_khau"], i)
        except Exception as e:
            print(f"Trang {i} gặp lỗi: {e}")

    print("\nĐã xử lý xong tất cả tài khoản.")
    input("Nhấn Enter để đóng tất cả cửa sổ...")

    browser.close()
