# Tạo mảng các chuỗi gọi là phương tiện
phuong_tien = ["Xe đạp", "Xe máy", "Ô tô", "Xe buýt", "Tàu hỏa"]

# Nhập chỉ số của một chiếc xe từ người dùng
chi_so = int(input("Nhập chỉ số của chiếc xe bạn muốn tìm: "))

# Trả về chiếc xe tại chỉ số đó
if 0 <= chi_so < len(phuong_tien):
    print(f"Chiếc xe tại chỉ số {chi_so} là: {phuong_tien[chi_so]}")
else:
    print("Chỉ số không hợp lệ!")

# Lặp qua mảng và in ra từng chiếc xe
print("\nDanh sách các phương tiện:")
for i, xe in enumerate(phuong_tien):
    print(f"{i}: {xe}")

# In ra số lượng xe trong mảng
print(f"\nTổng số lượng xe: {len(phuong_tien)}")