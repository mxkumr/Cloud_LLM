def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1  # or raise an exception, but per instructions we return a value

def main():
    id_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    size = len(id_sequence)
    
    try:
        index = int(input().strip())
        result = getValueFromArray(id_sequence, size, index)
        exit(result)
    except Exception:
        exit(-1)

if __name__ == "__main__":
    main()