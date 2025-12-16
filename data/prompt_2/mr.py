def memcpy(destination, source, num_bytes):
    """
    Copy num_bytes from source to destination.
    
    Args:
        destination: The destination memory location (list or array-like object).
        source: The source memory location (list or array-like object).
        num_bytes: The number of bytes to copy.
    
    Returns:
        None. The function modifies the destination in place.
    """
    if num_bytes == 0:
        return
    
    for i in range(num_bytes):
        destination[i] = source[i]