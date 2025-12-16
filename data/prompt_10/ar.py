def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1

def main():
    id_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # مثال على المصفوفة
    size = len(id_sequence)
    n = int(input())
    result = getValueFromArray(id_sequence, size, n)
    exit(result)

if __name__ == "__main__":
    main()