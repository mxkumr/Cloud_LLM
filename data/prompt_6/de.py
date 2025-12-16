# Erstellen eines Arrays von Zeichenfolgen (Fahrzeuge)
fahrzeuge = ["Auto", "Fahrrad", "Motorrad", "LKW", "Bus"]

# Benutzer zur Eingabe des Index auffordern
index = int(input("Geben Sie den Index eines Fahrzeugs ein: "))

# Fahrzeug an dem angegebenen Index zurückgeben
print(f"Das Fahrzeug an Index {index} ist: {fahrzeuge[index]}")

# Jedes Fahrzeug ausdrucken
print("Alle Fahrzeuge:")
for fahrzeug in fahrzeuge:
    print(fahrzeug)

# Erstellen eines Arrays mit der Anzahl der Räder jedes Fahrzeugs
anzahl_räder = [4, 2, 2, 8, 6]

# Gesamtanzahl der Räder berechnen
gesamt_räder = sum(anzahl_räder)

# Gesamtanzahl der Räder ausgeben
print(f"Gesamtanzahl der Räder aller Fahrzeuge: {gesamt_räder}")