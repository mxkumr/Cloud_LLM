vehicle = ["car", "truck", "motorcycle", "bicycle", "bus"]

index = int(input("Enter the index of the vehicle: "))
print("Selected vehicle:", vehicle[index])

print("All vehicles:")
for v in vehicle:
    print(v)

print("Length of the vehicle list:", len(vehicle))