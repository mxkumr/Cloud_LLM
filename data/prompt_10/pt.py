def getValueFromArray(arr, size, index):
    return arr[index]

id_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
size = len(id_sequence)

if __name__ == "__main__":
    n = int(input())
    result = getValueFromArray(id_sequence, size, n)
    exit(result)