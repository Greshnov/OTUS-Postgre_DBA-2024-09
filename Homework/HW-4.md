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

2. Выполнен вход под пользователем testread. Сделана выборка из таблицы t1.
```
зайдите под пользователем testread в базу данных testdb
сделайте select * from t1;
получилось? (могло если вы делали сами не по шпаргалке и не упустили один существенный момент про который позже)
напишите что именно произошло в тексте домашнего задания
у вас есть идеи почему? ведь права то дали?
посмотрите на список таблиц
подсказка в шпаргалке под пунктом 20
а почему так получилось с таблицей (если делали сами и без шпаргалки то может у вас все нормально)
```



#### Часть 6. Пересоздание таблицы
1. Удалена таблица t1 и создана заново с явным указанием имени схемы testnm.
```
вернитесь в базу данных testdb под пользователем postgres
удалите таблицу t1
создайте ее заново но уже с явным указанием имени схемы testnm
вставьте строку со значением c1=1
```



#### Часть 7. Проверка таблицы
1. Сделана выборка из таблицы t1 из-под пользователя testread.
```
зайдите под пользователем testread в базу данных testdb
сделайте select * from testnm.t1;
получилось?
есть идеи почему? если нет - смотрите шпаргалку
как сделать так чтобы такое больше не повторялось? если нет идей - смотрите шпаргалку
сделайте select * from testnm.t1;
получилось?
есть идеи почему? если нет - смотрите шпаргалку
сделайте select * from testnm.t1;
получилось?
ура!
```

#### Часть 8. Создание второй таблицы
1. Выполнена команда создания таблицы t2.
```
теперь попробуйте выполнить команду create table t2(c1 integer); insert into t2 values (2);
а как так? нам же никто прав на создание таблиц и insert в них под ролью readonly?
есть идеи как убрать эти права? если нет - смотрите шпаргалку
если вы справились сами то расскажите что сделали и почему, если смотрели шпаргалку - объясните что сделали и почему выполнив указанные в ней команды
теперь попробуйте выполнить команду create table t3(c1 integer); insert into t2 values (2);
расскажите что получилось и почему
```
2. Убраны права на создание и изменение таблиц.
```
...
```
3. Выполнена команда создания таблицы t3.
```
...
```
