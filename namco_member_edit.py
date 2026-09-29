"""Điền sẵn họ tên trên trang thay đổi thông tin thành viên NAMCO.

- Lưu phiên đăng nhập vào thư mục profile, lần sau không cần đăng nhập lại.
- Tự phát hiện khi đăng nhập xong, không cần quay lại Terminal nhấn Enter.
- Chờ form tải xong thay vì chờ cứng 3 giây.
- Kiểm tra lại giá trị sau khi điền.
- KHÔNG tự bấm lưu.

Ví dụ:
    python namco_member_edit.py
    python namco_member_edit.py --sei HO --mei "THI LINH" --sei-kana ホ --mei-kana ティリン
"""

import argparse
import re
import sys
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_URL = "https://parks2.bandainamco-am.co.jp"
LOGIN_URL = f"{BASE_URL}/login.html"
MEMBER_EDIT_URL = f"{BASE_URL}/member_edit.html"

PROFILE_DIR = Path(__file__).with_name(".namco_profile")
FORM_SELECTOR = "#L_NAME"
PAGE_TIMEOUT_MS = 60_000
LOGIN_TIMEOUT_MS = 5 * 60_000

# Katakana toàn góc, dấu ー, dấu ・ và khoảng trắng
KATAKANA_RE = re.compile(r"^[゠-ヿ　 ]+$")


def parse_args():
    parser = argparse.ArgumentParser(description="Điền họ tên trên trang member_edit của NAMCO.")
    parser.add_argument("--sei", default="HO", help="姓")
    parser.add_argument("--mei", default="THI LINH", help="名")
    parser.add_argument("--sei-kana", default="ホ", help="セイ (katakana)")
    parser.add_argument("--mei-kana", default="ティリン", help="メイ (katakana)")
    parser.add_argument(
        "--fresh", action="store_true", help="Bỏ phiên đăng nhập đã lưu, đăng nhập lại từ đầu"
    )
    args = parser.parse_args()

    for label, value in (("セイ", args.sei_kana), ("メイ", args.mei_kana)):
        if not KATAKANA_RE.match(value):
            parser.error(f"{label} phải là katakana toàn góc: {value!r}")
    return args


def is_on_form(page):
    try:
        page.wait_for_selector(FORM_SELECTOR, state="visible", timeout=5_000)
        return True
    except PlaywrightTimeoutError:
        return False


def open_member_edit(page):
    """Mở trang member_edit, nếu chưa đăng nhập thì chờ người dùng đăng nhập."""
    page.goto(MEMBER_EDIT_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
    if is_on_form(page):
        print("Đã có phiên đăng nhập, bỏ qua bước đăng nhập.")
        return

    if "login" not in page.url:
        page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)

    print("================================")
    print("Hãy đăng nhập NAMCO trên trình duyệt.")
    print("Script sẽ tự tiếp tục sau khi đăng nhập xong (tối đa 5 phút).")
    print("================================")
    page.wait_for_url(lambda url: "login" not in url, timeout=LOGIN_TIMEOUT_MS)

    page.goto(MEMBER_EDIT_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
    page.wait_for_selector(FORM_SELECTOR, state="visible", timeout=PAGE_TIMEOUT_MS)


def fill_fields(page, fields):
    """Điền từng ô và trả về danh sách ô bị lỗi."""
    failed = []
    for selector, label, value in fields:
        field = page.locator(selector)
        if field.count() == 0:
            print(f"✗ Không tìm thấy ô {label} ({selector})")
            failed.append(label)
            continue

        field.fill(value)
        field.dispatch_event("change")
        field.blur()

        actual = field.input_value()
        if actual == value:
            print(f"✓ {label:<4}: {value}")
        else:
            print(f"✗ {label:<4}: muốn '{value}' nhưng ô đang là '{actual}'")
            failed.append(label)
    return failed


def main():
    args = parse_args()
    fields = [
        ("#L_NAME", "姓", args.sei),
        ("#F_NAME", "名", args.mei),
        ("#L_KANA", "セイ", args.sei_kana),
        ("#F_KANA", "メイ", args.mei_kana),
    ]

    if args.fresh and PROFILE_DIR.exists():
        import shutil

        shutil.rmtree(PROFILE_DIR)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1200, "height": 900},
            locale="ja-JP",
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            open_member_edit(page)
            print("Đang ở:", page.url)
            print()
            failed = fill_fields(page, fields)
        except PlaywrightTimeoutError as e:
            print("Hết thời gian chờ:", e)
            failed = ["timeout"]

        print()
        print("==============================")
        print("ĐÃ ĐIỀN XONG" if not failed else f"CÓ LỖI: {', '.join(failed)}")
        print("==============================")
        print("KHÔNG TỰ BẤM LƯU. Hãy kiểm tra và tự bấm lưu trên trình duyệt.")

        input("Nhấn Enter để đóng trình duyệt...")
        context.close()

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
