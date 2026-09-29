# Duycuong

## namco_member_edit.py

Mở trình duyệt, chờ bạn đăng nhập NAMCO (tự phát hiện khi đăng nhập xong), rồi điền sẵn
姓 / 名 / セイ / メイ trên trang `member_edit.html`. Phiên đăng nhập được lưu trong
`.namco_profile/` nên lần sau không cần đăng nhập lại. Script **không** tự bấm lưu.

```bash
pip install -r requirements.txt
playwright install chromium
python namco_member_edit.py
```

Đổi giá trị bằng tham số:

```bash
python namco_member_edit.py --sei HO --mei "THI LINH" --sei-kana ホ --mei-kana ティリン
python namco_member_edit.py --fresh   # đăng nhập lại từ đầu
```
