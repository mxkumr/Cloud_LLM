def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1  # Return -1 for invalid index

def main():
    # Read the size of the array
    size = int(input().strip())
    
    # Read the array elements
    arr = list(map(int, input().strip().split()))
    
    # Read the index
    index = int(input().strip())
    
    # Call the function and return the result as exit code
    result = getValueFromArray(arr, size, index)
    exit(result)

if __name__ == "__main__":
    main()