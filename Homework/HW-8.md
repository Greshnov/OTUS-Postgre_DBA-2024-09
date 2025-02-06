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
```
![image](https://github.com/user-attachments/assets/772be927-1736-4eba-bd53-b07e4f9f9b0a)

```
# Останавливаем кластер
pg_ctlcluster 15 main-sum stop

# Устанавливаем использование контрольной суммы
```



2. Создана таблица с несколькими значениями. Выключите кластер. Измените пару байт в таблице. Включите кластер и сделайте выборку из таблицы. Что и почему произошло? как проигнорировать ошибку и продолжить работу?
```
...
```

3. Кластер выключен. Изменена пара байт в таблице. Включите кластер и сделайте выборку из таблицы. Что и почему произошло? как проигнорировать ошибку и продолжить работу?
```
...
```

4. Кластер включен и сделана выборка из таблицы. Что и почему произошло? как проигнорировать ошибку и продолжить работу?
```
...
```
