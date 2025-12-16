vehicles = ["Car", "Bike", "Truck", "Bus", "Motorcycle"]

# Prompt the user to enter the index
index_input = input("Enter the index of the vehicle: ")

# Convert the index input to an integer
try:
    index = int(index_input)
    
    # Check if the index is valid
    if 0 <= index < len(vehicles):
        vehicle = vehicles[index]
        print(f"Vehicle name: {vehicle}")
        print(f"Parts of {vehicle}:")
        # Assuming each vehicle has parts represented as a list
        parts = {
            "Car": ["Engine", "Wheels", "Doors", "Seats", "Steering Wheel"],
            "Bike": ["Engine", "Wheels", "Handlebars", "Saddle", "Chain"],
            "Truck": ["Engine", "Wheels", "Trailer", "Cab", "Horns"],
            "Bus": ["Engine", "Wheels", "Doors", "Seats", "Air Conditioner"],
            "Motorcycle": ["Engine", "Wheels", "Handlebars", "Saddle", "Exhaust"]
        }
        for part in parts[vehicle]:
            print(f"  - {part}")
    else:
        print("Invalid index! Please enter a valid index within the range.")
except ValueError:
    print("Invalid input! Please enter a valid integer.")