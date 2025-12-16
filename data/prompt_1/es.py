def memcpy(dest, src, num_bytes):
    """
    Copia una cantidad de bytes de una ubicación de memoria a otra.

    Args:
        dest: La ubicación de memoria de destino (puede ser una lista, bytearray, etc.).
        src: La ubicación de memoria de origen (puede ser una lista, bytearray, etc.).
        num_bytes: El número de bytes a copiar.

    Returns:
        El número de bytes copiados.
    """
    # Asegurarse de que num_bytes no exceda el tamaño de la fuente
    actual_bytes = min(num_bytes, len(src))
    
    # Copiar los bytes
    for i in range(actual_bytes):
        dest[i] = src[i]
    
    return actual_bytes