from logig import PasswordChanger
def modify_file_line(filename, line_number, new_value):
    """Изменяет указанную строку в файле"""
    # Читаем все строки
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Убеждаемся, что файл имеет достаточно строк
    while len(lines) < line_number:
        lines.append('\n')

    # Изменяем нужную строку (индексация с 0, поэтому line_number-1)
    lines[line_number - 1] = f"{new_value}\n"

    # Записываем обратно
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(lines)

    print(f"Строка {line_number} изменена на: {new_value}")



# Основная программа
filename = "passwords.txt"  # Укажите ваш файл
line_to_change = 4  # Меняем 4 строку

# Запускаем 3 раза с разными значениями
for value in [1, 2, 3]:
    print(f"\n--- Подготовка к запуску со значением {value} ---")

    # Изменяем файл
    modify_file_line(filename, line_to_change, value)

    # Создаем и запускаем экземпляр класса
    changer = PasswordChanger()
    changer.run()

print("\nВсе 3 запуска завершены!")
