def copy_bytes(destination, source, num_bytes):
    """
    Copies a number of bytes from source to destination.
    
    Args:
        destination: The destination memory location (list or bytearray).
        source: The source memory location (list or bytearray).
        num_bytes: The number of bytes to copy.
    
    Returns:
        The destination pointer (the modified destination list or bytearray).
    """
    # Ensure we don't copy more bytes than available in source
    num_bytes = min(num_bytes, len(source))
    
    # Copy the bytes from source to destination
    for i in range(num_bytes):
        destination[i] = source[i]
    
    return destination