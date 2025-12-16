def copy_bytes(destination, source, num_bytes):
    # Copy num_bytes from source to destination
    for i in range(num_bytes):
        destination[i] = source[i]

# Example usage:
# Create a source buffer with the string "hello"
source_buffer = bytearray(b"hello")
# Create a destination buffer of the same size
destination_buffer = bytearray(len(source_buffer))

# Copy bytes from source to destination
copy_bytes(destination_buffer, source_buffer, len(source_buffer))

# Output the result
print(destination_buffer.decode('utf-8'))