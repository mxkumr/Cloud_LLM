def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1  # or raise an exception, but per the problem, we return -1 for invalid index

def main():
    # Read the array size
    size = int(input().strip())
    
    # Read the array elements
    arr = list(map(int, input().strip().split()))
    
    # Read the index to retrieve
    index = int(input().strip())
    
    # Call the function and get the value
    result = getValueFromArray(arr, size, index)
    
    # Exit code is the result
    exit(result)

if __name__ == "__main__":
    main()