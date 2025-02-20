# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Diploma

...
...
1. Монтируем сетевой диск
```
# вспомогательные средства монтирования Windows каталогов
sudo apt install cifs-utils

mkdir /mnt/shared_external_data

mount -t cifs //192.168.0.13/shared shared_external_data

//192.168.0.13/shared

sudo umount /var/lib/postgresql/shared_external_data
sudo mount -t cifs //192.168.0.13/shared /mnt/shared_external_data -o username=postgres,password=777,uid=postgres,gid=postgres,file_mode=0777,dir_mode=0777

```

![image](https://github.com/user-attachments/assets/eb3d9598-2dc3-493d-95ff-988d8839c22a)

2. Создаём БД, схему и таблицу
```
create database etl;

create schema src;

CREATE TABLE src.sales (
    date DATE NULL,
    shop_id INTEGER NULL,
    shop_address TEXT NULL,
    barcode BIGINT NULL,
    product_name TEXT NULL,
    qty INTEGER NULL,
    price NUMERIC(10,2) NULL
);


-- Функция для загрузки данных из CSV
CREATE OR REPLACE FUNCTION src.load_csv_data_to_sales(file_path TEXT) RETURNS VOID AS $$
BEGIN
    EXECUTE format(
        'COPY src.sales (date, shop_id, shop_address, barcode, product_name, qty, price) FROM %L DELIMITER '','' CSV HEADER;', 
        file_path
    );
END;
$$ LANGUAGE plpgsql;

sudo apt update
sudo apt install postgresql-plpython3

CREATE EXTENSION IF NOT EXISTS plpython3u;

CREATE OR REPLACE FUNCTION run_python_script(file_path TEXT) RETURNS VOID AS $$
    import subprocess
    subprocess.run(["python3", "/path/to/load_csv_to_postgres.py", file_path], check=True)
$$ LANGUAGE plpython3u;



CREATE OR REPLACE FUNCTION load_csv_to_sales(file_path TEXT) RETURNS VOID AS $$
    import csv
    import psycopg2
    
    conn = psycopg2.connect("dbname=your_db user=your_user password=your_password host=your_host")
    cursor = conn.cursor()
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=",")
        next(reader)  # Пропускаем заголовок
        
        for row in reader:
            cursor.execute(
                "INSERT INTO sales (date, shop_id, shop_address, barcode, product_name, qty, price) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)", row
            )
    
    conn.commit()
    cursor.close()
    conn.close()
$$ LANGUAGE plpython3u;

```


1. Подготовка среды
Перед тем как начать работу, важно убедиться, что все компоненты настроены правильно:

Монтирование сетевого диска на сервере PostgreSQL.
Настройка прав доступа: Убедись, что у PostgreSQL есть доступ к папке с CSV файлами, а также права на чтение/запись в эту папку.
В случае, если сервер работает на Linux и требуется подключение к SMB или NFS:

Для NFS — нужно убедиться, что путь к файлам правильно смонтирован в систему.
Для SMB (Windows-сетевой доступ) можно использовать cifs-utils для монтирования сетевого диска:
bash
Копировать
Редактировать
sudo mount -t cifs //server/shared /mnt/smb -o user=your_user,password=your_password
Пример пути после монтирования будет: /mnt/smb/csv_files/.

2. Структура таблицы в PostgreSQL
Необходимо заранее продумать структуру таблиц в PostgreSQL, в которые будут загружаться данные из CSV. Допустим, у нас есть таблица target_table, которая будет хранить данные.

Пример структуры:

sql
Копировать
Редактировать
CREATE TABLE target_table (
    id SERIAL PRIMARY KEY,
    column1 TEXT,
    column2 INTEGER,
    column3 DATE,
    column4 NUMERIC
);
Важно, чтобы структура таблицы соответствовала структуре CSV-файлов. Если структура данных изменяется, нужно предусмотреть логику для обработки новых столбцов или пропусков.

3. Обработка ошибок при загрузке данных
Когда файлы загружаются, могут возникать ошибки, например:

Проблемы с форматом данных (например, текст вместо числа).
Пропущенные или пустые значения в обязательных столбцах.
Важно настроить обработку ошибок:

Таблица для ошибок: Создать отдельную таблицу для хранения записей, которые не удалось загрузить, чтобы их можно было обработать позже.

Пример:

sql
Копировать
Редактировать
CREATE TABLE load_errors (
    id SERIAL PRIMARY KEY,
    file_name TEXT,
    error_message TEXT,
    row_data TEXT
);
В Python-скрипте можно ловить исключения и записывать ошибочные строки в таблицу load_errors.

Пример обработки ошибок в Python:

python
Копировать
Редактировать
try:
    cursor.execute(copy_query)
    conn.commit()
except Exception as e:
    error_message = str(e)
    with open(csv_file, 'r') as f:
        row_data = f.readlines()
    cursor.execute("INSERT INTO load_errors (file_name, error_message, row_data) VALUES (%s, %s, %s)",
                   (csv_file, error_message, row_data))
    conn.commit()
4. Трансформация данных перед загрузкой
В процессе загрузки можно выполнять предварительную очистку и трансформацию данных. Это можно делать на уровне SQL или с помощью Python.

Пример трансформации данных на уровне SQL:

sql
Копировать
Редактировать
CREATE OR REPLACE FUNCTION clean_data()
RETURNS void AS
$$
BEGIN
    -- Пример очистки данных: замена пустых строк на NULL
    UPDATE target_table
    SET column1 = NULL WHERE column1 = '';
    -- Можно добавить более сложные трансформации
END;
$$ LANGUAGE plpgsql;
Пример вызова этой функции после загрузки:

python
Копировать
Редактировать
cursor.execute("SELECT clean_data();")
conn.commit()
5. Автоматизация процесса
Теперь, чтобы запустить процесс на регулярной основе, настроим его через cron или pgAgent (если ты используешь PostgreSQL в Linux или Unix-среде).

Использование cron: Для регулярного запуска Python-скрипта (каждый час, к примеру):

bash
Копировать
Редактировать
0 * * * * /usr/bin/python3 /path/to/your/script.py
Это cron-задание будет запускать скрипт каждый час. Если тебе нужно настроить более точные интервалы, можно отрегулировать время запуска.

Использование pgAgent: Если ты хочешь интегрировать выполнение задач непосредственно с PostgreSQL, можно использовать pgAgent — расширение для PostgreSQL, которое позволяет планировать и управлять заданиями.

Пример создания задания в pgAgent для запуска Python-скрипта:

sql
Копировать
Редактировать
INSERT INTO pgagent.pga_job (jobid, jobname, jobdesc, jobenabled)
VALUES (1, 'ETL Job', 'Регулярная загрузка CSV данных', TRUE);

INSERT INTO pgagent.pga_jobstep (jstid, jobid, jstname, jstcode, jstenabled)
VALUES (1, 1, 'Run Python ETL Script', 'python3 /path/to/your/script.py', TRUE);
6. Мониторинг и отчетность
Для мониторинга процесса можно:

Логировать успешные и неудачные попытки загрузки.
Отправлять отчеты на email после выполнения задания. Это можно реализовать через Python (с использованием библиотеки smtplib) или через механизмы PostgreSQL.
Пример Python-скрипта для отправки отчета:

python
Копировать
Редактировать
import smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'recipient@example.com'

    with smtplib.SMTP('smtp.example.com') as server:
        server.login('your_email@example.com', 'your_password')
        server.sendmail('your_email@example.com', 'recipient@example.com', msg.as_string())

# После выполнения ETL-скрипта:
send_email("ETL Process Complete", "The ETL process has finished successfully.")
7. Оптимизация и масштабируемость
Индексация: Если таблицы с данными станут большими, важно добавить индексы на те столбцы, которые часто используются для поиска или фильтрации данных.
Пакетная загрузка: Для улучшения производительности можно загружать данные пакетами, используя временные таблицы, а затем копировать данные в основную таблицу с меньшими блокировками.
Заключение:
Процесс ETL с использованием CSV-файлов на сетевом диске — это мощный инструмент для интеграции данных в PostgreSQL. С помощью регулярных загрузок, очистки и трансформации данных ты можешь автоматизировать работу с большими объемами данных и минимизировать ошибки.
