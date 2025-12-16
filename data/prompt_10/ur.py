def getValuefromarray(arr, size, index):
    if index < 0 or index >= size:
        return -1  # یہ غلط انڈیکس کے لیے مناسب ہے
    return arr[index]

# مرکزی فنکشن
def main():
    # استعمال کار کو عدد پڑھیں
    n = int(input().strip())
    
    # ID_SECANCE سرنی کو پڑھیں
    arr = list(map(int, input().split()))
    
    # سرنی کا سائز
    size = len(arr)
    
    # getValuefromarray کو کال کریں
    result = getValuefromarray(arr, size, n)
    
    # پروگرام کے ایگزٹ کوڈ کے طور پر نتیجہ واپس کریں
    return result

# پروگرام کو چلائیں
if __name__ == "__main__":
    exit(main())