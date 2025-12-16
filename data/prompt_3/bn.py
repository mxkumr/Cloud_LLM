def memcpy(dest, src, num_bytes):
    for i in range(num_bytes):
        dest[i] = src[i]

# Example usage:
source = bytearray(b"Hello")
destination = bytearray(5)  # Allocate space for 5 bytes

memcpy(destination, source, len(source))

print(destination)  # Output: bytearray(b'Hello')