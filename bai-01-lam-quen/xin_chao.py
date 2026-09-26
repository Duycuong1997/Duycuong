# Bài 1: Làm quen với Python
# Dòng bắt đầu bằng dấu # là "chú thích" — máy tính bỏ qua, chỉ để người đọc hiểu.

# 1. In chữ ra màn hình
print("Xin chào! Mình đang học code.")

# 2. Biến: một "cái hộp" có tên để cất dữ liệu
ten = "Cường"          # chuỗi (chữ) đặt trong dấu ngoặc kép
tuoi = 20              # số nguyên
chieu_cao = 1.72       # số thực (có dấu chấm)

print("Tên:", ten)
print("Tuổi:", tuoi)

# 3. Tính toán
nam_sau = tuoi + 1
print("Năm sau bạn", nam_sau, "tuổi")

# 4. Câu điều kiện: if / else
if tuoi >= 18:
    print("Bạn đã đủ 18 tuổi.")
else:
    print("Bạn chưa đủ 18 tuổi.")

# 5. Vòng lặp: lặp lại một việc nhiều lần
for i in range(1, 6):
    print("Lần lặp thứ", i)
