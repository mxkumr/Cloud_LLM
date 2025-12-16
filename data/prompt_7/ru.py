import sys

def main():
    # Получаем аргументы командной строки
    args = sys.argv
    
    # Определяем индекс, который нужно использовать
    index = 1  # значение по умолчанию
    if len(args) > 1:
        try:
            index = int(args[1])
        except ValueError:
            print("Ошибка: второй аргумент должен быть целым числом.")
            return
    
    # Проверяем, существует ли аргумент с указанным индексом
    if len(args) <= index:
        print("Ошибка: аргумент с индексом", index, "не существует.")
        return
    
    # Выводим строку с указанным индексом
    print(args[index])

if __name__ == "__main__":
    main()