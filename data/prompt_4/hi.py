vehicles = ["Car", "Bike", "Truck", "Bus", "Cycle"]

index = input("Enter the index of the vehicle: ")
index = int(index)

if 0 <= index < len(vehicles):
    print(vehicles[index])
else:
    print("Invalid index")