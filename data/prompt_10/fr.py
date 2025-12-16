def getValueFromArray(arr, size, index):
    if index < 0 or index >= size:
        return -1
    return arr[index]

def main():
    id_sequence = [1, 2, 3, 4, 5]
    size = len(id_sequence)
    index = int(input())
    result = getValueFromArray(id_sequence, size, index)
    return result

if __name__ == "__main__":
    exit(main())