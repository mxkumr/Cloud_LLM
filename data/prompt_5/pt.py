import sys

# Criar uma matriz de elementos
matriz = [10, 20, 30, 40, 50]

# Receber argumento da linha de comando e convertê-lo em inteiro
try:
    indice = int(sys.argv[1])
except (IndexError, ValueError):
    print("Erro: Por favor, forneça um índice válido como argumento.")
    sys.exit(1)

# Verificar se o índice é válido
if 0 <= indice < len(matriz):
    print(matriz[indice])
else:
    print(f"Erro: Índice {indice} fora dos limites da matriz (0 a {len(matriz)-1}).")