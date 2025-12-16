import sys

# Check if an index is provided
if len(sys.argv) < 2:
    print("Usage: python argv_index.py <index>")
    sys.exit(1)

# Get the index from command line argument
try:
    index = int(sys.argv[1])
except ValueError:
    print("Index must be an integer.")
    sys.exit(1)

# Check if the index is valid (non-negative and within range)
if index < 0 or index >= len(sys.argv):
    print(f"Index {index} is out of range. Available arguments: {len(sys.argv) - 1}")
    sys.exit(1)

# Print the argument at the specified index
print(sys.argv[index + 1])  # +1 because sys.argv[0] is the script name