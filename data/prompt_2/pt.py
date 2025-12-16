def copiar_memoria(destino, fonte, num_bytes):
    """
    Copia um número de bytes de um local de memória para outro.

    Args:
        destino: Lista ou array onde os bytes serão copiados (modificável).
        fonte: Lista ou array de onde os bytes serão copiados.
        num_bytes: Número de bytes a serem copiados.

    Returns:
        int: Número de bytes copiados.
    """
    # Limita o número de bytes a copiar ao tamanho disponível na fonte
    bytes_a_copiar = min(num_bytes, len(fonte))
    
    # Copia os bytes do fonte para o destino
    for i in range(bytes_a_copiar):
        destino[i] = fonte[i]
    
    return bytes_a_copiar