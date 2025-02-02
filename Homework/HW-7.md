# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 7. Блокировки 

#### Часть 1. Настройка журнала сообщений сервера
1. В VirtualBox создана виртуальная машина (2core CPU, 4Gb RAM, SSD(VDI)) 10Gb), установлена ОС Debian. Установлен PostgreSQL 15. (см. [Homework 1](/Homework/HW-1.md), [Homework 6](/Homework/HW-6.md) ).

2. Сервер настроен так, чтобы в журнал сообщений сбрасывалась информация о блокировках, удерживаемых более 200 миллисекунд.

```
# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters

psql

# Включаем логирование блокировок
ALTER SYSTEM SET log_lock_waits = on;
ALTER SYSTEM SET deadlock_timeout = 200;

# Проверяет, требуется ли перезагрузка
SELECT pg_reload_conf();

\q
# Перезапускаем кластер
pg_ctlcluster 15 main restart

psql

# Показываем установленное значение
SHOW deadlock_timeout;

```
![image](https://github.com/user-attachments/assets/2b097c12-cd12-45f9-8c92-38a16e0f2d78)


3. Воспроизведена ситуация, при которой в журнале появились сообщения о блокировках.
```
# Создание БД
create database locks;
\c locks

# Создание таблицы
CREATE TABLE accounts(
  acc_no integer PRIMARY KEY,
  amount numeric
);

# Наполнение таблицы
INSERT INTO accounts VALUES (1,1000.00), (2,2000.00), (3,3000.00);

```

![image](https://github.com/user-attachments/assets/bb322696-8373-42f3-99e7-9a4d3f9b34b5)

Во второй сессии создадим транзакцию и обновим строку
```
# Заходим под пользователем postgres
sudo su - postgres

psql

\c locks

# Начало транзакции
BEGIN;
# Номер обслуживающего процесса
SELECT pg_backend_pid();

# Список блокировок только что начавшейся транзакция
SELECT locktype, relation::REGCLASS, virtualxid AS virtxid, transactionid AS xid, mode, granted
FROM pg_locks WHERE pid = 4389;
# Транзакция всегда удерживает исключительную (ExclusiveLock) блокировку собственного номера, а данном случае — виртуального. Других блокировок у этого процесса нет.

# Обновим запись в таблице
UPDATE accounts SET amount = amount - 100.00 WHERE acc_no = 1;

```

В первой сессии создадим транзакцию
```
BEGIN;
UPDATE accounts SET amount = amount + 100.00 WHERE acc_no = 1;
# Вторая команда UPDATE ожидает блокировку, возникшую из-за первой транзакции
```

Во второй сессии завершим транзакцию с задержкой 10 секунд
```
SELECT pg_sleep(10);
COMMIT;
```
Теперь первая транзакция может завершиться
```
COMMIT;
```
Проверяем наличие записи о блокоривках в журнале
```
tail -n 10 /var/log/postgresql/postgresql-15-main.log
```
Первая сессия\
![image](https://github.com/user-attachments/assets/2bd5ae1f-3c62-4c55-8ae7-cb7804cdc13a)

Вторая сессия\
![image](https://github.com/user-attachments/assets/bae42b79-01df-46f1-bdfa-53e12cf0176d)



#### Часть 2. Моделирование блокировки
1. Смоделированы блокировки при обновлении одной и той же строки тремя командами UPDATE в разных сеансах. 
```
...
```

2. В представлении pg_locks видим список блокировок
```
Пришлите список блокировок и объясните, что значит каждая.
```


#### Часть 3. Моделирование взаимоблокировки (три транзакции)
1. Воспроизведена взаимоблокировка трех транзакций.
```
...
```
2. Изучая журнал сообщений можно разобраться в ситуации - ... 


#### Часть 4. Моделирование взаимоблокировки (две транзакции)
1. Две транзакции, выполняющие единственную команду UPDATE одной и той же таблицы (без where), могут заблокировать друг друга?
```

```


