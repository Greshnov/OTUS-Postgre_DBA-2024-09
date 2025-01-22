# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 4. Логический уровень PostgreSQL

#### Часть 1. Создание нового кластера PostgreSQL
1. В VirtualBox установлена ОС Debian. Установлен PostgreSQL latest (15). (см. [Homework 1](/Homework/HW-1.md)).\
Создан новый кластер PostgreSQL 14 с новым путём для данных и новым портом.
```
# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters
# Устанавливаем кластер PostgreSQL версии 14
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt install postgresql-14
# Созданные кластеры
pg_lsclusters
# Изменение конфига (меняем порт)
nano /etc/postgresql/14/main/postgresql.conf
# Перезапуск кластера
sudo systemctl restart postgresql@14-main
...
```
![image](https://github.com/user-attachments/assets/b69aa7ee-d96d-4e19-b403-3c39b8befc6d)
![image](https://github.com/user-attachments/assets/ef5bc5d1-9ca6-46c0-904b-07639daa5425)
![image](https://github.com/user-attachments/assets/d6cf37db-ca11-4afc-936c-fbe385334bbe)
![image](https://github.com/user-attachments/assets/b24a1ff4-57f1-4b5c-98ef-b5c7ef77a4a5)
![image](https://github.com/user-attachments/assets/2d3d0dc0-6591-4809-b90c-77d171acde3d)
![image](https://github.com/user-attachments/assets/b1680902-d875-481d-81b5-39c5ce9c9255)



#### Часть 2. Создание новой БД и схемы
1. Создана база данных testdb и схема testnm в ней.
```
sudo su - postgres
# Подключаемся к кластеру
psql -p 5434

# Создаем БД
CREATE DATABASE testdb;
# Переходим в БД
\c testdb
# Создаем схему
CREATE SCHEMA testnm;
```
![image](https://github.com/user-attachments/assets/e74076b0-98a4-495c-be6c-17daaa0f9dd0)


#### Часть 3. Создание таблицы
1. Создана таблица t1 с одной записью.
```
CREATE TABLE t1(c1 integer);
INSERT INTO t1 values(1);
```
![image](https://github.com/user-attachments/assets/d2b7f7d1-5eda-4705-8aca-c97e4889855b)


#### Часть 4. Создание роли
1. Создана роль readonly и наделена правами
```
# Cоздание роли
CREATE role readonly;

# Право на подключение к базе данных
grant connect on DATABASE testdb TO readonly;

# Право на использование схемы testnm
grant usage on SCHEMA testnm to readonly;

# Право на select для всех таблиц схемы testnm
grant SELECT on ALL TABLES in SCHEMA testnm TO readonly; 
```
![image](https://github.com/user-attachments/assets/41acebc3-45bc-4a8a-be0e-471815c4f72c)


#### Часть 5. Создание пользователя
1. Создан пользовател testread с ролью readonly
```
# Cоздание пользователя
CREATE USER testread with password '123';
# Добавление роли
grant readonly TO testread;
```
![image](https://github.com/user-attachments/assets/c0606a8d-669b-4ec2-ae38-5faf44f5d3ad)

2. Выполнен вход под пользователем testread (перед этим разрешен вход по паролю - скорректирована конфигурация pg_hba.conf).
   Сделана попытка выборки из таблицы t1.
   Получили ошибку ***ERROR:  permission denied for table t1***.
   Причина в том, что таблица создана в схеме public. Права пользователю (через роль readonly) выдавались только на таблицы схемы testnm. Прав на public для роли readonly нет и других ролей у пользователя тоже нет.
   Таблица создалась в схеме public, так как при её создании не указали схему, где её создавать.
   Видим, что схема по-умолчанию - "$user", public. То есть первой схемой по-умолчанию является схема, имя которой аналогична имени пользователя. А вторая - public. Так как схемы с именем пользователя нет, то установилась public.

```
# Изменение конфигурации
sudo nano /var/lib/postgres/14/pg_hba.conf
peer > md5
# Перезагрузка кластера
sudo systemctl restart postgresql@14-main

# Вход в кластер
sudo su - postgres
psql -p 5434

# Вход под пользователем testread
\c testdb testread

select * from t1;

# Просмотр текущей схемы
select current_schema();

# Просмотр схемы по-умолчанию
show search_path;

```
![image](https://github.com/user-attachments/assets/cd201a37-321b-4ce6-8884-442b5fb0f9d2)
![image](https://github.com/user-attachments/assets/966e5e2b-c829-4d4c-bebc-49c7cabd0968)
![image](https://github.com/user-attachments/assets/1f64454d-e2b8-46f6-a7ad-8eeb86895bbb)
![image](https://github.com/user-attachments/assets/c3979f6b-1f30-4b20-833a-5f0396e55eb6)
![image](https://github.com/user-attachments/assets/951d22ad-abc5-43d8-99a1-6834599f7450)



#### Часть 6. Пересоздание таблицы
1. Удалена таблица t1 и создана заново с явным указанием имени схемы testnm.
```
sudo su - postgres
psql -p 5434

# Вход в базу
\c testdb
# Просмотр таблиц
\dt

# Удаление таблицы
drop table t1;

# Создание таблицы с указанием схему
CREATE TABLE testnm.t1(c1 integer);
INSERT INTO testnm.t1 values(1);

вернитесь в базу данных testdb под пользователем postgres
удалите таблицу t1
создайте ее заново но уже с явным указанием имени схемы testnm
вставьте строку со значением c1=1
```
![image](https://github.com/user-attachments/assets/bdc4c767-e354-4803-8674-a33ea75efb2c)




#### Часть 7. Проверка таблицы
1. Сделана попытка выборки из таблицы t1 из-под пользователя testread.\
   Результат - отказ в доступе, потому что выделение прав запросом ***grant SELECT on all TABLES in SCHEMA testnm TO readonly*** дало доступ только для существующих на тот момент времени таблиц, а таблица t1 пересоздавалась и оказалась уже незнакомой.
2. Настроено выделение доступов по умолчанию (ALTER default privileges ...). Повторный запрос от пользователя testread завершился той же ошибкой доступа.\
   Причина в том, что таблица была создана до установки прав доступа по-умолчанию.
3. Выполнен повторный запрос выделения прав. Теперь выборка от пользователя testread завершилась успешно. Создаваемые впредь таблицы в этой схеме будут доступны пользователю по-умолчанию.
```
# Вход в кластер
sudo su - postgres
psql -p 5434

# Вход под пользователем testread
\c testdb testread

# Выборка
select * from testnm.t1;

# Переключение пользователя на postgres
\c testdb postgres;

# Установка доступов по умолчанию
ALTER default privileges in SCHEMA testnm grant SELECT on TABLES to readonly;

# Вход под пользователем testread
\c testdb testread

# Выборка
select * from testnm.t1;

# Переключение пользователя на postgres
\c testdb postgres;

# Повторное назначение прав
# Право на select для всех таблиц схемы testnm
grant SELECT on ALL TABLES in SCHEMA testnm TO readonly; 

# Вход под пользователем testread
\c testdb testread

# Выборка
select * from testnm.t1;
```

![image](https://github.com/user-attachments/assets/dacec1ba-1ab2-451f-a0c8-3867f1306069)
![image](https://github.com/user-attachments/assets/ecd37d03-6fcf-45e2-85dd-82b0f411772b)



#### Часть 8. Создание второй таблицы
1. Выполнена команда создания таблицы t2 пользователем testread с ролью readonly. Таблица создалась и наполниась данными. Это связано с тем, что роль public добавляется новому пользователю автоматически, таким образом он может по умолчанию создавать объекты в схеме public в подключившейся базе.
```
create table t2(c1 integer);
insert into t2 values (2);

а как так? нам же никто прав на создание таблиц и insert в них под ролью readonly?
есть идеи как убрать эти права? если нет - смотрите шпаргалку
если вы справились сами то расскажите что сделали и почему, если смотрели шпаргалку - объясните что сделали и почему выполнив указанные в ней команды
теперь попробуйте выполнить команду create table t3(c1 integer); insert into t2 values (2);
расскажите что получилось и почему
```
![image](https://github.com/user-attachments/assets/5304885b-deae-4195-ba70-90fd9352a5d7)

2. У роли public отозваны права на создание в схеме public и все права на базу testdb.
```
\c testdb postgres; 
REVOKE CREATE on SCHEMA public FROM public; 
REVOKE ALL on DATABASE testdb FROM public; 
```
![image](https://github.com/user-attachments/assets/90141fd6-ee9c-4c4f-9fe9-d4f17d0d762c)

3. Выполнена команда создания таблицы t3 пользователем testread. Получена ошибка отказа в доступе. Отказ в доступе в схеме public. Это соответстует логиге, заданной выше (отозваны права)
```
\c testdb testread;
create table t3(c1 integer);
insert into t2 values (2);
```
![image](https://github.com/user-attachments/assets/940b5e5e-5b9e-4d18-ad36-99c76afc1df9)


