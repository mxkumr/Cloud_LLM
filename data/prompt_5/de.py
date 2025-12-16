import sys

# Erstellen eines Arrays mit Elementen
array = [10, 20, 30, 40, 50]

# Befehlszeilenargument einlesen und in Ganzzahl umwandeln
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Fehler: Bitte ein gültiges Ganzzahl-Argument übergeben.")
    sys.exit(1)

# Prüfen, ob der Index im gültigen Bereich liegt
if 0 <= index < len(array):
    print(array[index])
else:
    print("Fehler: Der Index liegt außerhalb des Arrays.")