import sys

# Read the index from command line argument
index_str = sys.argv[1]

# Convert index to integer
index = int(index_str)

# Check if index is valid (1-based indexing)
if index < 1 or index >= len(sys.argv):
    print("Error: Index out of range.")
else:
    # Print the argument at the given index (1-based)
    print(sys.argv[index])