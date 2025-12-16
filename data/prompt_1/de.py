def copy_bytes(destination, source, num_bytes):
    current_dest = destination
    current_src = source
    for _ in range(num_bytes):
        byte = read_byte(current_src)
        write_byte(current_dest, byte)
        current_dest += 1
        current_src += 1
    return current_dest - 1