def getValueFromArray(arr, size, index):
    if index < 0:
        return -2
    if index >= size:
        return -1
    return arr[index]

def main():
    id_sequence = [10, 20, 30, 40, 50]
    size = len(id_sequence)
    try:
        index = int(input().strip())
        result = getValueFromArray(id_sequence, size, index)
        exit(result)
    except Exception:
        exit(-1)

if __name__ == "__main__":
    main()