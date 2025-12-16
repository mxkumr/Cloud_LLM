def copy_bytes(destination, source, num_bytes):
    # Определяем количество байтов, которое можно скопировать
    available_bytes = min(num_bytes, len(source))
    
    # Копируем байты из source в destination
    for i in range(available_bytes):
        destination[i] = source[i]
    
    return available_bytes