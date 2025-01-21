# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 2. Физический уровень PostgreSQL

#### Часть 1. Установка PostgreSQL.
1. В VirtualBox установлена ОС Debian. Установлен PostgreSQL. (см. [Homework 1](/Homework/HW-1.md))
2. Кластер запущен
```
sudo -u postgres pg_lsclusters
```
![image](https://github.com/user-attachments/assets/78695a8d-1a65-40e3-b74a-05ed1c9ddd45)

#### Часть 2. Создание таблицы и остановка PostgreSQL.
1. Из-под пользователя postgres в psql создана произвольная таблица с произвольным содержимым.
```
create table test(name text);
insert into test values('Name 1');
insert into test values('Name 2');
```
2. PostgreSQL остановлен.

#### Часть 3. Создание и подключение нового диска ВМ.
1. Создан новый диск к ВМ размером 10GB

2. Новый диск добавлен к ВМ. Зайти в режим ее редактирования и дальше выбрать пункт attach existing disk

3. Новый диск проинициализирован, файловая система подмрнтирована. Только не забывайте менять имя диска на актуальное, в вашем случае это скорее всего будет /dev/sdb - https://www.digitalocean.com/community/tutorials/how-to-partition-and-format-storage-devices-in-linux

4. Инстанс перезагружен, диск остается примонтированным. (если не так смотрим в сторону fstab)

#### Часть 4. Перенос содержимого PostgreSQL.
1. Пользователь postgres сделан владельцем /mnt/data 
```
- chown -R postgres:postgres /mnt/data/
```

2. Содержимое /var/lib/postgres/15 перенесено в /mnt/data
``` 
mv /var/lib/postgresql/15 /mnt/data
```

3. Попытка запуска кластера. напишите получилось или нет и почему
```
sudo -u postgres pg_ctlcluster 15 main start
```

#### Часть 5. Настройка конфигурации PostgreSQL.
1. В файлах, раположенных в /etc/postgresql/15/main, изменен конфигурационный параметр, который .... напишите что и почему поменяли
```
change
```
2. Кластер запущен. напишите получилось или нет и почему
```
sudo -u postgres pg_ctlcluster 15 main start
```
3. Содержимое ранее созданной таблицы на месте.
```
select * from 
```





