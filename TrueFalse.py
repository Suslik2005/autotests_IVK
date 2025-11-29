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

        # ШАГ 1: Нажимаем кнопку остановки процессов (элемент Image под индексом 6)
        print("\n1. 🔴 Нажатие кнопки остановки процессов...")

        # Ищем все элементы типа Image (как в предыдущем коде)
        images = window.descendants(control_type="Image")
        print(f"Найдено элементов Image: {len(images)}")

        if len(images) < 7:  # Нужно минимум 7 элементов (индекс 6)
            print(f"❌ Недостаточно элементов Image (нужно минимум 7, найдено {len(images)})")
            return False

        # Берем кнопку остановки под индексом 6
        stop_button = images[6]  # Индекс 6
        rect = stop_button.rectangle()
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2

        print(f"Координаты кнопки остановки: ({center_x}, {center_y})")

        # Наводим курсор и кликаем
        pyautogui.moveTo(center_x, center_y)
        time.sleep(1)
        pyautogui.click(center_x, center_y)

        print("✅ Кнопка остановки процессов нажата")
        time.sleep(2)

        # ШАГ 2: Нажимаем на меню "Пароли" и выбираем MenuItem под индексом 3
        print("\n2. 📋 Нажатие на меню 'Пароли'...")

        # Ищем меню "Пароли" (элемент 13 из отладки)
        try:
            passwords_menu = window.descendants()[13]  # Меню "Пароли"
            rect = passwords_menu.rectangle()
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2

            print(f"Координаты меню 'Пароли': ({center_x}, {center_y})")

            # Кликаем по меню "Пароли"
            pyautogui.click(center_x, center_y)
            print("✅ Меню 'Пароли' открыто")
            time.sleep(1)

            # После клика на "Пароли" ищем MenuItem с индексом 3
            time.sleep(1)

            # Ищем все MenuItem в выпадающем меню
            menu_items = []
            for elem in window.descendants():
                if (elem.element_info.control_type == "MenuItem" and
                        elem.element_info.name and
                        elem.rectangle().top > rect.bottom):  # Только те, что ниже основного меню
                    menu_items.append(elem)

            print(f"Найдено MenuItem в выпадающем меню: {len(menu_items)}")

            if len(menu_items) >= 3:
                # Берем MenuItem под индексом 3 (индекс 2 в списке)
                target_menu_item = menu_items[2]  # Индекс 2 для третьего элемента
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

        # ШАГ 3: Нажимаем первую кнопку во всплывшем окне
        print("\n3. 🎯 Нажатие первой кнопки во всплывшем окне...")

        # Ждем появления всплывающего окна
        time.sleep(3)

        # Ищем все окна чтобы найти всплывающее
        all_windows = []

        def find_popup_window(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and hwnd != window.handle:
                title = win32gui.GetWindowText(hwnd)
                if title and title != "":  # Окно с непустым заголовком
                    all_windows.append((hwnd, title))
            return True

        win32gui.EnumWindows(find_popup_window, None)

        if all_windows:
            print("📋 Найдены всплывающие окна:")
            for hwnd_popup, title_popup in all_windows:
                print(f"  - '{title_popup}'")

            # Берем первое всплывающее окно
            hwnd_popup, title_popup = all_windows[0]
            print(f"Работаем с окном: '{title_popup}'")

            # Активируем всплывающее окно
            ensure_window_visible(window_title=title_popup, maximize=False)
            time.sleep(1)

            # Подключаемся к всплывающему окну
            app_popup = Application(backend='uia').connect(handle=hwnd_popup)
            window_popup = app_popup.window(handle=hwnd_popup)

            # Ищем все кнопки во всплывающем окне
            popup_buttons = window_popup.descendants(control_type="Button")
            print(f"Найдено кнопок во всплывающем окне: {len(popup_buttons)}")

            if len(popup_buttons) > 0:
                # Нажимаем первую кнопку
                first_button = popup_buttons[0]
                rect = first_button.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                print(f"Координаты первой кнопки: ({center_x}, {center_y})")

                pyautogui.click(center_x, center_y)
                print("✅ Первая кнопка всплывающего окна нажата")
                time.sleep(2)

            else:
                print("❌ Не найдены кнопки во всплывающем окне")
                return False
        else:
            print("❌ Не найдено всплывающее окно")
            return False

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