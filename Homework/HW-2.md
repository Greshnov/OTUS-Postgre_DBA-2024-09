# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 2. Установка PostgreSQL

#### Часть 1. Установка Docker с сервером PostgreSQL.
1. В VirtualBox установлена ОС Debian. Выполнена команда для установки Docker из документации Ubuntu ([https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)).\
![image](https://github.com/user-attachments/assets/b27beeb8-6d29-49da-872f-36a00f02e1a5)
Так как по оишбке был выполнен запрос для Ubuntu, вместо Debian, пакеты загрузить не удалось. Была выполнена корректная команда из документации Debian ([https://docs.docker.com/engine/install/debian/](https://docs.docker.com/engine/install/debian/)).\
![image](https://github.com/user-attachments/assets/aab8972e-ca95-417c-987b-714c44913587)\
Для проверки правильности установки - выполнена команда из документации. Результат - Docker установлен.\
![image](https://github.com/user-attachments/assets/d19696db-dc9a-4946-93b7-f39aec61631b)
2. Создан каталог /var/lib/postgres (из-под пользователя root)\
   ![image](https://github.com/user-attachments/assets/2a58e3b3-457e-4e79-9113-cb5f6cd608b7)
3. Загружен образ PostgeSQL (https://hub.docker.com/_/postgres)\
   ![image](https://github.com/user-attachments/assets/444e153a-77df-4895-aab1-6d3076c582fb)
4. Создана Docker-сеть. 
```
sudo docker network create pg-net
```
   ![image](https://github.com/user-attachments/assets/9780c546-f6ce-467e-bc4e-c00ba3d9a427)

5. Запущен контейнер с образом PostgeSQL. Добавлено перенаправление порта 5432 на 5433, так как на ВМ уже установлен PostgreSQL. Примонтирован ранее созданный каталог /var/lib/postgres для данных /var/lib/postgresql/data.
```
sudo docker run --name pg-docker --network pg-net -e POSTGRES_PASSWORD=postgres -d -p 5433:5432 -v /var/lib/postgres:/var/lib/postgresql/data postgres:latest
```
![image](https://github.com/user-attachments/assets/64302698-41a2-4606-a4c0-ae29ce4096a7)

#### Часть 2. Установка Docker с клиентом PostgreSQL.
1. Запущен контейнер с клиентом PostgeSQL.
```
sudo docker run -it --rm --network pg-net --name pg-client postgres:latest psql -h pg-docker -U postgres
```
![image](https://github.com/user-attachments/assets/b5a9a6dc-b178-42f6-b88e-76ee0c938a1c)

2. Подключены из контейнера с клиентом к контейнеру с сервером. Создана таблица book.
```
create table book(title text, author text, year int);
insert into book(title, author, year) values('First book', 'First Author', 2024);
insert into book(title, author, year) values('Second book', 'First Author', 2025);
select * from book;
```
![image](https://github.com/user-attachments/assets/93b21670-b052-4419-8f1e-bba035714d95)
#### Часть 3. Подключение к Docker с сервером извне.
1. Подключены через программу DBeaver с другого ПК, находящегося в той же локальной сети.
```
# Получениие внешнего адреса виртуальной машины
ip -c a
```
![image](https://github.com/user-attachments/assets/49d08d1a-0c0e-4c3f-b474-074206a5c48e)\
![image](https://github.com/user-attachments/assets/9c777f9a-2ce6-4c86-af03-dc13c08450f9)\
![image](https://github.com/user-attachments/assets/ee554d0c-7f3b-4f27-b3bc-bf943ea4e482)

#### Часть 4. Удаление Docker с сервером и повторное создание.
1. Удален контейнер с сервером
```
sudo docker stop pg-docker
sudo docker rm  pg-docker
```
![image](https://github.com/user-attachments/assets/410ae12a-57a9-40d2-804b-df5b7a0938ff)\
В процессе выполнения (остановка контейнера) была ошибка отказа в доступе. Выполнено выделение прав пользователю и перезагрузка ВМ.
```
sudo usermod -a -G docker alex
sudo reboot
```
![image](https://github.com/user-attachments/assets/1943d7d0-45ac-451c-8de0-7eca5f4f5a8c)
2. Создан контейнер с сервером заново.\
![image](https://github.com/user-attachments/assets/2e4a11f1-0e73-4a08-b9ac-a0df85fa725a)
3. Подключены из контейнера с клиентом. Созданная ранее таблица и данные в ней обнаружены. Даннные на месте, так как примонтирован тот же каталог что и впервом случае. После удаление контейнера данные остались в примонтированном каталоге.\
![image](https://github.com/user-attachments/assets/14e5a1e5-b87d-410a-8936-08dba872f58f)








