import sys

# Verifica se foram passados exatamente dois argumentos
if len(sys.argv) != 3:
    print("Erro: O programa deve ser executado com dois argumentos da linha de comando.")
    sys.exit(1)

# Obtém o índice do segundo argumento (índice 1)
INDEX = int(sys.argv[1])

# Verifica se o índice está dentro dos limites dos argumentos
if INDEX < 0 or INDEX >= len(sys.argv):
    print(f"Erro: O índice {INDEX} está fora dos limites dos argumentos.")
    sys.exit(1)

# Obtém o argumento na posição INDEX
arg_value = sys.argv[INDEX]

# Imprime o valor do argumento na posição INDEX
print(arg_value)

# Imprime o valor do argumento na posição INDEX convertido em inteiro
int_value = int(arg_value)
print(int_value)

# Imprime o valor do argumento na posição INDEX convertido em inteiro, multiplicado por 2
print(int_value * 2)

# Imprime o valor do argumento na posição INDEX convertido em inteiro, multiplicado por 2 e convertido em string
str_value = str(int_value * 2)
print(str_value)

# Imprime o valor do argumento na posição INDEX convertido em inteiro, multiplicado por 2 e convertido em string, seguido do valor do argumento na posição INDEX convertido em inteiro, multiplicado por 2 e convertido em string
print(str_value + str_value)