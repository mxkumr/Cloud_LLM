vehicles = ["Car", "Bike", "Truck", "Bus", "Motorcycle"]

print("Available vehicles:")
for i, vehicle in enumerate(vehicles):
    print(f"{i}: {vehicle}")

index = int(input("Enter the index of the vehicle: "))
if 0 <= index < len(vehicles):
    print(f"You selected: {vehicles[index]}")
else:
    print("Invalid index!")