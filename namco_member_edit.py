"""Điền sẵn họ tên trên trang thay đổi thông tin thành viên NAMCO.

Đăng nhập bằng tay, script chỉ điền form và KHÔNG tự bấm lưu.
"""

from playwright.sync_api import sync_playwright

LOGIN_URL = "https://parks2.bandainamco-am.co.jp/login.html"
MEMBER_EDIT_URL = "https://parks2.bandainamco-am.co.jp/member_edit.html"

# (selector, nhãn, giá trị)
FIELDS = [
    ("#L_NAME", "姓", "HO"),
    ("#F_NAME", "名", "THI LINH"),
    ("#L_KANA", "セイ", "ホ"),
    ("#F_KANA", "メイ", "ティリン"),
]


def fill_field(page, selector, label, value):
    field = page.locator(selector)
    if field.count() == 0:
        print(f"Không tìm thấy ô {label}")
        return
    field.fill(value)
    print(f"Đã điền {label} = {value}")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1200, "height": 900})

        # Mở trang đăng nhập
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)

        print("================================")
        print("1. Hãy đăng nhập NAMCO bằng tay.")
        print("2. Sau khi đăng nhập xong, quay lại Terminal.")
        print("3. Nhấn Enter.")
        print("================================")
        input("Nhấn Enter sau khi đăng nhập xong...")

        # Mở trang thay đổi thông tin thành viên
        page.goto(MEMBER_EDIT_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)
        print("Đang ở:", page.url)

        for selector, label, value in FIELDS:
            fill_field(page, selector, label, value)

        print()
        print("==============================")
        print("ĐÃ ĐIỀN XONG")
        print("==============================")
        for _, label, value in FIELDS:
            print(f"{label:<4}: {value}")
        print()
        print("KHÔNG TỰ BẤM LƯU.")

        input("Kiểm tra trên màn hình rồi nhấn Enter để đóng...")
        browser.close()


if __name__ == "__main__":
    main()
