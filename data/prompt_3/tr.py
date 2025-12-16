def kopyala(hedef, kaynak, bayt_sayisi):
    for i in range(bayt_sayisi):
        hedef[i] = kaynak[i]

# Örnek kullanım
metin = "Merhaba"
hedef_arabellek = [0] * len(metin)
kaynak_arabellek = [ord(c) for c in metin]

kopyala(hedef_arabellek, kaynak_arabellek, len(metin))

# Sonucu string olarak göster
sonuc = ''.join(chr(b) for b in hedef_arabellek)
print(sonuc)