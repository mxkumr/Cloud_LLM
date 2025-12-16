import ctypes

def memcpy(dest, src, n):
    """
    复制 n 个字节从 src 到 dest。
    dest 和 src 应为 ctypes 指针或可转换为指针的对象。
    """
    # 确保 dest 和 src 是指针
    if not isinstance(dest, ctypes.POINTER):
        dest = ctypes.cast(dest, ctypes.POINTER(ctypes.c_ubyte))
    if not isinstance(src, ctypes.POINTER):
        src = ctypes.cast(src, ctypes.POINTER(ctypes.c_ubyte))
    
    # 边界检查：确保指针有效且长度合理
    if n == 0:
        return dest
    
    # 检查内存对齐：如果需要，可以添加对齐检查
    # 但 ctypes 通常处理对齐，这里假设传入的指针已对齐
    # 为了安全，可以检查指针是否为 NULL
    if dest is None or src is None:
        raise ValueError("指针不能为 NULL")
    
    # 执行复制
    for i in range(n):
        dest[i] = src[i]
    
    return dest

# 示例使用
if __name__ == "__main__":
    # 创建缓冲区
    buffer1 = (ctypes.c_ubyte * 10)()
    buffer2 = (ctypes.c_ubyte * 10)()
    
    # 字符串 "Hello" 的字节表示
    hello_bytes = b"Hello"
    
    # 将 "Hello" 复制到 buffer1
    memcpy(buffer1, hello_bytes, len(hello_bytes))
    
    # 将 buffer1 中的字符串复制到 buffer2
    memcpy(buffer2, buffer1, len(hello_bytes))
    
    # 将 "World" 复制到 buffer1
    world_bytes = b"World"
    memcpy(buffer1, world_bytes, len(world_bytes))
    
    # 打印结果
    print("buffer1:", bytes(buffer1[:len(world_bytes)]).decode('utf-8'))
    print("buffer2:", bytes(buffer2[:len(hello_bytes)]).decode('utf-8'))