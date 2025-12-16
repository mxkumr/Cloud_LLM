# Array kendaraan
kendaraan = ["Mobil", "Motor", "Sepeda", "Truk", "Bis"]

# Meminta pengguna memasukkan indeks kendaraan
indeks_input = input("Masukkan indeks kendaraan: ")

# Mengubah input menjadi bilangan bulat
try:
    indeks = int(indeks_input)
    
    # Memeriksa apakah indeks valid
    if 0 <= indeks < len(kendaraan):
        print(f"Kendaraan di indeks {indeks} adalah: {kendaraan[indeks]}")
    else:
        print("Error: Indeks tidak valid. Indeks harus antara 0 dan", len(kendaraan) - 1)
        
except ValueError:
    print("Error: Masukkan harus berupa bilangan bulat.")