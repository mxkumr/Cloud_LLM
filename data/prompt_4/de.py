# Beispiel-Fahrzeug-Array
fahrzeuge = ["Auto", "Motorrad", "Fahrrad", "LKW", "Bus"]

# Benutzer auffordern, einen Index einzugeben
index_input = input("Geben Sie den Index eines Fahrzeugs ein: ")

# Versuchen, den Index in eine Ganzzahl umzuwandeln
try:
    index = int(index_input)
    
    # Überprüfen, ob der Index im gültigen Bereich liegt
    if 0 <= index < len(fahrzeuge):
        print(f"Das Fahrzeug am Index {index} ist: {fahrzeuge[index]}")
    else:
        print("Fehler: Der Index liegt außerhalb des gültigen Bereichs.")
        
except ValueError:
    print("Fehler: Bitte geben Sie eine gültige Ganzzahl ein.")