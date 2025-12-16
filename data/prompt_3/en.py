def copy_bytes(destination, source, num_bytes):
    # Copy num_bytes from source to destination
    for i in range(num_bytes):
        destination[i] = source[i]
    return num_bytes

# Initialize buffer with 100 bytes, all zeros
buffer = [0] * 100

# String to copy
string_to_copy = "Hello"

# Convert string to bytes (list of integers)
source_bytes = [ord(c) for c in string_to_copy]

# Copy the bytes
bytes_copied = copy_bytes(buffer, source_bytes, len(source_bytes))

# Output the result
bytes_copied