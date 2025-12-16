def memcpy(destination, source, count):
    # Convertir les chaînes en listes de caractères pour pouvoir modifier
    dest_list = list(destination)
    src_list = list(source)
    
    # Copier les octets (caractères) de la source vers la destination
    for i in range(count):
        if i < len(src_list):
            dest_list[i] = src_list[i]
        else:
            # Si la source est plus courte que count, on ne fait rien
            break
    
    # Convertir la liste de retour en chaîne
    return ''.join(dest_list)

# Appel de la fonction avec les paramètres donnés
result = memcpy("Hello", "Bonjour", 7)
print(result)