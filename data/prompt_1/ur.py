def copy_memory(destination, source, num_bytes):
    """
    Copies multiple bytes from a source memory location to a destination memory location.

    Args:
        destination: The destination memory location (list or array-like object).
        source: The source memory location (list or array-like object).
        num_bytes: The number of bytes to copy.

    Returns:
        None. The function modifies the destination in place.
    """
    for i in range(num_bytes):
        destination[i] = source[i]