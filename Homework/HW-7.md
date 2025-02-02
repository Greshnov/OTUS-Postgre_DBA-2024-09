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
1. Смоделированы блокировки при обновлении одной и той же строки тремя командами UPDATE в разных сеансах.\

Для удобства мониторинга построено представление над pg_locks. Сделан вывод чуть более компактным и ограничен только интересными блокировками (отбрасываем блокировки виртуальных номеров транзакций, индекса на таблице accounts, pg_locks и самого представления).
```
\c locks

CREATE VIEW locks_v AS
SELECT pid,
       locktype,
       CASE locktype
         WHEN 'relation' THEN relation::regclass::text
         WHEN 'transactionid' THEN transactionid::text
         WHEN 'tuple' THEN relation::regclass::text||':'||tuple::text
       END AS lockid,
       mode,
       granted
FROM pg_locks
WHERE locktype in ('relation','transactionid','tuple')
AND (locktype != 'relation' OR relation = 'accounts'::regclass);
```

**Первая сессия**. Транзакция удерживает блокировку таблицы и собственного номера
```  
-- Первая транзакция
BEGIN;
SELECT txid_current(), pg_backend_pid();

-- Обновление строки
UPDATE accounts SET amount = amount + 100.00 WHERE acc_no = 1;
SELECT * FROM locks_v WHERE pid = 4512;

```
![image](https://github.com/user-attachments/assets/322c0ace-c98d-4439-9c0f-5c740a598bae)

**Вторая сессия**. Транзакция заблокирована.
```
sudo su - postgres
psql
\c locks

-- Вторая транзакция
BEGIN;
SELECT txid_current(), pg_backend_pid();
-- Обновление строки
UPDATE accounts SET amount = amount + 100.00 WHERE acc_no = 1;
```
![image](https://github.com/user-attachments/assets/749f0276-8c62-4535-ba18-c6dc2a81eed4)

**Первая сессия**. Видим, что вторая транзакция захватила версию строки (выделено красным) - granted = t, значит доступ есть, но заблокирована первой транзакцией (выделено зеленым) ShareLock granted = f, значит доступа нет.
```
SELECT * FROM locks_v WHERE pid = 4583;

```
![image](https://github.com/user-attachments/assets/7563d09f-e902-46cb-84f3-bcfda23c809b)


**Третья сессия**. Транзакция заблокирована.
```
sudo su - postgres
psql
\c locks

-- Третья транзакция
BEGIN;
SELECT txid_current(), pg_backend_pid();
-- Обновление строки
UPDATE accounts SET amount = amount + 100.00 WHERE acc_no = 1;
```
![image](https://github.com/user-attachments/assets/b6bdbb2c-0454-40a9-9d1f-8c07bfdd3075)

**Первая сессия**. Видим, что третья транзакция заблокирована и пытается захватить блокировку версии строки (выделено красным), но безуспешно, так как операция заблокирована второй транзакцией (granted = f, значит доступа нет).
```
SELECT * FROM locks_v WHERE pid = 4639;

```

![image](https://github.com/user-attachments/assets/12ccdf51-7b78-4d0c-be23-04c9d36ee57c)


2. В представлении pg_stat_activity видим очередь блокировок
```
SELECT pid, wait_event_type, wait_event, pg_blocking_pids(pid)
FROM pg_stat_activity
WHERE backend_type = 'client backend' ORDER BY pid;
```
![image](https://github.com/user-attachments/assets/899d14fe-265e-4db6-8272-554394a5b3e0)

3. Завершим последовательно транзакции во всех трёх сессиях.
**Первая сессия**
```
COMMIT;
SELECT * FROM locks_v WHERE pid = 4512;
SELECT * FROM locks_v WHERE pid = 4583;
SELECT * FROM locks_v WHERE pid = 4639;
```

После завершения первой видим, что запрос во второй транзакции выполнился, вторая транзакция разблокирована (нет значений granted = f). Третья транзакция ожидает выполнения второй (появилась запись ShareLock granted = f).\
![image](https://github.com/user-attachments/assets/405a18c6-f83a-4402-874b-c1f80bbfb41b)\

После завершения второй видим, что запрос в третьей транзакции выполнился, третья транзакция разблокирована (нет значений granted = f).\
![image](https://github.com/user-attachments/assets/a8cb50a7-3f81-4afe-b586-ed4fac22b844)\

После завершения третьей транзакции блокировок нет.\
![image](https://github.com/user-attachments/assets/2a528dad-6319-421c-a1b2-b2a392d58da4)


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


