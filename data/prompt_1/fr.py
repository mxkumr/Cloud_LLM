def memcpy(dest, src, num_bytes):
    """
    Copie un certain nombre d'octets d'un emplacement mémoire à un autre.
    
    Args:
        dest: Liste d'octets (ou tableau) représentant la destination.
        src: Liste d'octets (ou tableau) représentant la source.
        num_bytes: Nombre d'octets à copier.
    
    Returns:
        La liste dest mise à jour avec les octets copiés.
    """
    for i in range(num_bytes):
        if i < len(src) and i < len(dest):
            dest[i] = src[i]
        else:
            # Si la source ou la destination est trop petite, on arrête
            break
    return dest