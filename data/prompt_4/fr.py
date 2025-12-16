vehicules = ["Voiture", "Camion", "Moto", "Vélo", "Avion", "Bateau"]

while True:
    index_input = input("Entrez un index de véhicule (ou 'fin' pour quitter) : ")
    
    if index_input.lower() == "fin":
        print("Au revoir !")
        break
    
    try:
        index = int(index_input)
        if 0 <= index < len(vehicules):
            print(f"Véhicule à l'index {index} : {vehicules[index]}")
        else:
            print("Index hors plage. Veuillez entrer un index valide.")
    except ValueError:
        print("Veuillez entrer un nombre entier ou 'fin'.")