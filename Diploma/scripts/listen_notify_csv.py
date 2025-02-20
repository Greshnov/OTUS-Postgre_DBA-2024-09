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
