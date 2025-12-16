def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return -1

def main():
    # 標準入力から整数を読み取る
    n = int(input().strip())
    
    # id_sequence 配列の定義（例として、0 から n-1 の整数）
    id_sequence = list(range(n))
    
    # getValueFromArray を呼び出し、戻り値を終了コードとして返す
    result = getValueFromArray(id_sequence, n, n - 1)
    exit(result)

if __name__ == "__main__":
    main()