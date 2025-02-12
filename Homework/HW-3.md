# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 3. Физический уровень PostgreSQL

#### Часть 1. Установка PostgreSQL.
1. В VirtualBox установлена ОС Debian. Установлен PostgreSQL. (см. [Homework 1](/Homework/HW-1.md))
2. Кластер запущен
```
sudo -u postgres pg_lsclusters
```
![image](https://github.com/user-attachments/assets/963acaa4-8ebf-496e-a4b3-a9ae1dbc8c0f)

#### Часть 2. Создание таблицы и остановка PostgreSQL.
1. Из-под пользователя postgres в psql создана произвольная таблица с произвольным содержимым.
```
create table test(name text);
insert into test values('Name 1');
insert into test values('Name 2');
```
   ![image](https://github.com/user-attachments/assets/6292277a-f536-45f2-94a5-c596a4702f7c)

2. PostgreSQL остановлен.\
![image](https://github.com/user-attachments/assets/bb52d2bd-a49a-4da4-9a1e-0b4fc27ccd17)


#### Часть 3. Создание и подключение нового диска ВМ.
1. Создан новый диск к ВМ размером 10GB.\
   ![image](https://github.com/user-attachments/assets/4e163e88-8f3f-44b8-8063-c30a3c0690bd)\
![image](https://github.com/user-attachments/assets/05bd8796-6b4b-412f-9530-82ceaa512241)\
![image](https://github.com/user-attachments/assets/eaa370c8-15e3-498c-bcc8-f96e0ca60fd5)\


3. Новый диск добавлен к ВМ.
![image](https://github.com/user-attachments/assets/7ffb4c5a-b368-4fc9-9340-383d8b4c0fb6)
![image](https://github.com/user-attachments/assets/81494515-8f24-469f-bf54-101007a8c7b6)

5. Новый диск проинициализирован, файловая система подмонтирована.\
   (По инструкции https://www.digitalocean.com/community/tutorials/how-to-partition-and-format-storage-devices-in-linux)
```
# Просмотр устройств
lsblk
```
![image](https://github.com/user-attachments/assets/acc35217-d72b-49a1-8b13-4bf8005e4232)
```
# Установка утилиты parted для разметки диска
sudo apt update
sudo apt install parted
```
![image](https://github.com/user-attachments/assets/03d4b10d-270b-470f-a44b-d1fa83887e7e)
```
# Убеждаемся, что это наш новый диск 
sudo parted -l | grep Error
```
![image](https://github.com/user-attachments/assets/a5031f3f-422e-4705-9893-fe3df617b62f)

```
# Форматируем и размечаем диск
sudo parted /dev/sdb mklabel gpt
sudo parted -a opt /dev/sdb mkpart primary ext4 0% 100%
```
![image](https://github.com/user-attachments/assets/75faa0b0-f315-4d59-8725-6d796916c43c)

```
# Создаем файловую систему
sudo mkfs.ext4 -L datapartition /dev/sdb1
```
![image](https://github.com/user-attachments/assets/34801d80-bf6f-4eb2-8751-6afa30c467ff)
```
# Монтируем файловую систему
sudo mkdir -p /mnt/data
sudo mount -o defaults /dev/sdb1 /mnt/data
```
![image](https://github.com/user-attachments/assets/ffbb3928-68d4-4df3-9e7a-d24d38606918)
```
# Добавляем монтирование диска при загрузке системы
sudo nano /etc/fstab

/dev/sdb1 /mnt/data ext4 defaults 0 2
# или
#UUID=37ea3650-9492-417f-86ae-b0f9e819c9b0 /mnt/data ext4 defaults 0 2
```
![image](https://github.com/user-attachments/assets/b9f6d641-d9c2-47d2-81a8-86e1f8ebb601)
```
# Проверяем доступность смотрированного каталога
# Системная команда
df -h -x tmpfs
# Записываем тестовый файл, проверяем содержимое, удаляем
echo "success" | sudo tee /mnt/data/test_file
cat /mnt/data/test_file
sudo rm /mnt/data/test_file
```
![image](https://github.com/user-attachments/assets/2cc59a33-a169-4a13-b394-876ad56976fd)


6. Инстанс ВМ перезагружен, диск остается примонтированным.
   ```
   sudo reboot
   df -h -x tmpfs
   ```
![image](https://github.com/user-attachments/assets/a9b8a4ce-727a-4abb-9179-3485bf49badf)

#### Часть 4. Перенос содержимого PostgreSQL.
1. Пользователь postgres сделан владельцем /mnt/data 
```
sudo chown -R postgres:postgres /mnt/data/
```
![image](https://github.com/user-attachments/assets/0dcc65d5-6dab-4a4c-bf60-36eb75fb3e12)


2. Содержимое /var/lib/postgres/15 перенесено в /mnt/data
``` 
sudo mv /var/lib/postgresql/15 /mnt/data
```
![image](https://github.com/user-attachments/assets/28f08ee5-784c-4c62-8252-b7d5cf914162)

3. Попытка запуска кластера. Запуск не удался, так как настройки PostgeSQL остались без изменений и ссылаются на прежний каталог, которого уже нет.
```
sudo -u postgres pg_ctlcluster 15 main start
```
![image](https://github.com/user-attachments/assets/21a8ad61-3929-4fe9-9efc-fdc891ec31ee)


#### Часть 5. Настройка конфигурации PostgreSQL.
1. В файле postgresql.conf, раположенном в /etc/postgresql/15/main, изменено значение ***data_directory*** в секции FILE LOCATIONS - задан адрес нового примонтированного каталога, куда ранее был перенесен каталог с данными PostgreSQL.
```
sudo nano /etc/postgresql/15/main/postgresql.conf

data_directory = '/var/lib/postgresql/15/main'
>
data_directory = '/mnt/data/15/main'

```
![image](https://github.com/user-attachments/assets/735d8ccb-5160-43cd-aabc-0e9c8b37cd9e)\
![image](https://github.com/user-attachments/assets/03e032b3-3dcc-422c-8929-e60053278b7d)


2. Кластер запущен. Видим, что примонтирован нужный каталог с данными на новом примонтированном диске.
```
sudo -u postgres pg_ctlcluster 15 main start
sudo -u postgres pg_lsclusters
```
![image](https://github.com/user-attachments/assets/3462c28d-1ea1-4e33-a351-971bad5bf74b)
![image](https://github.com/user-attachments/assets/db243e97-4575-4c8d-ae58-250cac25d8bb)


3. Содержимое ранее созданной таблицы на месте.
```
sudo su postgres
psql
select * from test;
```
![image](https://github.com/user-attachments/assets/c71e1699-d053-46e7-b346-bf45e8e6f4c6)






