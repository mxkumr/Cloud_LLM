def copy_bytes(destination, source, num_bytes):
    """
    Copies a specified number of bytes from a source memory location to a destination memory location.

    Parameters:
    - destination: The destination memory location (list or bytearray).
    - source: The source memory location (list or bytearray).
    - num_bytes: The number of bytes to copy.

    Returns:
    - None (modifies the destination in-place).
    """
    for