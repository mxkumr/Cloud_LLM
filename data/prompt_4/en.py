vehicles = ["Car", "Bike", "Truck", "Bus", "Motorcycle"]

try:
    index = int(input("Enter an index of a vehicle: "))
    print(vehicles[index])
except IndexError:
    print("Index out of range.")
except ValueError:
    print("Please enter a valid integer.")