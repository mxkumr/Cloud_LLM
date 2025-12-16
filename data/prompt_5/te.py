import sys

# Create a list of code elements
code_elements = [10, 20, 30, 40, 50]

# Take command line argument and convert it to integer
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Please provide a valid integer as a command line argument.")
    sys.exit(1)

# Print the element at the given index
if 0 <= index < len(code_elements):
    print(code_elements[index])
else:
    print(f"Index {index} is out of range for the list of size {len(code_elements)}.")