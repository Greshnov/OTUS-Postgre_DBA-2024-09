# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 1. SQL и реляционные СУБД. Введение в PostgreSQL

#### Часть 1. Создание ВМ (виртуальной машины), подключение к ней, и установка СУБД PostgreSQL.
1. В VirtualBox установлена ОС Ubuntu, создан пользователь alex с правами на root.
2. На Windows-системе сгенерирован ключ, для подключения к ВМ по ssh.
![2025-01-16_12-30-12](https://github.com/user-attachments/assets/75108ee4-7cc0-408d-90c3-01e11cb59293)
3. На ВМ поднят ssh-сервер и добавлен открытая часть ssh-ключа пользователя.  
![image](https://github.com/user-attachments/assets/986f2226-28c0-48f2-9800-4c949b27c39d)
4. Через PuTTY (добавлена закрытая часть shh-ключа пользователя) осуществлено подключение к ВМ, установлен PostgreSQL. 
![image](https://github.com/user-attachments/assets/3a64be88-3624-44db-a756-a2e60af95f33)
![image](https://github.com/user-attachments/assets/b9ad0d57-22b6-4cf4-800e-03fdcb5cd5b8)

#### Часть 2. Работа с БД
1. Запущены две сессии, на каждой psql из-под пользователя postgres. В первой - создана таблица и наполнена данными.  
![image](https://github.com/user-attachments/assets/ba4826da-3e34-4369-adeb-51086aed71c1)
2. Текущий уровень изоляции - read committed. \
![image](https://github.com/user-attachments/assets/a0ed67e8-bb2b-4912-9551-f1dc0a933941)
3.
4. 

...
