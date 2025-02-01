# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 6. MVCC, vacuum и autovacuum 

#### Часть 1. Создание ВМ, установка PostgreSQL
1. В VirtualBox создана новая виртуальная машина (2core CPU, 4Gb RAM, SSD(VDI)) 10Gb), установлена ОС Debian. Установлен PostgreSQL 15. (см. [Homework 1](/Homework/HW-1.md)).
```
# Информация о процессоре
lscpu
# Информация о оперативной памяти
free -m

# Проверяем, запушен ли сервис PostgreSQL
sudo systemctl status postgresql.service

# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters
```
![image](https://github.com/user-attachments/assets/3171af9d-4bf2-4c71-bd05-7a6221e7b7d1)
![image](https://github.com/user-attachments/assets/4917fb5f-d651-4c8d-8499-21430438da8e)


![image](https://github.com/user-attachments/assets/8360bdca-58b9-4b5d-8a72-612321a07bbd)


#### Часть 2. Нагрузка кластера через утилиту pgbench
1. Кластер нагружен через утилиту pgbench (https://postgrespro.ru/docs/postgrespro/14/pgbench).Получили следующий показатель tps = 583.595052**.
```
# Заходим под пользователем postgres
sudo su - postgres

# Инициируем pgbench (создаются таблицы для теста в базе postgres)
pgbench -i postgres

# Запускаем pgbench
pgbench -c 8 -P 6 -T 60 -U postgres postgres
   
```
![image](https://github.com/user-attachments/assets/e7249f77-c044-4eb1-b3d0-a5b9c3b9b23d)


#### Часть 3. Изменение параметров кластера и повторная нагрузка
1. Установлены следующие параметры кластера
```
max_connections = 40
shared_buffers = 1GB
effective_cache_size = 3GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 500
random_page_cost = 4
effective_io_concurrency = 2
work_mem = 65536kB
min_wal_size = 4GB
max_wal_size = 16GB
```
Запрос на применение изменений
```
# Заходим под пользователем postgres
sudo su - postgres
psql

-- Memory Configuration
ALTER SYSTEM SET shared_buffers TO '1GB';
ALTER SYSTEM SET effective_cache_size TO '3GB';
ALTER SYSTEM SET work_mem TO '65536kB';
ALTER SYSTEM SET maintenance_work_mem TO '512MB';

-- Checkpoint Related Configuration
ALTER SYSTEM SET min_wal_size TO '4GB';
ALTER SYSTEM SET max_wal_size TO '16GB';
ALTER SYSTEM SET checkpoint_completion_target TO '0.9';
ALTER SYSTEM SET wal_buffers TO '16MB';

-- Network Related Configuration
ALTER SYSTEM SET max_connections TO '40';

-- Storage Configuration
ALTER SYSTEM SET random_page_cost TO '4.0';
ALTER SYSTEM SET effective_io_concurrency TO '2';

-- Other
ALTER SYSTEM SET default_statistics_target TO '500';

```

![image](https://github.com/user-attachments/assets/c5bce6c3-c7dc-45c6-9fbb-5e631a485b23)


2. Кластер нагружен через утилиту pgbench с теми же параметрами. Получили следующий показатель tps = **567.787385**. Значительных изменений не произошло. Небольшой выигрыш получился из-за лучшего набора конфигурации для текущих тех. условий (процессоры, память, диск). Однако, min_wal_size установлены впритых RAM, веделенную ВМ, а max_wal_size превышает RAM в четыре раза. Это улучшает производительность, но черевато выходу кластера и ВМ из строя - риск переполнения.
 ```
# Заходим под пользователем postgres
sudo su - postgres

# Инициируем pgbench (создаются таблицы для теста в базе postgres)
pgbench -i postgres

# Запускаем pgbench
pgbench -c 8 -P 6 -T 60 -U postgres postgres
   
```
![image](https://github.com/user-attachments/assets/ba90f8e7-71b1-479b-a34b-50f864457dbb)

<details>
   <summary>Описание наиболее важных параметров</summary>

1. shared_buffers - Используется для кэширования данных. По умолчанию низкое значение (для поддержки как можно большего кол-ва ОС). Согласно документации, рекомендуемое значение для данного параметра - 25% от общей оперативной памяти на сервере. PostgreSQL использует 2 кэша - свой (изменяется shared_buffers) и ОС. Редко значение больше, чем 40% окажет влияние на производительность.
   
2. max_connections - Максимальное количество соединений. Для изменения данного параметра придётся перезапускать сервер. Если планируется использование PostgreSQL как DWH, то большое количество соединений не нужно. Данный параметр тесно связан с work_mem. Поэтому будьте пределено аккуратны с ним

3. effective_cache_size - Служит подсказкой для планировщика, сколько ОП у него в запасе. Можно определить как shared_buffers + ОП системы - ОП используемое самой ОС и другими приложениями. За счёт данного параметра планировщик может чаще использовать индексы, строить hash таблицы. Наиболее часто используемое значение 75% ОП от общей на сервере. 

4. work_mem - Используется для сортировок, построения hash таблиц. Это позволяет выполнять данные операции в памяти, что гораздо быстрее обращения к диску. В рамках одного запроса данный параметр может быть использован множество раз. Если ваш запрос содержит 5 операций сортировки, то память, которая потребуется для его выполнения уже как минимум work_mem * 5. Т.к. скорее-всего на сервере вы не одни и сессий много, то каждая из них может использовать этот параметр по нескольку раз, поэтому не рекомендуется делать его слишком большим. Можно выставить небольшое значение для глобального параметра в конфиге и потом, в случае сложных запросов, менять этот параметр локально (для текущей сессии)
   
6. maintenance_work_mem - Определяет максимальное количество ОП для операций типа VACUUM, CREATE INDEX, CREATE FOREIGN KEY. Увеличение этого параметра позволит быстрее выполнять эти операции. Не связано с work_mem поэтому можно ставить в разы больше, чем work_mem

7. wal_buffers - Объём разделяемой памяти, который будет использоваться для буферизации данных WAL, ещё не записанных на диск. Если у вас большое количество одновременных подключений, увеличение параметра улучшит производительность. По умолчанию -1, определяется автоматически, как 1/32 от shared_buffers, но не больше, чем 16 МБ (в ручную можно задавать большие значения). Обычно ставят 16 МБ.
  
8. max_wal_size - Максимальный размер, до которого может вырастать WAL между автоматическими контрольными точками в WAL. Значение по умолчанию — 1 ГБ. Увеличение этого параметра может привести к увеличению времени, которое потребуется для восстановления после сбоя, но позволяет реже выполнять операцию сбрасывания на диск. Так же сбрасывание может выполниться и при достижении нужного времени, определённого параметром checkpoint_timeout

9. checkpoint_timeout - Чем реже происходит сбрасывание, тем дольше будет восстановление БД после сбоя. Значение по умолчанию 5 минут, рекомендуемое - от 30 минут до часа. 
Необходимо "синхронизировать" два этих параметра. Для этого можно поставить checkpoint_timeout в выбранный промежуток, включить параметр log_checkpoints и по нему отследить, сколько было записано буферов. После чего подогнать параметр max_wal_size.

</details>

#### Часть 4. Создание таблицы с 1 млн строк
1. Создана таблица test с текстовым полем val. Заполнена данными в размере 1млн строк 
```
# Заходим под пользователем postgres
sudo su - postgres

psql

create table test (txt char(100));

insert into test(txt) select 'some value' from generate_series(1,1000000);

select count(*) from test;

```
![image](https://github.com/user-attachments/assets/b4ff4890-4393-4410-a847-158a6095db44)

2. Размер файла с таблицей равен 128 MB. 
```
select pg_size_pretty(pg_total_relation_size('test'));
```

![image](https://github.com/user-attachments/assets/b715df80-7ab2-4531-beba-0b547cf151c2)


#### Часть 5. Обновление записей таблицы и контроль размера файла
1. Пять раз обновлены все записи - к каждому значению добавлен произвольный символ 
```
update test set txt = txt || '1';
update test set txt = txt || '2';
update test set txt = txt || '3';
update test set txt = txt || '4';
update test set txt = txt || '5';
```
![image](https://github.com/user-attachments/assets/d8cc4029-b990-4d72-a9e9-0302eed8d267)


2. Количество мертвых строчек в таблице **3230869**, автовакуум последний раз приходил до запуска обновления таблицы.
```
SELECT relname, n_live_tup, n_dead_tup, trunc(100*n_dead_tup/(n_live_tup+1))::float "ratio%", last_autovacuum FROM pg_stat_user_TABLEs WHERE relname = 'test';

```
![image](https://github.com/user-attachments/assets/e970cecf-79bd-4e0c-8b73-f10a3fb7ba10)


3. Спустя минуту пришел автовакуум. Размер файла с таблицей равен ??. 
```
SELECT relname, n_live_tup, n_dead_tup, trunc(100*n_dead_tup/(n_live_tup+1))::float "ratio%", last_autovacuum FROM pg_stat_user_TABLEs WHERE relname = 'test';

select pg_size_pretty(pg_total_relation_size('test'));
```
fr


4. Пять раз обновлены все записи - к каждому значению добавлен произвольный символ.
```
...
```

5. Размер файла с таблицей равен 542Mb. 
```
...
```
![image](https://github.com/user-attachments/assets/10cdbf07-fc99-48d9-bddc-e302ac9af209)


6. Отключен автовакуум на таблице test. 
```
...
```

7. Десять раз обновлены все записи - к каждому значению добавлен произвольный символ.
```
...
```

8. Размер файла с таблицей равен ??. Так как ??, то размер файла ??.
```
...
```

9. Автовакуум включен на таблице test.
```
...
```


