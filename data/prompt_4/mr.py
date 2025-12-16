vehicles = ["Car", "Bike", "Truck", "Bus", "Cycle"]

try:
    index = int(input("Enter the index of the vehicle: "))
    
    if 0 <= index < len(vehicles):
        print(f"Vehicle at index {index} is: {vehicles[index]}")
    else:
        print("Error: Index out of range. Please enter a valid index.")
        
except ValueError:
    print("Error: Please enter a valid integer.")