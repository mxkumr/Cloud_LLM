import ctypes

def copy_memory(destination, source, num_bytes):
    """
    Копирует определенное количество байтов из одного места памяти в другое.
    
    Аргументы:
    destination: указатель на место назначения (в виде ctypes pointer)
    source: указатель на источник (в виде ctypes pointer)
    num_bytes: количество байтов для копирования (целое число)
    """
    ctypes.memmove(destination, source, num_bytes)