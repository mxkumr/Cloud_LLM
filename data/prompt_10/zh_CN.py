def getValueFromArray(arr, size, index):
    if index < 0 or index >= size:
        raise IndexError("Index out of bounds")
    return arr[index]

def main():
    import sys
    # Read an integer from standard input
    try:
        user_input = int(sys.stdin.readline().strip())
    except ValueError:
        sys.exit(1)
    
    # Define the id_sequence array
    id_sequence = [10, 20, 30, 40, 50]  # Example array, can be modified as needed
    size = len(id_sequence)
    
    # Call getValueFromArray with the array, size, and user input as index
    try:
        result = getValueFromArray(id_sequence, size, user_input)
        sys.exit(result)
    except IndexError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()