def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        raise IndexError("Índice fuera de rango")

def main():
    id_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    size = len(id_sequence)
    
    try:
        index = int(input().strip())
        result = getValueFromArray(id_sequence, size, index)
        return result
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    import sys
    exit(main())