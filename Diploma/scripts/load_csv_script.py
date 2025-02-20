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