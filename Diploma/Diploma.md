# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Diploma. Автоматизация ETL-процессов в PostgreSQL


1. Монтируем сетевой диск
```sh
# вспомогательные средства монтирования Windows каталогов
sudo apt install cifs-utils

mkdir /mnt/shared_external_data

sudo mount -t cifs //192.168.0.13/shared /mnt/shared_external_data -o username=postgres,password=777,uid=postgres,gid=postgres,file_mode=0777,dir_mode=0777

```

2. Создаём БД, схему и таблицу
```sql
create database etl;

create schema src;

CREATE TABLE src.csv_queue (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL,
    processed BOOLEAN DEFAULT FALSE
);

CREATE OR REPLACE FUNCTION src.notify_csv() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('load_csv', '/mnt/shared_external_data/scripts/load_csv_script.py ' || NEW.file_path);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER src.trigger_csv_insert
AFTER INSERT ON csv_queue
FOR EACH ROW
EXECUTE FUNCTION notify_csv();

CREATE TABLE sales (
    date DATE NOT NULL,
    shop_id INTEGER NOT NULL,
    shop_address TEXT,
    barcode VARCHAR(50) NOT NULL,
    product_name TEXT,
    qty INTEGER NOT NULL,
    price NUMERIC(10,2) NOT NULL
);

```


3. Создаём Python скрипт мониторинга новых файлов (watch_csv_folder.py)
```python
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

```

4. Создаём Python скрипт мониторинга прослушивания событий (listen_notify_csv.py)
```python
import psycopg2
import select
import subprocess

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

def load_csv_to_postgres(script_path, file_path):
    """Запускаем внешний Python-скрипт для загрузки CSV"""
    print(f"Запущен скрипт {script_path} для обработки файла {file_path}")
    subprocess.run(["python3", script_path, file_path], check=True)
    print(f"Выполнен скрипт {script_path} для обработки файла {file_path}")

# Подключаемся к БД и слушаем события
conn = get_db_connection()
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cursor = conn.cursor()
cursor.execute("LISTEN load_csv;")

print("Ожидание новых файлов...")
while True:
    select.select([conn], [], [], None)
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop(0)
        message = notify.payload.split(" ")  # Разделяем путь к скрипту и путь к файлу
        script_path = message[0]
        file_path = message[1]
        print(f"Получено уведомление о файле: {file_path}, запуск скрипта: {script_path}")
        load_csv_to_postgres(script_path, file_path)

```


4. Создаём Python скрипт загрузки данныхbp csv-файла (load_csv_script.py)
```python
import psycopg2
import csv
import sys
from datetime import datetime  # ← Импортируем datetime

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

def convert_date(date_str):
    """Преобразует дату из формата DD.MM.YYYY в формат YYYY-MM-DD"""
    return datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")

def load_csv(file_path):
    """Загружает CSV-файл в PostgreSQL"""
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # Пропускаем заголовок

        for row in reader:
            row[0] = convert_date(row[0])  # Преобразуем дату в ISO-формат

            cursor.execute(
                "INSERT INTO src.sales (date, shop_id, shop_address, barcode, product_name, qty, price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)", row
            )

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Файл {file_path} успешно загружен в БД.")

if __name__ == "__main__":
    file_path = sys.argv[1]  # Получаем путь к файлу из аргументов командной строки
    load_csv(file_path)
```
5. Устанавливаем необходимые компоненты
```
sudo apt update

# Службы мониторинга файловой системы
sudo apt install inotify-tools

# Питон
sudo apt install python

# Установщик расширений Питона
sudo apt install python3 python3-pip

# Расширение Питона для реализации мониторинга
pip3 install --break-system-packages  watchdog

# Расширение Питона для реализации доступа к СУБД PostgreSQL
pip3 install --break-system-packages  psycopg2-binary

```

6. Добавляем автозапуск скриптов listen_notify_csv.py и load_csv_script.py в автозагрузку пользователя postgres
```
crontab -e

@reboot python3 /mnt/shared_external_data/scripts/watch_csv_folder.py >> /var/log/watch_csv.log 2>&1 &
@reboot python3 /mnt/shared_external_data/scripts/listen_notify_csv.py >> /var/log/listen_notify.log 2>&1 &

```
