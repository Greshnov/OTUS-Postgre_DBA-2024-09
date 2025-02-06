# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 8. Журналы 

#### Часть 1. Настройка контрольной точки
1. В VirtualBox создана виртуальная машина (2core CPU, 4Gb RAM, SSD(VDI)) 10Gb), установлена ОС Debian. Установлен PostgreSQL 15. (см. [Homework 1](/Homework/HW-1.md), [Homework 6](/Homework/HW-6.md) ).

2. Настроено выполнение контрольной точки раз в 30 секунд.

```
# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters

psql
# Текущее значение настройки выполнения контрольной точки
\x;
select * from pg_settings where name = 'checkpoint_timeout';
# или
show checkpoint_timeout;

# Устанавливаем значение настройки выполнения контрольной точки
ALTER SYSTEM SET checkpoint_timeout TO '30';

# Перезапускаем сервер
\q
pg_ctlcluster 15 main stop
pg_ctlcluster 15 main start

```
![image](https://github.com/user-attachments/assets/5c851c16-fb8b-4dd8-91cf-9467ae6ca5c7)


#### Часть 2. Нагрузка
1. В течение 10 минут c помощью утилиты pgbench подана нагрузка.
```
pgbench -i postgres
pgbench -P 10 -P 60 -T 600 postgres
```
![image](https://github.com/user-attachments/assets/3c3fd333-a019-4e69-bd9a-3bcbcd9a27af)

2. Измерен объем сгенерированных журнальных файлов за время нагрузки. В среднем на одну контрольную точку приходится объём, равный 20Мб. Поэтому образовалось несколько WAL-файлов на одну контрольную точку. Так как по умолчанию размер файла 16 Мб.
```
# Посмотрим, какие WAL-файлы находятся в системе
select * from pg_ls_waldir() limit 10;

# Посмотрим логи
nano  /var/log/postgresql/postgresql-15-main.log

```
![image](https://github.com/user-attachments/assets/95d6506f-c3b5-4896-8bcc-731682088f4e)
![image](https://github.com/user-attachments/assets/a6380a8f-14c9-4f23-92c7-9e0ab12dc3b0)


3. По данным статистики: контрольные точки выполнялись примерно на три секудны раньше (см. логи выше, значение write или разницу между записями в логах). Так произошло из-за того, что параметр checkpoint_completion_target равен 0.9, то есть считается как только 90% данных записаны в wal-файл контрольная точка считается завершенной и начинается отсчёт следующей.
   ```
   show checkpoint_completion_target;

   ```
![image](https://github.com/user-attachments/assets/7166de88-8167-4dec-9592-923cb805ffe1)


#### Часть 3. Сравнение tps в синхронном/асинхронном режиме
1. Утилита pgbench запущена в синхронном и асинхронном режиме. В синхронном получили значение tps, равным 528, в асинхронном - 997. Значение в асинхронном режиме почти в два раза выше, так как для синхронного — при фиксации транзакции продолжение работы невозможно до тех пор, пока все журнальные записи об этой транзакции не окажутся на диске; асинхронном — транзакция завершается немедленно, а журнал записывается в фоновом режиме.
```
psql
show synchronous_commit;
\q

# Синхронный
pgbench -i postgres
pgbench -P 10 -P 60 -T 60 postgres

# Асинхронный
# Отключаем синхронность
psql
alter system set synchronous_commit = off;
\q
pg_ctlcluster 15 main restart

pgbench -i postgres
pgbench -P 10 -P 60 -T 60 postgres
```
![image](https://github.com/user-attachments/assets/3c613f50-a94f-40b5-b68b-a5ffaa0e14d3)
![image](https://github.com/user-attachments/assets/8ca79782-d6d0-4cd0-bd6b-3469329de520)




#### Часть 4. Кластер с контрольной суммой
1. Создан новый кластер с включенной контрольной суммой страниц.
```
pg_createcluster 15 main-sum
pg_ctlcluster 15 main-sum restart
pg_lsclusters
```
![image](https://github.com/user-attachments/assets/6c745e89-b77d-4c90-8dd8-c97e55dce83d)

```
psql -p 5433

#Текущая настройка
SHOW data_checksums;
\q

# Останавливаем кластер
pg_ctlcluster 15 main-sum stop

# Устанавливаем использование контрольной суммы
/usr/lib/postgresql/15/bin/pg_checksums -e -D /var/lib/postgresql/15/main-sum

# Запускаем кластер
pg_ctlcluster 15 main-sum start

```
![image](https://github.com/user-attachments/assets/8a46da98-8f1b-4bc2-8700-b35173495482)



2. Создана таблица с несколькими значениями.
```
create table test(i int);

# Добавим значения
insert into test select s.id from generate_series(1, 100) as s(id); 
select * from test limit 10;

# Адрес файла таблицы
SELECT pg_relation_filepath('tablename');
```
![image](https://github.com/user-attachments/assets/28a39d73-e419-4e10-ab97-7fa55ff27b28)
![image](https://github.com/user-attachments/assets/37e91888-046d-42de-b108-830257d043bf)



3. Кластер выключен. Добавлено несколько символов в конец файла таблицы. Далее кластер включен и сделана выборка из таблицы. 
```
\q
# Выключаем кластер
pg_ctlcluster 15 main-sum stop

# Изменяем файл
nano /var/lib/postgresql/15/main-sum/base/5/16388

```
![image](https://github.com/user-attachments/assets/0fb1f341-835e-40a8-b1c5-faa183617e71)


4. Кластер включен. При попытке выполнить выборку из таблицы получена ошибка несоответствия контрольной суммы - так как файл был изменейн нами напрямую и кластер видит, что он не соответствует тому, о котором знает он на момент выключения. 
```
# Запускаем кластер
pg_ctlcluster 15 main-sum start

psql -p 5433
# Делаем выборку
select * from test limit 10;
```
![image](https://github.com/user-attachments/assets/b14f1761-c0f7-4a43-bf8f-6df91b8553d6)
![image](https://github.com/user-attachments/assets/48bf5fd0-97d7-4af4-b106-d0498e8a4e1b)

Проигнорировать ошибку и продолжить работу можно установкой настройки ignore_checksum_failure. Естественно, после восстановления нужно убрать. 
В нашем случае после установки пзначения on, выдаётся предупреждение о несоответствии контрольной суммы. При этом выборка выполняется, но видим, что данные в ней уже не соответствуют прежним (до изменения файла).
```
# Текущая настройка
show ignore_checksum_failure
# Меняем настройку
alter system set ignore_checksum_failure = on;

\q
# Выключаем кластер
pg_ctlcluster 15 main-sum stop

# Проверяем контрольную сумму
/usr/lib/postgresql/15/bin/pg_checksums -c -D /var/lib/postgresql/15/main-sum

# Включаем кластер
pg_ctlcluster 15 main-sum start

# Повторяем выборку
psql -p 5433
select * from test limit 10;

```
![image](https://github.com/user-attachments/assets/df7d2c54-6494-410a-b408-60adc28cd010)


