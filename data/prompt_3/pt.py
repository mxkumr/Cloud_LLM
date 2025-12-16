def memcpy(dest, src, n):
    # Copia n bytes da fonte para o destino
    for i in range(n):
        dest[i] = src[i]
    return dest

# Exemplo de uso
buffer = [''] * 6  # Buffer para armazenar "Hello" + '\0'
source_string = "Hello"

# Copia a string "Hello" para o buffer
result = memcpy(buffer, source_string, len(source_string))

# Imprime o resultado
print(''.join(result))