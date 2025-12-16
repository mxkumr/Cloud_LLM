import sys

def get_argument(index):
    if len(sys.argv) <= index:
        print(f"Error: Argument index {index} is out of range.")
        sys.exit(1)
    return sys.argv[index]

# Get the argument at index 1 (argv[1])
if __name__ == "__main__":
    result = get_argument(1)
    print(result)