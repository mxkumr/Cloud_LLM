veiculos = ["Carro", "Moto", "Bicicleta", "Caminhão", "Ônibus"]

indice = input("Insira um índice de um veículo: ")
indice = int(indice)

try:
    print(veiculos[indice])
except IndexError:
    print("Índice inválido")