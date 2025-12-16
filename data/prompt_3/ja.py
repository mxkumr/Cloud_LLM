def copy_memory(destination, source, byte_count):
    # Copy bytes from source to destination
    for i in range(byte_count):
        destination[i] = source[i]
    return byte_count

# Initialize buffer with "World"
buffer = bytearray(b"World")

# Copy "Hello" to buffer
copy_memory(buffer, b"Hello", 5)

# The buffer now contains "Hello"
print(buffer)  # Output: bytearray(b'Hello')