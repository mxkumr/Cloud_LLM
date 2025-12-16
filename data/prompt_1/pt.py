def memcpy(dest, src, num_bytes):
    """
    Copia um número de bytes de um local de memória para outro.

    Args:
        dest: Lista ou array que representa o destino da cópia.
        src: Lista ou array que representa a fonte da cópia.
        num_bytes: Número de bytes a serem copiados.

    Returns:
        O número de bytes copiados.
    """
    # Limita o número de bytes ao tamanho da fonte
    num_bytes = min(num_bytes, len(src))
    
    # Copia os bytes do src para o dest
    for i in range(num_bytes):
        dest[i] = src[i]
    
    return num_bytes