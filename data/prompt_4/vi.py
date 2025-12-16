# Danh sách xe
xe = ["Toyota", "Honda", "Ford", "BMW", "Mercedes"]

# Nhập chỉ mục từ người dùng
chuoi_chỉ_mục = input("Nhập chỉ mục của chiếc xe: ")

# Chuyển đổi chuỗi thành số nguyên
chỉ_mục = int(chuoi_chỉ_mục)

# Kiểm tra chỉ mục có hợp lệ không
if 0 <= chỉ_mục < len(xe):
    print(xe[đ只_mục])
else:
    print("Chỉ số không hợp lệ")