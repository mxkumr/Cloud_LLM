import sys

def string_to_int(s):
    return int(s)

# İkinci argümanı (index 1) al
index = string_to_int(sys.argv[1])

# INDEX konumundaki argümanı ekrana yazdır
print(sys.argv[index])