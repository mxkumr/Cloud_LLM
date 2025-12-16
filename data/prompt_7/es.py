import sys

def string_to_int(s):
    return int(s)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Error: Se requieren al menos dos argumentos en la línea de comandos.")
        sys.exit(1)
    
    try:
        index = string_to_int(sys.argv[1])
        if index == 1:
            print("Hello World")
        elif index == 2:
            print("Hola Mundo")
        elif index == 3:
            print("¡Hola Mundo!")
        else:
            print("Índice no válido")
    except ValueError:
        print("Error: El segundo argumento debe ser un número entero.")