import sys

# Crear una matriz de elementos
matriz = [10, 20, 30, 40, 50]

# Tomar el argumento de línea de comando y convertirlo en entero
try:
    indice = int(sys.argv[1])
except (IndexError, ValueError):
    print("Índice fuera de rango")
    exit()

# Imprimir el elemento en ese índice o un mensaje si está fuera de rango
if 0 <= indice < len(matriz):
    print(matriz[indice])
else:
    print("Índice fuera de rango")