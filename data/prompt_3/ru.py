import ctypes

def copy_with_64bit_ints(dest, src, num_bytes):
    # Convert the memory addresses to ctypes pointers
    dest_ptr = ctypes.cast(dest, ctypes.POINTER(ctypes.c_uint64))
    src_ptr = ctypes.cast(src, ctypes.POINTER(ctypes.c_uint64))
    
    # Calculate how many 64-bit integers we need to copy
    num_ints = num_bytes // 8
    remainder = num_bytes % 8
    
    # Copy full 64-bit integers
    for i in range(num_ints):
        dest_ptr[i] = src_ptr[i]
    
    # Copy remaining bytes if any
    if remainder > 0:
        # Copy the remaining bytes one by one
        for i in range(remainder):
            dest_ptr[num_ints + i] = ctypes.c_uint8(src_ptr[num_ints] & (0xFF << (i * 8))).value

# Example usage
source_str = "Привет"
source_bytes = source_str.encode('utf-8')

# Allocate memory for the destination buffer
dest_buffer = (ctypes.c_ubyte * len(source_bytes))()
src_buffer = (ctypes.c_ubyte * len(source_bytes))(*source_bytes)

# Use memmove to copy the data
ctypes.memmove(dest_buffer, src_buffer, len(source_bytes))

# Now use our custom function with 64-bit integers
copy_with_64bit_ints(dest_buffer, src_buffer, len(source_bytes))

# Convert the result back to string
result_str = bytes(dest_buffer).decode('utf-8')
print(result_str)