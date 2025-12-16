# Definimos una lista de vehículos
vehiculos = ["Automóvil", "Camión", "Motocicleta", "Bicicleta", "Avión"]

# Solicitamos al usuario que ingrese un índice
indice_str = input("Ingrese el índice de un vehículo: ")

try:
    # Convertimos el índice a número entero
    indice = int(indice_str)
    
    # Verificamos si el índice está dentro del rango válido
    if 0 <= indice < len(vehiculos):
        print(f"El vehículo en el índice {indice} es: {vehiculos[indice]}")
    else:
        print("Error: El índice ingresado no es válido.")
        
except ValueError:
    print("Error: Por favor, ingrese un número entero válido.")