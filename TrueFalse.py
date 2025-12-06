import pyautogui
import win32con
import win32gui
import time
from pywinauto import Application


def safe_set_foreground(hwnd):
    """Безопасная активация окна с обходом ограничений Windows"""
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


def ensure_window_visible(window_title=None, window_class=None, maximize=True):
    """
    Проверяет, видно ли окно, и при необходимости разворачивает его.
    """
    print(f"=== ПРОВЕРКА ВИДИМОСТИ ОКНА ===")

    try:
        if window_title:
            hwnd = win32gui.FindWindow(window_class, window_title)
        else:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)

        if not hwnd:
            print(f"❌ Окно не найдено: {window_title}")
            return False

        print(f"Найдено окно: '{window_title}' (handle: {hwnd})")

        placement = win32gui.GetWindowPlacement(hwnd)
        current_state = placement[1]

        if current_state == win32con.SW_SHOWMINIMIZED:
            print("📌 Окно свернуто - восстанавливаем")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)

        if maximize and current_state != win32con.SW_SHOWMAXIMIZED:
            print("📌 Разворачиваем окно на весь экран")
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        elif not maximize and current_state == win32con.SW_SHOWMAXIMIZED:
            print("📌 Восстанавливаем нормальный размер окна")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        safe_set_foreground(hwnd)
        time.sleep(1)

        print("✅ Окно подготовлено")
        return True

    except Exception as e:
        print(f"❌ Ошибка при работе с окном: {e}")
        return False


def find_configurator_window():
    """
    Находит окно конфигуратора по части заголовка (поддерживает №118 и №116)
    """
    windows = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "Конфигуратор ИВК«АБАК+»" in title:
                windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, None)
    return windows


def change_password_for_user(user_type, current_password, new_password):
    """
    Меняет пароль для конкретного типа пользователя
    """
    print(f"\n🔐 Смена пароля для: {user_type}")

    # Ищем окно смены паролей
    password_windows = []

    def find_password_window(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if "парол" in title.lower() or "password" in title.lower():
                password_windows.append((hwnd, title))
        return True

    win32gui.EnumWindows(find_password_window, None)

    if not password_windows:
        print("❌ Не найдено окно смены паролей")
        return False

    hwnd_popup, title_popup = password_windows[0]
    print(f"📋 Работаем с окном: '{title_popup}'")

    # Активируем окно
    ensure_window_visible(window_title=title_popup, maximize=False)
    time.sleep(1)

    try:
        # Подключаемся к окну смены паролей
        app_popup = Application(backend='uia').connect(handle=hwnd_popup)
        window_popup = app_popup.window(handle=hwnd_popup)

        # ШАГ 1: Выбираем тип пользователя из выпадающего списка
        print(f"1. 👤 Выбор пользователя: {user_type}")

        # Ищем комбобокс или кнопку выбора пользователя
        comboboxes = window_popup.descendants(control_type="ComboBox")
        buttons = window_popup.descendants(control_type="Button")

        print(f"Найдено ComboBox: {len(comboboxes)}")
        print(f"Найдено Button: {len(buttons)}")

        # Ищем элемент для выбора типа пользователя
        user_selector = None
        for elem in window_popup.descendants():
            elem_info = elem.element_info
            if (elem_info.control_type in ["ComboBox", "Button"] and
                    elem_info.name and any(
                        word in elem_info.name.lower() for word in ["пользователь", "user", "тип", "role"])):
                user_selector = elem
                break

        if not user_selector:
            # Если не нашли по названию, берем первый комбобокс или подходящую кнопку
            if comboboxes:
                user_selector = comboboxes[0]
            elif len(buttons) > 3:  # Предполагаем, что кнопка выбора не среди основных
                user_selector = buttons[0]  # Первая кнопка может быть для выбора

        if user_selector:
            rect = user_selector.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2

            print(f"Координаты выбора пользователя: ({center_x}, {center_y})")

            # Кликаем для открытия списка
            pyautogui.click(center_x, center_y)
            time.sleep(1)

            # Выбираем нужного пользователя из списка
            # Позиции могут быть разными, нужно подобрать
            user_positions = {
                "оператор": (center_x, center_y + 30),
                "наладчик": (center_x, center_y + 60),
                "поверитель": (center_x, center_y + 90)
            }

            if user_type.lower() in user_positions:
                target_x, target_y = user_positions[user_type.lower()]
                pyautogui.click(target_x, target_y)
                print(f"✅ Выбран пользователь: {user_type}")
                time.sleep(1)
            else:
                print(f"❌ Неизвестный тип пользователя: {user_type}")
                return False
        else:
            print("❌ Не найден элемент выбора пользователя")
            return False

        # ШАГ 2: Вводим пароли в три поля
        print("2. ⌨️ Ввод паролей...")

        # Ищем поля ввода
        edit_fields = window_popup.descendants(control_type="Edit")
        print(f"Найдено полей ввода: {len(edit_fields)}")

        if len(edit_fields) >= 3:
            passwords = [current_password, new_password, new_password]
            field_labels = ["текущий пароль", "новый пароль", "подтверждение"]

            for i, field in enumerate(edit_fields[:3]):  # Берем первые три поля
                rect = field.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                print(f"  Поле {i + 1} ({field_labels[i]}): ({center_x}, {center_y})")

                # Кликаем в поле
                pyautogui.click(center_x, center_y)
                time.sleep(0.3)

                # Очищаем поле
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.1)
                pyautogui.press('delete')
                time.sleep(0.1)

                # Вводим пароль
                pyautogui.write(passwords[i], interval=0.05)
                print(f"    Введен: {passwords[i]}")
                time.sleep(0.3)
        else:
            print("❌ Не найдено три поля для ввода паролей")
            return False

        # ШАГ 3: Нажимаем кнопку подтверждения
        print("3. ✅ Подтверждение смены пароля...")

        # Ищем кнопки OK, Применить, Сохранить и т.д.
        confirm_button = None
        for button in buttons:
            button_name = button.element_info.name.lower()
            if any(word in button_name for word in ["ок", "ok", "применить", "apply", "сохранить", "save"]):
                confirm_button = button
                break

        if not confirm_button and buttons:
            # Берем последнюю кнопку (обычно это OK)
            confirm_button = buttons[-1]

        if confirm_button:
            rect = confirm_button.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2

            print(f"Координаты кнопки подтверждения: ({center_x}, {center_y})")

            pyautogui.click(center_x, center_y)
            print("✅ Пароль изменен")
            time.sleep(2)
        else:
            print("❌ Не найдена кнопка подтверждения")
            return False

        return True

    except Exception as e:
        print(f"❌ Ошибка при смене пароля: {e}")
        return False


def change_passwords_sequence():
    """
    Основная последовательность для смены паролей
    """
    print("🚀 ЗАПУСК ПРОЦЕДУРЫ СМЕНЫ ПАРОЛЕЙ")
    print("=" * 50)

    # Ищем окно конфигуратора
    config_windows = find_configurator_window()

    if not config_windows:
        print("❌ Не найдено окон конфигуратора")
        return False

    # Берем первое найденное окно
    hwnd, window_title = config_windows[0]
    print(f"📋 Найдено окно конфигуратора: '{window_title}'")

    try:
        # Убеждаемся, что окно видно и развернуто на полный экран
        if not ensure_window_visible(window_title=window_title, maximize=True):
            return False

        # Подключаемся к конфигуратору
        app = Application(backend='uia').connect(handle=hwnd)
        window = app.window(handle=hwnd)

        print("🔍 Поиск элементов интерфейса...")

        # ШАГ 1: Нажимаем кнопку остановки процессов
        print("\n1. 🔴 Нажатие кнопки остановки процессов...")

        images = window.descendants(control_type="Image")
        print(f"Найдено элементов Image: {len(images)}")

        if len(images) < 7:
            print(f"❌ Недостаточно элементов Image (нужно минимум 7, найдено {len(images)})")
            return False

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

        # ШАГ 2: Открываем меню смены паролей
        print("\n2. 📋 Открытие меню смены паролей...")

        try:
            passwords_menu = window.descendants()[13]
            rect = passwords_menu.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2

            print(f"Координаты меню 'Пароли': ({center_x}, {center_y})")

            pyautogui.click(center_x, center_y)
            print("✅ Меню 'Пароли' открыто")
            time.sleep(1)

            # Ищем MenuItem с индексом 3
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

        # ШАГ 3: Меняем пароли для всех трех типов пользователей
        print("\n3. 🔐 Последовательная смена паролей для всех пользователей")

        # Пароли для смены (текущий_пароль, новый_пароль)
        password_changes = [
            ("оператор", "1234", "5678"),
            ("наладчик", "5678", "3456"),
            ("поверитель", "3456", "1234")
        ]

        for user_type, current_pass, new_pass in password_changes:
            success = change_password_for_user(user_type, current_pass, new_pass)
            if not success:
                print(f"❌ Не удалось сменить пароль для {user_type}")
                # Продолжаем с другими пользователями
            else:
                print(f"✅ Пароль для {user_type} успешно изменен")

            time.sleep(1)

        print("\n🎉 ПРОЦЕДУРА СМЕНЫ ПАРОЛЕЙ УСПЕШНО ЗАВЕРШЕНА!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при выполнении процедуры: {e}")
        return False


# Основная последовательность выполнения
if __name__ == "__main__":
    print("🚀 ЗАПУСК СКРИПТА СМЕНЫ ПАРОЛЕЙ")
    print("=" * 50)

    # Запускаем основную процедуру
    success = change_passwords_sequence()

    if success:
        print("\n✅ Смена паролей выполнена успешно!")
    else:
        print("\n❌ Произошла ошибка при смене паролей")
