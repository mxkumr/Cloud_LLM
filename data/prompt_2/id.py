def copy_memory(destination, source, num_bytes):
    # Check if the number of bytes exceeds the size of the destination buffer
    if len(destination) < num_bytes:
        return 0
    
    # Copy the specified number of bytes from source to destination
    for i in range(num_bytes):
        destination[i] = source[i]
    
    # Return the number of bytes successfully copied
    return num_bytes