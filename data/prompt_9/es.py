import sys

if len(sys.argv) <= 1:
    print("Error: Se requiere un índice como argumento.")
    sys.exit(1)

try:
    index = int(sys.argv[1])
except ValueError:
    print("Error: El índice debe ser un número entero.")
    sys.exit(1)

if index < 0 or index >= len(sys.argv):
    print("Error: El índice proporcionado está fuera del rango de los argumentos.")
    sys.exit(1)

print(sys.argv[index + 1])