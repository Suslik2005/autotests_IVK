import pyautogui
import win32con
import win32gui
import time

from pywinauto import Application
import os


class PasswordChanger:
    def safe_set_foreground(self, hwnd):
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                  win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
            win32gui.BringWindowToTop(hwnd)
            return True
        except:
            return False

    def ensure_window_visible(self, window_title=None, window_class=None, maximize=True):
        print(f"ПРОВЕРКА ВИДИМОСТИ ОКНА")

        try:
            if window_title:
                hwnd = win32gui.FindWindow(window_class, window_title)
            else:
                hwnd = win32gui.GetForegroundWindow()
                window_title = win32gui.GetWindowText(hwnd)

            if not hwnd:
                print(f"Окно не найдено: {window_title}")
                return False

            print(f"Найдено окно: '{window_title}' (handle: {hwnd})")

            placement = win32gui.GetWindowPlacement(hwnd)
            current_state = placement[1]

            if current_state == win32con.SW_SHOWMINIMIZED:
                print("Окно свернуто - восстанавливаем")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.5)

            if maximize and current_state != win32con.SW_SHOWMAXIMIZED:
                print("Разворачиваем окно на весь экран")
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            elif not maximize and current_state == win32con.SW_SHOWMAXIMIZED:
                print("Восстанавливаем нормальный размер окна")
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            self.safe_set_foreground(hwnd)
            time.sleep(1)

            print("Окно подготовлено")
            return True

        except Exception as e:
            print(f"Ошибка при работе с окном: {e}")
            return False

    def find_configurator_window(self):
        windows = []

        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Конфигуратор ИВК«АБАК+»" in title:
                    windows.append((hwnd, title))
            return True

        win32gui.EnumWindows(callback, None)
        return windows

    def change_password_for_user(self, user_type, current_password, new_password):
        print(f"\n🔄 Смена пароля для: {user_type}")

        password_windows = []

        def find_password_window(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "парол" in title.lower() or "password" in title.lower():
                    password_windows.append((hwnd, title))
            return True

        win32gui.EnumWindows(find_password_window, None)

        if not password_windows:
            print("Не найдено окно смены паролей")
            return False

        hwnd_popup, title_popup = password_windows[0]
        print(f"Работаем с окном: '{title_popup}'")

        self.ensure_window_visible(window_title=title_popup, maximize=False)
        time.sleep(1)

        try:
            app_popup = Application(backend='uia').connect(handle=hwnd_popup)
            window_popup = app_popup.window(handle=hwnd_popup)

            print(f"1. 👤 Выбор пользователя: {user_type}")

            comboboxes = window_popup.descendants(control_type="ComboBox")
            buttons = window_popup.descendants(control_type="Button")

            print(f"Найдено ComboBox: {len(comboboxes)}")
            print(f"Найдено Button: {len(buttons)}")

            user_selector = None
            for elem in window_popup.descendants():
                elem_info = elem.element_info
                if (elem_info.control_type in ["ComboBox", "Button"] and
                        elem_info.name and any(
                            word in elem_info.name.lower() for word in ["пользователь", "user", "тип", "role"])):
                    user_selector = elem
                    break

            if not user_selector:
                if comboboxes:
                    user_selector = comboboxes[0]
                elif len(buttons) > 3:
                    user_selector = buttons[0]

            if user_selector:
                rect = user_selector.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                print(f"Координаты выбора пользователя: ({center_x}, {center_y})")

                pyautogui.click(center_x, center_y)
                time.sleep(1)

                user_positions = {
                    "наладчик": (center_x, center_y + 60),
                    "оператор": (center_x, center_y + 30),
                    "поверитель": (center_x, center_y + 90)
                }

                if user_type.lower() in user_positions:
                    target_x, target_y = user_positions[user_type.lower()]
                    pyautogui.click(target_x, target_y)
                    print(f"Выбран пользователь: {user_type}")
                    time.sleep(1)
                else:
                    print(f"Неизвестный тип пользователя: {user_type}")
                    return False
            else:
                print("Не найден элемент выбора пользователя")
                return False

            print("2. 🔑 Ввод паролей...")

            edit_fields = window_popup.descendants(control_type="Edit")
            print(f"Найдено полей ввода: {len(edit_fields)}")

            if len(edit_fields) >= 3:
                passwords = [current_password, new_password, new_password]
                field_labels = ["текущий пароль", "новый пароль", "подтверждение"]

                for i, field in enumerate(edit_fields[:3]):
                    rect = field.rectangle()
                    center_x = (rect.left + rect.right) // 2
                    center_y = (rect.top + rect.bottom) // 2

                    print(f"  Поле {i + 1} ({field_labels[i]}): ({center_x}, {center_y})")

                    pyautogui.click(center_x, center_y)
                    time.sleep(0.3)

                    pyautogui.hotkey('ctrl', 'a')
                    time.sleep(0.1)
                    pyautogui.press('delete')
                    time.sleep(0.1)

                    pyautogui.write(passwords[i], interval=0.05)
                    print(f"    Введен: {passwords[i]}")
                    time.sleep(0.3)
            else:
                print("Не найдено три поля для ввода паролей")
                return False

            print("3. ✅ Подтверждение смены пароля...")

            confirm_button = None
            for button in buttons:
                button_name = button.element_info.name.lower()
                if any(word in button_name for word in
                       ["ок", "ok", "применить", "apply", "сохранить", "save", "изменить", "change"]):
                    confirm_button = button
                    break

            if not confirm_button and buttons:
                confirm_button = buttons[-1]

            if confirm_button:
                rect = confirm_button.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                print(f"Координаты кнопки подтверждения: ({center_x}, {center_y})")

                pyautogui.click(center_x, center_y)
                print("Кнопка подтверждения нажата")
                time.sleep(2)

                print(f"✅ Пароль для {user_type} успешно изменен")
                return True
            else:
                print("Не найдена кнопка подтверждения")
                return False

        except Exception as e:
            print(f"❌ Ошибка при смене пароля: {e}")
            return False

    def change_passwords_sequence(self):
        print("🚀 ЗАПУСК ПРОЦЕДУРЫ СМЕНЫ ПАРОЛЕЙ")
        print("=" * 50)

        config_windows = self.find_configurator_window()

        if not config_windows:
            print("❌ Не найдено окон конфигуратора")
            return False

        hwnd, window_title = config_windows[0]
        print(f"📋 Найдено окно конфигуратора: '{window_title}'")

        try:
            if not self.ensure_window_visible(window_title=window_title, maximize=True):
                return False

            app = Application(backend='uia').connect(handle=hwnd)
            window = app.window(handle=hwnd)

            print("🔍 Поиск элементов интерфейса...")

            print("\n1. ⏸️ Нажатие кнопки остановки процессов...")

            images = window.descendants(control_type="Image")
            print(f"Найдено элементов Image: {len(images)}")

            stop_button = images[6]
            rect = stop_button.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2

            print(f"Координаты кнопки остановки: ({center_x}, {center_y})")

            pyautogui.moveTo(center_x, center_y)
            time.sleep(1)
            pyautogui.click(center_x, center_y)
            print("✅ Кнопка остановки процессов нажата")
            time.sleep(2)

            print("\n2. 📂 Открытие меню смены паролей...")

            try:
                passwords_menu = window.descendants()[13]
                rect = passwords_menu.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                print(f"Координаты меню 'Пароли': ({center_x}, {center_y})")

                pyautogui.click(center_x, center_y)
                print("✅ Меню 'Пароли' открыто")
                time.sleep(1)

                menu_items = []
                for elem in window.descendants():
                    if (elem.element_info.control_type == "MenuItem" and
                            elem.element_info.name and
                            elem.rectangle().top > rect.bottom):
                        menu_items.append(elem)

                print(f"Найдено MenuItem в выпадающем меню: {len(menu_items)}")

                if len(menu_items) >= 3:
                    target_menu_item = menu_items[2]
                    rect_item = target_menu_item.rectangle()
                    center_x_item = (rect_item.left + rect_item.right) // 2
                    center_y_item = (rect_item.top + rect_item.bottom) // 2

                    print(f"Координаты MenuItem: ({center_x_item}, {center_y_item})")
                    print(f"Текст MenuItem: '{target_menu_item.element_info.name}'")

                    pyautogui.click(center_x_item, center_y_item)
                    print("✅ MenuItem нажат")
                    time.sleep(2)
                else:
                    print("❌ Не найдены MenuItem в выпадающем меню")
                    return False

            except Exception as e:
                print(f"❌ Ошибка при работе с меню: {e}")
                return False

            print("\n3. 👥 Последовательная смена паролей для пользователей")

            array = []
            if not os.path.exists("passwords.txt"):
                with open("passwords.txt", "w", encoding='utf-8') as f:
                    f.write("1234\n")
                    f.write("5678\n")
                    f.write("3456\n")
                    f.write("1\n")
                print("Создан файл passwords.txt с дефолтными значениями")
            else:
                print("✅ Файл passwords.txt найден")
            with open("passwords.txt", 'r', encoding='utf-8') as f:
                for i in range(4):
                    line = f.readline()
                    if line:
                        array.append(line.strip())
                    else:
                        array.append("")

            print(f"Прочитано из файла: {array}")

            users_to_change = []
            fourth_line = array[3] if len(array) > 3 else ""

            if fourth_line in ['1', '2', '3']:
                user_num = int(fourth_line)
                user_types = ['оператор', 'наладчик', 'поверитель']
                users_to_change.append(user_types[user_num - 1])
                print(f" Меняем пароль только для: {users_to_change[0]}")
            else:
                users_to_change = ['оператор', 'наладчик', 'поверитель']
                print(f" Меняем пароли для всех пользователей: {users_to_change}")

            current_password = array[int(fourth_line) - 1]
            if fourth_line == "1":
                if current_password == "1234":
                    new_password = "1001"
                else:
                    new_password = "1234"
            elif fourth_line == "2":
                if current_password == "5678":
                    new_password = "2002"
                else:
                    new_password = "5678"
            else:
                if current_password == "3456":
                    new_password = "3003"
                else:
                    new_password = "3456"

            for user_type in users_to_change:
                success = self.change_password_for_user(user_type, current_password, new_password)
                if success:
                    print(f"✅ Пароль для {user_type} успешно изменен на {new_password}")
                    time.sleep(1)
                else:
                    print(f"❌ Не удалось сменить пароль для {user_type}")

            self.update_line_in_file('passwords.txt', int(fourth_line), new_password)
            self.close_password_success_dialog()
            print("\n🎉 ПРОЦЕДУРА СМЕНЫ ПАРОЛЕЙ УСПЕШНО ЗАВЕРШЕНА!")
            return True

        except Exception as e:
            print(f"❌ Ошибка при выполнении процедуры: {e}")
            return False

    def update_line_in_file(self, filename, line_number, new_text):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if line_number < 1 or line_number > len(lines):
                print(f"Ошибка: строка {line_number} не существует в файле")
                return False
            lines[line_number - 1] = new_text + '\n'
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            return False

    def close_password_success_dialog(self):
        print("\n🔄 Закрываю диалог об успешной замене пароля...")
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.press('enter')
        return True

    def run(self):
        print("🚀 ЗАПУСК СКРИПТА СМЕНЫ ПАРОЛЕЙ")
        print("=" * 50)

        success = self.change_passwords_sequence()

        if success:
            print("\n✅ Смена паролей выполнена успешно!")
        else:
            print("\n❌ Произошла ошибка при смене паролей")


if __name__ == "__main__":
    changer = PasswordChanger()
    changer.run()
