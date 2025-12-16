import sys

# Membuat array elemen
arr = [10, 20, 30, 40, 50]

# Mengambil argumen baris perintah dan mengubahnya menjadi bilangan bulat
try:
    index = int(sys.argv[1])
except (IndexError, ValueError):
    print("Indeks tidak valid")
    exit()

# Mencetak elemen pada indeks tersebut
if 0 <= index < len(arr):
    print(arr[index])
else:
    print("Indeks tidak valid")