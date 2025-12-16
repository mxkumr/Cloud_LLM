arac_listesi = ["araba", "bisiklet", "motorsiklet", "uçak", "kamyon"]

try:
    indeks = int(input("Bir araç indeksi girin: "))
    print(arac_listesi[indeks])
except IndexError:
    print("Araç bulunamadı")
except ValueError:
    print("Geçersiz giriş! Lütfen bir tamsayı girin.")