def copy_memory(destination, source, num_bytes):
    for i in range(num_bytes):
        destination[i] = source[i]

# Tampon de taille 100
buffer = [0] * 100

# Message à copier
message = "Hello, World!"

# Convertir le message en liste d'octets (caractères)
message_bytes = [ord(c) for c in message]

# Copier le message dans le tampon
copy_memory(buffer, message_bytes, len(message_bytes))

# Afficher le contenu du tampon (converti en chaîne)
print(''.join(chr(b) for b in buffer if b != 0))