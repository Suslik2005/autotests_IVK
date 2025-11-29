import pyautogui
import win32con
import win32gui
import time

from pywinauto import Application


def ensure_window_visible(window_title=None, window_class=None, maximize=True):
    """
    Проверяет, видно ли окно, и при необходимости разворачивает его.

    Args:
        window_title (str): Заголовок окна для поиска
        window_class (str): Класс окна для поиска (опционально)
        maximize (bool): Если True - максимизирует окно, иначе восстанавливает

    Returns:
        bool: Успешно ли окно найдено и обработано
    """
    print(f"=== ПРОВЕРКА ВИДИМОСТИ ОКНА ===")

    try:
        # Ищем окно по заголовку или классу
        if window_title:
            hwnd = win32gui.FindWindow(window_class, window_title)
        else:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)

        if not hwnd:
            print(f"❌ Окно не найдено: {window_title}")
            return False

        print(f"Найдено окно: '{window_title}' (handle: {hwnd})")

        # Получаем текущее состояние окна
        placement = win32gui.GetWindowPlacement(hwnd)
        current_state = placement[1]

        # Проверяем, свернуто ли окно
        if current_state == win32con.SW_SHOWMINIMIZED:
            print("📌 Окно свернуто - восстанавливаем")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            time.sleep(0.5)

        # Проверяем, максимизировано ли окно
        if maximize and current_state != win32con.SW_SHOWMAXIMIZED:
            print("📌 Разворачиваем окно на весь экран")
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
        elif not maximize and current_state == win32con.SW_SHOWMAXIMIZED:
            print("📌 Восстанавливаем нормальный размер окна")
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Активируем окно (переводим на передний план)
        win32gui.SetForegroundWindow(hwnd)

        # Проверяем, видно ли окно (не перекрыто ли другими окнами)
        if win32gui.IsWindowVisible(hwnd):
            print("✅ Окно видимо и активно")
        else:
            print("⚠️ Окно существует, но может быть не видно")

        # Дополнительная проверка - является ли окно активным
        active_hwnd = win32gui.GetForegroundWindow()
        if active_hwnd == hwnd:
            print("✅ Окно активно (на переднем плане)")
        else:
            print("⚠️ Окно не активно - пытаемся активировать")
            win32gui.SetForegroundWindow(hwnd)

        time.sleep(1)
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


# Обновленная функция connection с поддержкой обоих номеров версий
def connection_enhanced():
    print("=== НАЖАТИЕ НА КНОПКУ В КОНФИГУРАТОРЕ ===")

    # Ищем все окна конфигуратора
    config_windows = find_configurator_window()

    if not config_windows:
        print("❌ Не найдено окон конфигуратора")
        return False

    # Берем первое найденное окно
    hwnd, window_title = config_windows[0]
    print(f"📋 Найдено окно конфигуратора: '{window_title}'")

    try:
        # Сначала убеждаемся, что окно видно и РАЗВЕРНУТО НА ПОЛНЫЙ ЭКРАН
        if not ensure_window_visible(window_title=window_title, maximize=True):
            return False

        # Подключаемся к конфигуратору
        app1 = Application(backend='uia').connect(handle=hwnd)
        windo1 = app1.window(handle=hwnd)

        # Ищем все элементы типа Image
        images = windo1.descendants(control_type="Image")

        # Индекс нужной нам кнопки
        fifth_button = images[5]

        # Получаем координаты кнопки
        rect = fifth_button.rectangle()
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2

        print(f"Координаты 5-й кнопки: ({center_x}, {center_y})")

        # Наводим курсор и кликаем
        pyautogui.moveTo(center_x, center_y)
        time.sleep(1)
        pyautogui.click(center_x, center_y)

        print("✅ 5-я кнопка в разделе Image нажата успешно!")
        return True

    except Exception as e:
        print(f"❌ Ошибка при нажатии кнопки: {e}")
        return False


# УЛУЧШЕННАЯ функция precise_coordinate_automation
def precise_coordinate_automation_enhanced():
    print("=== ТОЧНАЯ АВТОМАТИЗАЦИЯ ПО КООРДИНАТАМ ===")

    window_title = "Пароли"

    # Сначала убеждаемся, что окно видно
    if not ensure_window_visible(window_title=window_title, maximize=False):
        return False

    # Находим окно
    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print("❌ Окно не найдено")
        return False

    # Получаем координаты окна
    rect = win32gui.GetWindowRect(hwnd)
    x, y, right, bottom = rect
    width = right - x
    height = bottom - y

    print(f"Окно: X={x}, Y={y}, Width={width}, Height={height}")

    # Активируем окно
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # УЛУЧШЕННЫЕ координаты полей
    field_positions = [
        (width // 2, height // 4),  # первое поле - выше
        (width // 2, height // 2),  # второе поле - посередине
        (width // 2, height * 3 // 4 + 10),  # третье поле - ниже + смещение
    ]

    passwords = ["1234", "5678", '3456']

    for i, (rel_x, rel_y) in enumerate(field_positions):
        # Абсолютные координаты
        abs_x = x + rel_x
        abs_y = y + rel_y

        print(f"Поле {i + 1}: клик в ({abs_x}, {abs_y})")

        # Двойной клик для выделения возможного текста
        pyautogui.doubleClick(abs_x, abs_y)
        time.sleep(0.3)

        # Очистка через Ctrl+A
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)

        # Вводим пароль
        pyautogui.write(passwords[i], interval=0.05)
        print(f"  Введен пароль: {passwords[i]}")
        time.sleep(0.3)

        # После ввода пароля в первые два поля ждем немного дольше
        if i < 2:
            time.sleep(0.5)

    # Enter в последнем поле
    pyautogui.press('enter')
    print("✅ Все пароли введены и Enter нажат!")

    # После ввода паролей снова активируем главное окно конфигуратора
    time.sleep(2)
    config_windows = find_configurator_window()
    if config_windows:
        hwnd, window_title = config_windows[0]
        ensure_window_visible(window_title=window_title, maximize=True)
        print("✅ Главное окно конфигуратора снова активировано")

    return True


# Альтернативная функция с использованием TAB для навигации
def precise_coordinate_with_tab():
    print("=== АВТОМАТИЗАЦИЯ С ИСПОЛЬЗОВАНИЕМ TAB ===")

    window_title = "Пароли"

    if not ensure_window_visible(window_title=window_title, maximize=False):
        return False

    hwnd = win32gui.FindWindow(None, window_title)
    if not hwnd:
        print("❌ Окно не найдено")
        return False

    # Получаем координаты окна
    rect = win32gui.GetWindowRect(hwnd)
    x, y, right, bottom = rect
    width = right - x
    height = bottom - y

    print(f"Окно: X={x}, Y={y}, Width={width}, Height={height}")

    # Активируем окно
    win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.5)

    # Кликаем в первое поле
    first_field_x = x + width // 2
    first_field_y = y + height // 4
    print(f"Клик в первое поле: ({first_field_x}, {first_field_y})")

    pyautogui.click(first_field_x, first_field_y)
    time.sleep(0.5)

    passwords = ["1234", "5678", '3456']

    # Вводим пароли используя TAB для перехода между полями
    for i, password in enumerate(passwords):
        print(f"Поле {i + 1}: ввод пароля {password}")

        # Очищаем поле
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.1)
        pyautogui.press('delete')
        time.sleep(0.1)

        # Вводим пароль
        pyautogui.write(password, interval=0.05)
        time.sleep(0.3)

        # Переходим к следующему полю (кроме последнего)
        if i < len(passwords) - 1:
            pyautogui.press('tab')
            time.sleep(0.3)

    # Enter в последнем поле
    pyautogui.press('enter')
    print("✅ Все пароли введены через TAB!")

    # Возвращаем фокус на главное окно
    time.sleep(2)
    config_windows = find_configurator_window()
    if config_windows:
        hwnd, window_title = config_windows[0]
        ensure_window_visible(window_title=window_title, maximize=True)
        print("✅ Главное окно конфигуратора снова активировано")

    return True


# Обновленная основная последовательность выполнения
if __name__ == "__main__":
    print("🚀 ЗАПУСК АВТОМАТИЗАЦИИ КОНФИГУРАТОРА")
    print("=" * 50)

    # Сначала нажимаем кнопку в конфигураторе (поддерживает №118 и №116)
    connection_success = connection_enhanced()

    if connection_success:
        # Ждем немного перед вводом паролей
        time.sleep(2)

        # Сначала пробуем основной метод
        print("🔄 Пробуем основной метод...")
        success = precise_coordinate_automation_enhanced()

        # Если не сработало, пробуем метод с TAB
        if not success:
            print("🔄 Пробуем альтернативный метод с TAB...")
            time.sleep(1)
            precise_coordinate_with_tab()
    else:
        print("❌ Не удалось найти или активировать конфигуратор")