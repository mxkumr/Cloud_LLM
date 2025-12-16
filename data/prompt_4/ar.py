vehicles = ["Toyota", "Honda", "Ford", "BMW", "Audi"]

try:
    index = int(input("أدخل فهرس المركبة: "))
    if 0 <= index < len(vehicles):
        print(f"المركبة في الفهرس {index} هي: {vehicles[index]}")
    else:
        print("خطأ: الفهرس خارج النطاق!")
except ValueError:
    print("خطأ: يُرجى إدخال عدد صحيح!")