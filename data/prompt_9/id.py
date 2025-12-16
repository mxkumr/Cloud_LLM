import sys

# Ambil indeks dari argumen baris perintah
index = int(sys.argv[1])

# Cetak argumen sesuai indeks (indeks dimulai dari 1 untuk argumen pengguna)
if index + 1 < len(sys.argv):
    print(sys.argv[index + 1])
else:
    print("Indeks melebihi jumlah argumen yang tersedia.")