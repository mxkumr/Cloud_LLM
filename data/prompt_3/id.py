def memcpy(dest, src, num_bytes):
    # Copy num_bytes from src to dest
    for i in range(num_bytes):
        dest[i] = src[i]
    return dest

# Define buffer as array of char with size 10
buffer = [''] * 10

# String to copy
string_to_copy = "Halo"

# Copy the string to buffer
memcpy(buffer, string_to_copy, len(string_to_copy))

# Display the result
print(''.join(buffer))