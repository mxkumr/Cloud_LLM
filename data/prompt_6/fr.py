# Création d'un tableau de chaînes appelées véhicules
vehicules = ["voiture", "moto", "vélo", "camion", "bus"]

# Demande à l'utilisateur l'index d'un véhicule
index = int(input("Entrez l'index d'un véhicule : "))

# Renvoie le véhicule à l'index spécifié
print(f"Le véhicule à l'index {index} est : {vehicules[index]}")

# Parcours du tableau et impression de chaque véhicule
print("Liste des véhicules :")
for vehicule in vehicules:
    print(vehicule)

# Affichage du nombre total de véhicules dans le tableau
print(f"Nombre total de véhicules : {len(vehicules)}")

# Ajout d'un nouveau véhicule au tableau
nouveau_vehicule = input("Entrez un nouveau véhicule : ")
vehicules.append(nouveau_vehicule)

# Affichage du nouveau tableau
print("Nouveau tableau de véhicules :")
print(vehicules)