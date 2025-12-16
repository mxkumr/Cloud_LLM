def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        raise IndexError("Index out of bounds")

def main():
    # Read integer from standard input
    index = int(input().strip())
    
    # Define the array id_sequence
    id_sequence = [10, 20, 30, 40, 50]  # Example array, can be modified as needed
    
    # Call getValueFromArray function
    result = getValueFromArray(id_sequence, len(id_sequence), index)
    
    # Return the result as program exit code
    return result

# Run the main function and exit with the result
if __name__ == "__main__":
    exit(main())