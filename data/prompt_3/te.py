def copy_memory(destination, source, num_bytes):
    # Copy num_bytes from source to destination
    for i in range(num_bytes):
        destination[i] = source[i]

# Example usage
buffer = [0] * 5  # Buffer to hold the copied data
source_string = "Hello"
source_bytes = source_string.encode('utf-8')

# Copy the bytes from source to buffer
copy_memory(buffer, source_bytes, len(source_bytes))

# Print the copied bytes
print(buffer)