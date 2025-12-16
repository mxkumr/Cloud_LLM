import sys

def main():
    if len(sys.argv) < 2:
        print("Error: Please provide an index as a command line argument.")
        sys.exit(1)
    
    try:
        index = int(sys.argv[1])
    except ValueError:
        print("Error: Index must be an integer.")
        sys.exit(1)
    
    # Command line arguments start from index 1 (sys.argv[0] is the program name)
    # So we need to check if index is valid (1 <= index < len(sys.argv))
    if index < 1 or index >= len(sys.argv):
        print(f"Error: Index {index} is out of range. Available arguments: 1 to {len(sys.argv) - 1}.")
        sys.exit(1)
    
    print(sys.argv[index])

if __name__ == "__main__":
    main()