def copy_bytes(destination, source, num_bytes):
    # Ensure that the source and destination are bytes-like objects
    if isinstance(source, str):
        source = source.encode('utf-8')
    if isinstance(destination, str):
        destination = destination.encode('utf-8')
    
    # Copy the specified number of bytes from source to destination
    for i in range(num_bytes):
        if i < len(source):
            destination[i] = source[i]
        else:
            break

# Example usage: Copy "hello" string into a buffer
buffer = bytearray(b'\x00' * 10)  # Create a buffer of 10 bytes
copy_bytes(buffer, "hello", 5)
print(buffer)  # Output: bytearray(b'hello\x00\x00\x00\x00')