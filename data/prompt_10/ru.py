def getValueFromArray(arr, size, index):
    if 0 <= index < size:
        return arr[index]
    else:
        return None

id_sequence = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
size = len(id_sequence)

# Считываем целое число из стандартного ввода
index = int(input().strip())

# Вызываем функцию
value = getValueFromArray(id_sequence, size, index)

# Проверяем четность и завершаем программу с соответствующим кодом
if value is not None and value % 2 == 0:
    exit(0)
elif value is not None and value % 2 == 1:
    exit(1)
else:
    exit(1)  # В случае недопустимого индекса завершаем с кодом 1