import sys

# Créer un tableau d'éléments
tableau = [10, 20, 30, 40, 50]

# Prendre un argument de ligne de commande et le convertir en entier
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Erreur : Veuillez fournir un argument numérique valide.")
    sys.exit(1)

# Imprimer l'élément à cet index ou un message d'erreur si hors limites
if 0 <= index < len(tableau):
    print(tableau[index])
else:
    print("Erreur : L'index est hors limites.")