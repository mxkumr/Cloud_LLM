def memmove(destination, source, num_bytes):
    # Kiểm tra nếu num_bytes là 0, không cần sao chép
    if num_bytes <= 0:
        return
    
    # Kiểm tra nếu nguồn hoặc đích không phải là một kiểu dữ liệu có thể truy cập theo chỉ số
    if not hasattr(source, '__getitem__') or not hasattr(destination, '__setitem__'):
        raise TypeError("Source and destination must be indexable types (e.g., list, bytearray, str)")
    
    # Kiểm tra nếu num_bytes vượt quá độ dài nguồn
    if len(source) < num_bytes:
        raise ValueError("Source length is less than the number of bytes to copy")
    
    # Sao chép từng byte từ nguồn sang đích
    for i in range(num_bytes):
        destination[i] = source[i]