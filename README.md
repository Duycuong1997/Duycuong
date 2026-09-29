# Duycuong

## namco_member_edit.py

Mở trình duyệt, bạn đăng nhập NAMCO rồi tự bấm vào trang thay đổi thông tin thành viên.
Khi form hiện ra, script tự điền 姓 / 名 / セイ / メイ. Phiên đăng nhập (`.namco_profile/`)
và URL trang sửa thông tin (`.namco_edit_url`) được lưu lại, lần sau mở thẳng.
Script **không** tự bấm lưu.

```bash
pip install -r requirements.txt
playwright install chromium
python namco_member_edit.py
```

Đổi giá trị bằng tham số:

```bash
python namco_member_edit.py --sei HO --mei "THI LINH" --sei-kana ホ --mei-kana ティリン
python namco_member_edit.py --fresh   # đăng nhập lại từ đầu, quên URL đã lưu
```
