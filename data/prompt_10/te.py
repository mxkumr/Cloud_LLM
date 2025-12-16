def getValueFromArray(arr, size, index):
    if index < 0 or index >= size:
        return 0
    return arr[index]

def main():
    try:
        # Read the integer from standard input
        index = int(input().strip())
        
        # Read the sequence of integers
        id_sequence = list(map(int, input().split()))
        
        # Get the size of the array
        size = len(id_sequence)
        
        # Call the function and get the result
        result = getValueFromArray(id_sequence, size, index)
        
        # Exit with the result as the exit code
        exit(result)
        
    except (ValueError, IndexError):
        # If input is not an integer or invalid, exit with code 0
        exit(0)

if __name__ == "__main__":
    main