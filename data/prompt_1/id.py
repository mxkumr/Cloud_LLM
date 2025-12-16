import ctypes

def memcpy(dest, src, num_bytes):
    """
    Menyalin sejumlah byte dari lokasi memori sumber ke lokasi memori tujuan.
    
    Args:
        dest: Lokasi memori tujuan (pointer atau objek yang dapat diakses sebagai pointer).
        src: Lokasi memori sumber (pointer atau objek yang dapat diakses sebagai pointer).
        num_bytes: Jumlah byte yang akan disalin.
    
    Returns:
        Jumlah byte yang berhasil disalin.
    """
    # Muat library C
    libc = ctypes.CDLL(None)
    
    # Ambil fungsi memcpy dari library C
    memcpy_func = libc.memcpy
    memcpy_func.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    memcpy_func.restype = ctypes.c_void_p
    
    # Panggil fungsi memcpy
    result = memcpy_func(dest, src, num_bytes)
    
    # Kembalikan jumlah byte yang disalin
    return num_bytes