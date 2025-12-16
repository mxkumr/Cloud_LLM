# Membuat array string yang disebut kendaraan
kendaraan = ["mobil", "motor", "sepeda", "bus", "truk"]

# Meminta pengguna untuk mengindeks kendaraan
indeks = int(input("Masukkan indeks kendaraan (0-4): "))

# Mengembalikan kendaraan berdasarkan indeks
if 0 <= indeks < len(kendaraan):
    print(f"Kendaraan pada indeks {indeks} adalah: {kendaraan[indeks]}")
else:
    print("Indeks tidak valid!")

# Mengulang array dan mencetak setiap kendaraan
print("\nDaftar kendaraan:")
for i, kendaraan_item in enumerate(kendaraan):
    print(f"{i}: {kendaraan_item}")

# Mencetak jumlah kendaraan yang ada
print(f"\nJumlah kendaraan: {len(kendaraan)}")