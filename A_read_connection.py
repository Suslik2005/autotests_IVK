import socket
import struct


def read_specific_register(ip, address, slave_id=1):
    """Читает один регистр и возвращает его значение"""

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((ip, 502))

        # Преобразуем адрес в два байта
        address_high = (address >> 8) & 0xFF
        address_low = address & 0xFF

        # Modbus запрос для чтения одного регистра
        modbus_request = bytes([
            # MBAP Header
            0x00, 0x08,  # Transaction ID
            0x00, 0x00,  # Protocol ID
            0x00, 0x06,  # Length
            # PDU
            slave_id,  # Unit ID
            0x03,  # Function Code (Read Holding Registers)
            address_high, address_low,  # Starting Address
            0x00, 0x01  # Quantity (1 регистр)
        ])

        sock.send(modbus_request)
        response = sock.recv(256)

        # Анализируем ответ
        if len(response) >= 9:
            if response[7] & 0x80:  # Ошибка
                sock.close()
                return None
            else:
                # Успешный ответ
                if len(response) >= 11:
                    register_value = struct.unpack('>H', response[9:11])[0]
                    sock.close()
                    return register_value

        sock.close()
        return None

    except Exception as e:
        return None


# Читаем только адрес 11952 и сохраняем в переменную right_password
right_password = read_specific_register("192.168.53.164", 11952, 1)

print(f"right_password = {right_password}")