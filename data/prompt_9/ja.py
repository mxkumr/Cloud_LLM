import sys

def main():
    if len(sys.argv) < 2:
        print("Error: No index provided.", file=sys.stderr)
        sys.exit(1)
    
    try:
        index = int(sys.argv[1])
    except ValueError:
        print("Error: Index must be an integer.", file=sys.stderr)
        sys.exit(1)
    
    if index <= 0:
        print("Error: Index must be a positive integer.", file=sys.stderr)
        sys.exit(1)
    
    if index + 1 >= len(sys.argv):
        print(f"Error: Index {index} is out of range. Only {len(sys.argv) - 1} arguments provided.", file=sys.stderr)
        sys.exit(1)
    
    print(sys.argv[index + 1])

if __name__ == "__main__":
    main()