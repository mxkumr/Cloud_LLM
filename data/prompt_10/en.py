def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1  # or raise an exception, but returning -1 for simplicity

def main():
    id_sequence = [1, 2, 3, 4, 5]
    size = len(id_sequence)
    index = int(input().strip())
    result = getValueFromArray(id_sequence, size, index)
    exit(result)

if __name__ == "__main__":
    main()