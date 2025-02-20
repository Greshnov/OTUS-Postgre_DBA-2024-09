import psycopg2
import time
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

WATCH_FOLDER = "/mnt/shared_external_data/ext_data/"

# Явно задаем параметры подключения к БД
DB_PARAMS = {
    "dbname": "etl",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    """Получаем подключение к БД с явными параметрами"""
    return psycopg2.connect(**DB_PARAMS)

def add_file_to_queue(file_path):
    """Добавляем новый файл в csv_queue"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO src.csv_queue (file_path) VALUES (%s)", (file_path,))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Файл {file_path} добавлен в csv_queue.")

class CSVFileHandler(FileSystemEventHandler):
    """Отслеживает появление новых файлов"""
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".csv"):
            time.sleep(1)  # Ожидание полной записи файла
            print(f"Файл создан: {event.src_path}")
            add_file_to_queue(event.src_path)

observer = PollingObserver()
observer.schedule(CSVFileHandler(), path=WATCH_FOLDER, recursive=False)
observer.start()

print(f"Наблюдение за папкой {WATCH_FOLDER} запущено...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
