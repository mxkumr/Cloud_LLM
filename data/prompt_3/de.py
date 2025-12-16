def memcpy(dest, src, num_bytes):
    # Kopiert num_bytes von src nach dest
    for i in range(num_bytes):
        dest[i] = src[i]

# Beispiel: Kopiert die Zeichenfolge "Hello" in einen Puffer von 100 Bytes
buffer = bytearray(100)  # 100-Byte-Puffer
source_string = b"Hello"

# Kopiere die Bytes von source_string in den Puffer
memcpy(buffer, source_string, len(source_string))

# Ausgabe des Ergebnisses (optional)
print(buffer[:len(source_string)])  # Gibt b'Hello' aus