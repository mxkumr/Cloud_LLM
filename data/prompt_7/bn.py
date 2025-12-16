import sys

def string_to_int(s):
    return int(s)

# Get the second command line argument (index)
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Error: Please provide a valid integer as the second argument.")
    sys.exit(1)

# Check if the index is within the valid range
if index < 0 or index >= len(sys.argv):
    print("Error: Index out of range.")
    sys.exit(1)

# Get the argument at the specified index
arg = sys.argv[index]

# Convert the string to an integer and print
try:
    result = string_to_int(arg)
    print(result)
except ValueError:
    print(f"Error: '{arg}' is not a valid integer.")
    sys.exit(1)