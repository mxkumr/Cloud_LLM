veiculos = ["Carro", "Moto", "Bicicleta", "Triciclo", "Caminhão"]

# Solicita ao usuário o índice de um veículo
indice = int(input("Digite o índice de um veículo (0-4): "))

# Retorna o veículo com base no índice
print(f"Veículo no índice {indice}: {veiculos[indice]}")

# Percorre a matriz com um laço for e imprime cada veículo
print("\nLista de veículos (usando for):")
for veiculo in veiculos:
    print(veiculo)

# Percorre a matriz com um laço while e imprime cada veículo
print("\nLista de veículos (usando while):")
indice_while = 0
while indice_while < len(veiculos):
    print(veiculos[indice_while])
    indice_while += 1