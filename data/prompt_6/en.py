vehicles = ["car", "bike", "truck", "bus"]

# Prompt the user for the index of a vehicle
index = int(input("Enter the index of a vehicle: "))
if 0 <= index < len(vehicles):
    print(f"Vehicle at index {index}: {vehicles[index]}")
else:
    print("Invalid index.")

# Loop through the array and print each vehicle
print("Current vehicles:")
for vehicle in vehicles:
    print(vehicle)

# Ask the user to enter a vehicle and add it to the end of the array
new_vehicle = input("Enter a vehicle to add: ")
vehicles.append(new_vehicle)

# Loop through the array and print each vehicle again
print("Updated vehicles:")
for vehicle in vehicles:
    print(vehicle)