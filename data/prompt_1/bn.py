def copy_memory(destination, source, byte_count):
    for i in range(byte_count):
        destination[i] = source[i]