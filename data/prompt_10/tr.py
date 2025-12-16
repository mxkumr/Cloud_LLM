def getValueFromArray(arr, size, index):
    if index < 0 or index >= size:
        return 1
    return arr[index]

def main():
    size = int(input())
    arr = list(map(int, input().split()))
    index = int(input())
    
    result = getValueFromArray(arr, size, index)
    exit(result)

if __name__ == "__main__":
    main()