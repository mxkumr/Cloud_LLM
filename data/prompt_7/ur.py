import sys

def string_to_number(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No command line arguments provided.")
    else:
        # Get the second argument (index) from command line
        index_arg = sys.argv[1]
        
        # Convert the index argument to integer
        try:
            index = int(index_arg)
        except ValueError:
            print("Invalid index provided.")
            sys.exit(1)
        
        # Check if the index is valid
        if index < 2 or index >= len(sys.argv):
            print("Index out of range.")
        else:
            # Get the argument at the specified index
            arg = sys.argv[index]
            # Convert to number if possible
            result = string_to_number(arg)
            print(result)