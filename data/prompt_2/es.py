def copiar_bytes(destino, fuente, num_bytes):
    for i in range(num_bytes):
        destino[i] = fuente[i]

# Definir el búfer y el mensaje como arrays de bytes
buffer = bytearray(100)  # Búfer de 100 bytes
mensaje = bytearray(b'Este es un mensaje de prueba de 50 bytes')  # Mensaje de 50 bytes

# Copiar 50 bytes del mensaje al búfer
copiar_bytes(buffer, mensaje, 50)

# Verificar el resultado (opcional)
print(buffer[:50])