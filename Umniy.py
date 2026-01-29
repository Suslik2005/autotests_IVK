import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class QuickSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.role_number = None

        self.setWindowTitle("Select Role")
        self.setGeometry(100, 100, 300, 250)

        layout = QVBoxLayout()

        # Кнопки с номерами
        btn1 = QPushButton("OPERATOR → 1")
        btn1.clicked.connect(lambda: self.select("1"))
        layout.addWidget(btn1)

        btn2 = QPushButton("TECHNICIAN → 2")
        btn2.clicked.connect(lambda: self.select("2"))
        layout.addWidget(btn2)

        btn3 = QPushButton("VERIFIER → 3")
        btn3.clicked.connect(lambda: self.select("3"))
        layout.addWidget(btn3)

        self.setLayout(layout)

    def select(self, number):
        self.role_number = number
        self.close()


def save_to_passwords(number):
    """Сохраняет номер в 4-ю строку passwords.txt"""
    filename = "passwords.txt"

    # Читаем или создаем файл
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
    else:
        lines = []

    # Добавляем пароли если нужно
    while len(lines) < 3:
        lines.append(f"default_pass_{len(lines) + 1}")

    # Обновляем 4-ю строку
    if len(lines) >= 4:
        lines[3] = number
    else:
        lines.append(number)

    # Сохраняем
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    return lines


# Основная программа
if __name__ == "__main__":
    # 1. Показываем окно выбора
    app = QApplication(sys.argv)
    selector = QuickSelector()
    selector.show()
    app.exec()

    # 2. Получаем номер
    if selector.role_number:
        print(f"Selected number: {selector.role_number}")

        # 3. Сохраняем в файл
        updated_lines = save_to_passwords(selector.role_number)
        print(f"Updated passwords.txt (4th line = {selector.role_number})")

        # 4. Ваш код продолжается здесь
        print("\nYour program continues...")

        # Пример использования номера
        role_map = {"1": "оператор", "2": "наладчик", "3": "поверитель"}
        selected_role = role_map.get(selector.role_number, "unknown")

        print(f"\nStarting as {selected_role}...")
        # ... ваш основной код ...

    else:
        print("No selection made")

if __name__ == "__main__":
    # Run the program
    result = main()

    if result:
        print(f"\nProgram can now use: {result}")
        # Your additional logic here