import serial
# Импортируем SerialException напрямую
from serial import SerialException
import csv
import datetime
import os
import time

# --- Настройки COM-порта ---
# Укажите правильный COM-порт для вашего устройства
# Например, на Windows это может быть 'COM3', на Linux '/dev/ttyUSB0' или '/dev/ttyACM0'
COM_PORT = '/dev/ttyUSB1'  # Замените на ваш COM-порт
BAUD_RATE = 9600  # Укажите правильную скорость передачи данных вашего устройства

# --- Настройки файла ---
# Папка для сохранения CSV-файлов
OUTPUT_DIR = 'com_data'
# Базовое имя файла (к нему будет добавлен timestamp)
BASE_FILENAME = 'com_data'

def create_unique_filename(base_name, directory):
    """Создает уникальное имя файла на основе текущего времени."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3] # До миллисекунд
    filename = f"{base_name}_{timestamp}.csv"
    return os.path.join(directory, filename)

def ensure_directory_exists(directory):
    """Проверяет существование папки и создает ее, если она не существует."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Создана папка: {directory}")

def read_from_com_and_write_to_csv(port, baud, output_dir, base_filename):
    """
    Читает данные с COM-порта и записывает их в CSV-файл.
    Каждый запуск создает новый файл.
    """
    ensure_directory_exists(output_dir)
    csv_filename = create_unique_filename(base_filename, output_dir)

    try:
        # Открываем COM-порт
        ser = serial.Serial(port, baud, timeout=1)
        print(f"Открыт порт {port} со скоростью {baud}")

        # Открываем CSV-файл для записи
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)

            # Записываем заголовок
            csv_writer.writerow(['Timestamp', 'COM_Data'])
            print(f"Данные будут записаны в файл: {csv_filename}")
            print("Нажмите Ctrl+C для остановки.")

            while True:
                try:
                    # Читаем строку из COM-порта
                    # Ожидаем, что данные приходят в виде строки, завершающейся символом новой строки (\n или \r\n)
                    line = ser.readline()

                    if line:
                        # Декодируем байты в строку
                        decoded_line = line.decode('utf-8', errors='ignore').strip()

                        try:
                            # Преобразуем данные в целое число (int64)
                            # Предполагаем, что декодированная строка является числом
                            com_data = int(decoded_line)

                            # Получаем текущее время с миллисекундами
                            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

                            # Записываем временную метку и данные в CSV
                            csv_writer.writerow([current_time, com_data])
                            # Для немедленной записи в файл (может снизить производительность)
                            # csvfile.flush()
                            # os.fsync(csvfile.fileno())

                            # Опционально: выводим прочитанные данные в консоль
                            # print(f"Прочитано: {decoded_line} -> Записано: {current_time}, {com_data}")

                        except ValueError:
                            # Обработка ошибки, если данные не являются корректным числом
                            print(f"Ошибка преобразования данных в число: '{decoded_line}'")
                        except Exception as e:
                            print(f"Произошла ошибка при обработке данных: {e}")

                # Теперь ловим SerialException напрямую
                except SerialException as e:
                    print(f"Ошибка чтения с COM-порта: {e}")
                    # Можно добавить задержку перед попыткой повторного чтения
                    time.sleep(0.1)
                except Exception as e:
                    print(f"Произошла непредвиденная ошибка в цикле чтения: {e}")
                    # Можно добавить задержку перед продолжением
                    time.sleep(0.1)

    # Теперь ловим SerialException напрямую
    except SerialException as e:
        print(f"Ошибка при открытии COM-порта {port}: {e}")
    except KeyboardInterrupt:
        print("\nЧтение остановлено пользователем.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    finally:
        # Закрываем порт при выходе из программы
        if 'ser' in locals() and ser.isOpen():
            ser.close()
            print(f"Порт {port} закрыт.")

# --- Запуск скрипта ---
if __name__ == "__main__":
    read_from_com_and_write_to_csv(COM_PORT, BAUD_RATE, OUTPUT_DIR, BASE_FILENAME)
