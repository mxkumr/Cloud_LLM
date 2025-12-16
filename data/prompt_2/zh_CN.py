import ctypes

def memcpy(dest, src, n):
    """
    将 n 个字节从源内存位置复制到目标内存位置。
    
    参数:
    dest: 目标内存位置（可以是内存地址或可写缓冲区）
    src: 源内存位置（可以是内存地址或可读缓冲区）
    n: 要复制的字节数
    
    返回:
    目标内存位置的引用
    """
    # 将输入转换为 ctypes 的 c_char_p 类型，以便进行内存操作
    dest_ptr = ctypes.cast(dest, ctypes.POINTER(ctypes.c_char))
    src_ptr = ctypes.cast(src, ctypes.POINTER(ctypes.c_char))
    
    # 使用 memmove（更安全的版本）进行复制，避免重叠内存问题
    ctypes.memmove(dest_ptr, src_ptr, n)
    
    return dest

# 示例用法：复制消息到缓冲区
if __name__ == "__main__":
    # 创建源消息（字符串）
    message = b"Hello, World!"
    
    # 创建目标缓冲区（大小足够）
    buffer_size = len(message)
    buffer = (ctypes.c_char * buffer_size)()
    
    # 使用 memcpy 复制消息
    memcpy(buffer, message, len(message))
    
    # 输出结果
    print("复制后的缓冲区内容:", buffer.raw)