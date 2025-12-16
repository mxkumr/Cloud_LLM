# Araçlar dizisini oluştur
araçlar = ["Otobüs", "Otomobil", "Motosiklet", "Bisiklet", "Traktör"]

# Kullanıcıdan aracın endeksinin alınması
endeks = int(input("Bir aracın endeksinin alınması için bir sayı girin (0-4): "))
print(f"Endeksi {endeks} olan araç: {araçlar[endeks]}")

# Dizi boyunca döngü yaparak her bir aracın çıktısını al
print("\nTüm araçlar:")
for araç in araçlar:
    print(araç)

# Kullanıcıdan bir aracın adını ister ve aracın dizideki endeksinin çıktısını alır
araç_adi = input("\nBir aracın adını girin: ")
if araç_adi in araçlar:
    endeks = araçlar.index(araç_adi)
    print(f"{araç_adi} aracının dizideki endeksi: {endeks}")
else:
    print(f"{araç_adi} aracını dizide bulamadık.")