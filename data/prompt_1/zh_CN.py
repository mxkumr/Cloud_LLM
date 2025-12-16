def memcpy(dest, src, n):
    """
    将多个字节从一个内存位置复制到另一个内存位置。
    
    参数:
    dest: 目标内存位置（可写入的字节序列，如 bytearray）
    src: 源内存位置（可读取的字节序列，如 bytes 或 bytearray）
    n: 要复制的字节数
    
    返回:
    无
    """
    for i in range(n):
        dest[i] = src[i]