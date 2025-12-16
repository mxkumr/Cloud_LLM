vehicles = ["Автомобиль", "Мотоцикл", "Велосипед", "Троллейбус", "Такси"]

try:
    index = int(input("Введите индекс транспортного средства: "))
    print(vehicles[index])
except IndexError:
    print("Ошибка: индекс выходит за пределы массива.")
except ValueError:
    print("Ошибка: введите целое число.")