# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 5. Настройка PostgreSQL

#### Часть 1. Создание ВМ, установка PostgreSQL
1. В VirtualBox установлена ОС Debian. Установлен PostgreSQL 15. (см. [Homework 1](/Homework/HW-1.md)).
```
# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters
```
   ![image](https://github.com/user-attachments/assets/7dddaba5-068a-4465-aa48-f64e2737f4bf)\
2. Для возможности внешнего подключение из локальной сети был именен файл pg_hba.conf
```
# Файл конфигурации подключений
sudo nano /etc/postgresql/15/main/pg_hba.conf

# добавлена строка
# host    all             all             192.168.0.0/24         md5
# подключение по паролю (md5) с адресов 192.168.0.*

# Перезагрузка
sudo systemctl restart postgresql.service

# Вход под пользователем postgres
sudo su - postgres
psql

# Установка пароля пользоватлю postgres
ALTER USER postgres WITH PASSWORD 'postgres';

# Разрешение прослушивания портов (для доступа извне)
ALTER SYSTEM SET listen_addresses TO '*';
# Просмотр разрешений
show listen_addresses;

# Перезагрузка
sudo systemctl restart postgresql.service

```

![image](https://github.com/user-attachments/assets/ff273bce-6c61-4382-a21f-8ce8c94c36f2)\
![image](https://github.com/user-attachments/assets/dbe735eb-ac40-44ee-8c35-a9325e553243)

3. Текущие значения настроек
```
select * from pg_file_settings;
```
![image](https://github.com/user-attachments/assets/1e11a0a8-a962-47c4-bb37-0c138e9d8d04)

```
select * from pg_settings;
```
См. [Список настроек по-умолчанию](/Homework/ext/HW-5.pg_settings_default.html)

#### Часть 2. Нагрузка кластера через утилиту pgbench
1. Кластер нагружен через утилиту pgbench (https://postgrespro.ru/docs/postgrespro/14/pgbench). До настроек получили следующий показатель tps = **536.435490**.
```
sudo su - postgres
psql

# Создаём БД test
create database test;
\q

# Инициируем pgbench
pgbench -i test

# Запускаем pgbench
pgbench -c 50 -j 2 -P 10 -T 60 test
   
```
![image](https://github.com/user-attachments/assets/11c20267-e0f4-464e-9715-accebfa61685)\
![image](https://github.com/user-attachments/assets/c8ababdc-a249-492e-b1fe-a3bb71889005)


#### Часть 3. Настройка кластера PostgreSQL 15 на максимальную производительность
1. ...

#### Часть 4. Нагрузка кластера через утилиту pgbench
1. Кластер нагружен через утилиту pgbench (https://postgrespro.ru/docs/postgrespro/14/pgbench)


#### Часть 5. Результат
1. Удалось достичь значения tps ??, при этом установлены следующие параметры конфигурации.


