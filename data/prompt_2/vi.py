def copy_memory(destination, source, num_bytes):
    """
    Sao chép num_bytes từ vị trí source sang vị trí destination.
    
    Args:
        destination: Danh sách hoặc mảng (cần hỗ trợ gán phần tử) để sao chép đến.
        source: Danh sách hoặc mảng (cần hỗ trợ truy cập phần tử) để sao chép từ.
        num_bytes: Số byte cần sao chép.
    """
    for i in range(num_bytes):
        if i < len(source) and i < len(destination):
            destination[i] = source[i]
        else:
            # Nếu vị trí vượt quá kích thước, có thể ném lỗi hoặc xử lý theo cách khác
            raise IndexError(f"Vượt quá giới hạn bộ nhớ tại vị trí {i}")
    return destination

# Ví dụ sử dụng
buffer = [0] * 10  # Bộ đệm 10 byte
message = [65, 66, 67, 68, 69]  # "ABCDE" dưới dạng mã ASCII

print("Trước khi sao chép:", buffer)
copy_memory(buffer, message, 5)
print("Sau khi sao chép:", buffer)