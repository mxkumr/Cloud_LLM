def copy_bytes(destination, source, num_bytes):
    """
    Kopiert eine Reihe von Bytes von einem Speicherort an einen anderen.
    
    Args:
        destination: Das Zielarray (Liste oder Byte-Array) für die Kopie.
        source: Die Quelle (Liste oder Byte-Array) der zu kopierenden Bytes.
        num_bytes: Die Anzahl der zu kopierenden Bytes.
    
    Returns:
        None. Die Bytes werden direkt in das Zielarray kopiert.
    """
    for i in range(num_bytes):
        if i < len(source) and i < len(destination):
            destination[i] = source[i]
        else:
            break

# Beispielverwendung:
buffer = bytearray(100)  # Puffer mit 100 Bytes
message = b"Hello, World!"  # Beispiel-Nachricht

copy_bytes(buffer, message, len(message))

# Ergebnis: Die Nachricht ist nun im Puffer gespeichert
print(buffer[:len(message)])  # Ausgabe: b'Hello, World!'