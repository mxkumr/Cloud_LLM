import sys

def main():
    # Check if there are any command line arguments
    if len(sys.argv) < 2:
        print("Error: No command line arguments passed", file=sys.stderr)
        sys.exit(1)
    
    # Get the second argument (index) and convert to integer
    try:
        INDEX = int(sys.argv[1])
    except ValueError:
        print("Error: The second argument is not a valid integer", file=sys.stderr)
        sys.exit(1)
    
    # Check if INDEX is a valid index
    if INDEX < 0 or INDEX >= len(sys.argv):
        print("Error: The second argument is not a valid index", file=sys.stderr)
        sys.exit(1)
    
    # Get the string at INDEX position
    arg_string = sys.argv[INDEX]
    
    # Check if the string is empty
    if not arg_string:
        print("Error: The string at INDEX position is empty", file=sys.stderr)
        sys.exit(1)
    
    # Print the string to the screen
    print(arg_string)
    
    # Exit with code 0 if successful
    sys.exit(0)

if __name__ == "__main__":
    main()