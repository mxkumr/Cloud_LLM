vehicles = ["Car", "Bike", "Truck", "Bus"]

for i in range(len(vehicles)):
    print(f"Enter the location of {vehicles[i]}: ", end="")
    location = input()
    vehicles[i] = f"{vehicles[i]} at {location}"

for vehicle in vehicles:
    print(vehicle)