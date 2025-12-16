import sys

if len(sys.argv) > int(sys.argv[1]) + 1:
    print(sys.argv[int(sys.argv[1]) + 1])
else:
    print("Índice fora dos limites dos argumentos da linha de comando.")