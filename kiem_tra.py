"""
Script chẩn đoán: mở trang đăng nhập và in ra TẤT CẢ ô nhập + nút bấm
để xác định đúng selector. Không đăng nhập, chỉ xem cấu trúc trang.
"""
from playwright.sync_api import sync_playwright

URL = (
    "https://parks2.bandainamco-am.co.jp/"
    "login.html?request=redirect_logon"
    "&redirectTo=member_history.html"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    trang = browser.new_page()
    trang.goto(URL, wait_until="domcontentloaded", timeout=60000)
    trang.wait_for_timeout(3000)

    print("\n====== URL hiện tại ======")
    print(trang.url)

    print("\n====== CÁC Ô NHẬP (input) ======")
    inputs = trang.locator("input")
    for i in range(inputs.count()):
        o = inputs.nth(i)
        try:
            print(f"[{i}] type={o.get_attribute('type')!r} "
                  f"name={o.get_attribute('name')!r} "
                  f"id={o.get_attribute('id')!r} "
                  f"placeholder={o.get_attribute('placeholder')!r} "
                  f"visible={o.is_visible()}")
        except Exception as e:
            print(f"[{i}] (không đọc được: {e})")

    print("\n====== CÁC NÚT (button) ======")
    buttons = trang.locator("button")
    for i in range(buttons.count()):
        o = buttons.nth(i)
        try:
            print(f"[{i}] text={o.inner_text()!r} "
                  f"type={o.get_attribute('type')!r} "
                  f"id={o.get_attribute('id')!r} "
                  f"visible={o.is_visible()}")
        except Exception as e:
            print(f"[{i}] (không đọc được: {e})")

    print("\n====== NÚT dạng input[type=submit] ======")
    subs = trang.locator('input[type="submit"]')
    for i in range(subs.count()):
        o = subs.nth(i)
        try:
            print(f"[{i}] value={o.get_attribute('value')!r} "
                  f"id={o.get_attribute('id')!r} "
                  f"visible={o.is_visible()}")
        except Exception as e:
            print(f"[{i}] (không đọc được: {e})")

    print("\n====== LINK có chữ đăng nhập (a) ======")
    links = trang.locator("a")
    for i in range(links.count()):
        o = links.nth(i)
        try:
            txt = o.inner_text().strip()
            if txt and ("ログイン" in txt or "login" in txt.lower()
                        or "ログオン" in txt):
                print(f"[{i}] text={txt!r} href={o.get_attribute('href')!r}")
        except Exception:
            pass

    print("\nĐã in xong. Xem kết quả ở trên rồi gửi cho mình.")
    input("Nhấn Enter để đóng trình duyệt...")
    browser.close()
