"""Điền sẵn họ tên trên trang thay đổi thông tin thành viên NAMCO.

- Lưu phiên đăng nhập vào thư mục profile, lần sau không cần đăng nhập lại.
- Tự nhận ra khi bạn mở trang sửa thông tin, không cần quay lại Terminal nhấn Enter.
- Nhớ URL trang sửa thông tin, lần sau mở thẳng.
- Kiểm tra lại giá trị sau khi điền.
- KHÔNG tự bấm lưu.

Ví dụ:
    python namco_member_edit.py
    python namco_member_edit.py --sei HO --mei "THI LINH" --sei-kana ホ --mei-kana ティリン
"""

import argparse
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

BASE_URL = "https://parks2.bandainamco-am.co.jp"
LOGIN_URL = f"{BASE_URL}/login.html"
DEFAULT_EDIT_URL = f"{BASE_URL}/member_regist.html?request=edit"

PROFILE_DIR = Path(__file__).with_name(".namco_profile")
# Lưu URL trang sửa thông tin tìm được, lần sau mở thẳng
EDIT_URL_FILE = Path(__file__).with_name(".namco_edit_url")
FORM_SELECTOR = "#L_NAME"
PAGE_TIMEOUT_MS = 60_000
FILL_TIMEOUT_MS = 5_000
WAIT_FORM_TIMEOUT_S = 10 * 60

# Katakana toàn góc, dấu ー, dấu ・ và khoảng trắng
KATAKANA_RE = re.compile(r"^[゠-ヿ　 ]+$")


def parse_args():
    parser = argparse.ArgumentParser(description="Điền họ tên trên trang member_edit của NAMCO.")
    parser.add_argument("--sei", default="HO", help="姓")
    parser.add_argument("--mei", default="THI LINH", help="名")
    parser.add_argument("--sei-kana", default="ホ", help="セイ (katakana)")
    parser.add_argument("--mei-kana", default="ティリン", help="メイ (katakana)")
    parser.add_argument("--url", help="URL trang sửa thông tin (mặc định: URL đã lưu lần trước)")
    parser.add_argument(
        "--fresh", action="store_true", help="Bỏ phiên đăng nhập đã lưu, đăng nhập lại từ đầu"
    )
    args = parser.parse_args()

    for label, value in (("セイ", args.sei_kana), ("メイ", args.mei_kana)):
        if not KATAKANA_RE.match(value):
            parser.error(f"{label} phải là katakana toàn góc: {value!r}")
    return args


def find_form_page(context):
    """Trả về tab đang có form sửa họ tên, không có thì trả về None."""
    for pg in context.pages:
        try:
            if pg.locator(FORM_SELECTOR).first.is_visible():
                return pg
        except PlaywrightError:
            pass
    return None


def open_member_edit(context, page, url):
    """Mở trang sửa thông tin và trả về tab có form.

    Nếu đã biết URL (lưu từ lần trước hoặc --url) thì mở thẳng. Nếu không,
    người dùng tự đăng nhập và bấm vào trang sửa thông tin, script tự nhận ra form.
    """
    if url:
        page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        try:
            page.wait_for_selector(FORM_SELECTOR, state="visible", timeout=5_000)
            print("Đã mở thẳng trang sửa thông tin.")
            return page
        except PlaywrightTimeoutError:
            pass

    page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
    print("================================")
    print("1. Đăng nhập NAMCO trên cửa sổ Chrome vừa mở.")
    print("2. Tự bấm vào trang thay đổi thông tin thành viên (会員情報変更).")
    print("3. Khi form hiện ra, script sẽ tự điền (chờ tối đa 10 phút).")
    print("================================")

    deadline = time.monotonic() + WAIT_FORM_TIMEOUT_S
    while time.monotonic() < deadline:
        form_page = find_form_page(context)
        if form_page:
            EDIT_URL_FILE.write_text(form_page.url, encoding="utf-8")
            return form_page
        time.sleep(1)
    raise PlaywrightTimeoutError("Không thấy form sửa họ tên sau 10 phút.")


def fill_fields(page, fields):
    """Điền từng ô đang hiển thị và trả về danh sách ô bị lỗi.

    Ô ẩn (type="hidden") là ô trang không cho sửa, nên bỏ qua chứ không ép giá trị.
    """
    failed = []
    for selector, label, value in fields:
        field = page.locator(f"{selector}:visible").first
        if field.count() == 0:
            if page.locator(selector).count() > 0:
                print(f"✗ {label:<4}: ô {selector} bị ẩn, trang không cho sửa ở đây")
            else:
                print(f"✗ {label:<4}: không tìm thấy ô {selector}")
            failed.append(label)
            continue

        try:
            field.fill(value, timeout=FILL_TIMEOUT_MS)
            field.dispatch_event("change")
            field.blur()
            actual = field.input_value()
        except PlaywrightError as e:
            print(f"✗ {label:<4}: không điền được ({e.message.splitlines()[0]})")
            failed.append(label)
            continue

        if actual == value:
            print(f"✓ {label:<4}: {value}")
        else:
            print(f"✗ {label:<4}: muốn '{value}' nhưng ô đang là '{actual}'")
            failed.append(label)
    return failed


def print_visible_inputs(page):
    """In các ô nhập chữ đang hiển thị để tìm đúng id của ô cần điền."""
    inputs = page.eval_on_selector_all(
        "input:not([type=hidden]):not([type=checkbox]):not([type=radio])"
        ":not([type=submit]):not([type=button]), textarea",
        """els => els.filter(e => e.offsetParent !== null).map(e => ({
            id: e.id, name: e.name, value: e.value,
            label: (e.labels && e.labels[0] ? e.labels[0].innerText : "").trim()
        }))""",
    )
    print()
    print("Các ô nhập đang hiển thị trên trang (gửi phần này để sửa script):")
    for i in inputs:
        print(f"  id={i['id']!r} name={i['name']!r} value={i['value']!r} label={i['label']!r}")


def main():
    args = parse_args()
    fields = [
        ("#L_NAME", "姓", args.sei),
        ("#F_NAME", "名", args.mei),
        ("#L_KANA", "セイ", args.sei_kana),
        ("#F_KANA", "メイ", args.mei_kana),
    ]

    if args.fresh:
        import shutil

        shutil.rmtree(PROFILE_DIR, ignore_errors=True)
        EDIT_URL_FILE.unlink(missing_ok=True)

    url = args.url
    if not url and EDIT_URL_FILE.exists():
        url = EDIT_URL_FILE.read_text(encoding="utf-8").strip()
    url = url or DEFAULT_EDIT_URL

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
            viewport={"width": 1200, "height": 900},
            locale="ja-JP",
        )
        page = context.pages[0] if context.pages else context.new_page()

        try:
            page = open_member_edit(context, page, url)
            page.bring_to_front()
            print("Đang ở:", page.url)
            print()
            failed = fill_fields(page, fields)
            if failed:
                print_visible_inputs(page)
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
