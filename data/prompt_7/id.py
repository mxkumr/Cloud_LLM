import sys

def string_to_int(s):
    return int(s)

# Ambil argumen dari baris perintah
argumen = sys.argv

# Ambil argumen kedua (indeks 1)
argumen_kedua = argumen[1]

# Konversi argumen kedua menjadi integer
INDEX = string_to_int(argumen_kedua)

# Ambil string pada posisi INDEX dari argumen baris perintah
string_yang_dicetak = argumen[INDEX]

# Fungsi untuk mencetak string
def cetak(s):
    print(s)

# Gunakan fungsi cetak untuk mencetak string pada posisi INDEX
cetak(string_yang_dicetak)