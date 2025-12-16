import sys

def main():
    # Создаем массив элементов
    arr = [10, 20, 30, 40, 50]
    
    # Проверяем, есть ли аргумент командной строки
    if len(sys.argv) != 2:
        print("Invalid argument")
        return
    
    # Пытаемся преобразовать аргумент в целое число
    try:
        index = int(sys.argv[1])
    except ValueError:
        print("Invalid argument")
        return
    
    # Проверяем, находится ли индекс в допустимых пределах
    if index < 0 or index >= len(arr):
        print("Index out of range")
    else:
        print(arr[index])

if __name__ == "__main__":
    main()