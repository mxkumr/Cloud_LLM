import sys

# Tạo mảng các phần tử
arr = [10, 20, 30, 40, 50]

# Nhận đối số dòng lệnh và chuyển đổi thành số nguyên
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Vui lòng cung cấp một chỉ mục hợp lệ.")
    sys.exit(1)

# Kiểm tra chỉ mục và in phần tử tương ứng
if 0 <= index < len(arr):
    print(arr[index])
else:
    print("Không tìm thấy phần tử tại chỉ mục này")