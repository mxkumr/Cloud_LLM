import sys

# Create an array of elements
elements = [10, 20, 30, 40, 50]

# Take command line argument and convert to integer
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Please provide a valid integer argument.")
    sys.exit(1)

# Check if index is within bounds
if 0 <= index < len(elements):
    print(elements[index])
else:
    print("Index out of bounds")