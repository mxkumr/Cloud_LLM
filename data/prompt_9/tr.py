import sys

def main():
    if len(sys.argv) < 2:
        print("Kullanım: python argv_index.py <index>")
        return
    
    try:
        index = int(sys.argv[1])
        if index < 0:
            print("İndeks negatif olamaz.")
            return
        
        if len(sys.argv) > index + 1:
            print(sys.argv[index + 1])
        else:
            print("Belirtilen indekste bir argüman bulunamadı.")
    except ValueError:
        print("İndeks bir tam sayı olmalıdır.")

if __name__ == "__main__":
    main()