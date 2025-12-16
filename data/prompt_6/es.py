vehiculos = ["Auto", "Camioneta", "Moto", "Bicicleta", "Triciclo"]

while True:
    try:
        indice = int(input("Ingrese el índice de un vehículo (0-4): "))
        if 0 <= indice < len(vehiculos):
            print(f"Vehículo seleccionado: {vehiculos[indice]}")
        else:
            print("Índice fuera de rango. Intente de nuevo.")
            continue
    except ValueError:
        print("Por favor, ingrese un número válido.")
        continue

    print("Todos los vehículos:")
    for vehiculo in vehiculos:
        print(vehiculo)

    continuar = input("¿Desea continuar? (S/N): ").strip().upper()
    if continuar == "N":
        print("Fin del programa.")
        break
    elif continuar != "S":
        print("Respuesta no válida. Por favor, ingrese 'S' para continuar o 'N' para salir.")