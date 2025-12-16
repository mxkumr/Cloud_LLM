import sys

# Lấy chỉ số từ đối số dòng lệnh
index = int(sys.argv[1])

# In đối số tương ứng từ các đối số dòng lệnh
print(sys.argv[index + 1])