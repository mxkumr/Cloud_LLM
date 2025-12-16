def copy_bytes(destination, source, num_bytes):
    for i in range(num_bytes):
        destination[i] = source[i]

# Example usage
buffer = bytearray(5)  # Allocate space for 5 bytes
source_string = "हॅलो"
source_bytes = source_string.encode('utf-8')

# Copy bytes from source to buffer
copy_bytes(buffer, source_bytes, len(source_bytes))

# Print the output
print(buffer.decode('utf-8'))