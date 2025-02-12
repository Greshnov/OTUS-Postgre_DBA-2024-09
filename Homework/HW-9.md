# OTUS-Postgre_DBA-2024-09
## Александр Грешнов

### Homework 9. Виды индексов. Работа с индексами и оптимизация запросов 

#### Часть 1. Создание индекса
1. В VirtualBox создана виртуальная машина (2core CPU, 4Gb RAM, SSD(VDI)) 10Gb), установлена ОС Debian. Установлен PostgreSQL 15. (см. [Homework 1](/Homework/HW-1.md), [Homework 6](/Homework/HW-6.md) ).

2. Создана база данных test с таблицей test. Создан индекс к этой таблице

```
# Заходим под пользователем postgres
sudo su - postgres
# Созданные кластеры
pg_lsclusters

psql

# Создадим БД
create database test;

# Перейдём в БД
\c test

# Создадим таблицу

create table test as 
select generate_series as id
	, generate_series::text || (random() * 10)::text as col2 
  , (array['Yes', 'No', 'Maybe'])[floor(random() * 3 + 1)] as is_okay
from generate_series(1, 50000);

# Сделаем тестовую выборку
select * from test limit 10;

# Посмотрим структуру таблицы
\d test

```

![image](https://github.com/user-attachments/assets/b0d9a0b3-9cff-4ea9-a09e-9fcf0ee4154e)


3. Создан индекс к этой таблице
```
# Просмотрим план запроса (до создания индекса)
explain 
select id from test where id = 1;

# Просмотрим план запроса со скоростью выполнения (до создания индекса)
explain 
explain analyze
select id from test where id = 1;

# Создадим индекс
create index idx_test_id on test(id);

# Просмотрим план запроса (после создания индекса)
explain 
explain 
select id from test where id = 1;

# Просмотрим план запроса со скоростью выполнения (после создания индекса)
explain analyze
select id from test where id = 1;

```

4. Результат команды explain. Видим, что запрос содержащий ограничение по полю, находящемуся в индексе, значительно ускорился. План запроса демонстрирует, что используется индекс.
```
 Seq Scan on test  (cost=0.00..1007.00 rows=1 width=4) (actual time=0.026..24.476 rows=1 loops=1)
   Filter: (id = 1)
   Rows Removed by Filter: 49999
 Planning Time: 0.151 ms
 Execution Time: 24.505 ms
```
```
 Index Only Scan using idx_test_id on test  (cost=0.29..8.31 rows=1 width=4) (actual time=0.142..0.144 rows=1 loops=1)
   Index Cond: (id = 1)
   Heap Fetches: 1
 Planning Time: 0.191 ms
 Execution Time: 0.167 ms
```
![image](https://github.com/user-attachments/assets/dad669d3-21ed-4a69-8fce-5e166914ebbd)



#### Часть 2. Индекс для полнотекстового поиска
1. Добавим поле типа tsvector к таблице для использования в полнотекстовом поиске. Перенесем туда значение колонки col2.
```
# Добавим столбец
alter table test add column col2_lexeme tsvector;

# Заполним данными
update test
set col2_lexeme = to_tsvector(col2);

```

![image](https://github.com/user-attachments/assets/fd55a098-c32f-4d2f-a921-f7ee7bc08453)


2. Создан индекс типа GIN (Generalized Inverted Index) к таблице
```
# Просмотрим план запроса со скоростью выполнения (до создания индекса) 
explain analyze
select * from test where col2_lexeme @@ to_tsquery('4955');

# Создадим индекс
CREATE INDEX search_index_col2 ON test USING GIN (col2_lexeme);

# Просмотрим план запроса со скоростью выполнения (после создания индекса) 
explain analyze
select * from test where col2_lexeme @@ to_tsquery('4955');
```

3. Результат команды explain. Видим, что запрос содержащий поиск текста в поле типа tsvector, находящемгося в индексе, значительно ускорился. План запроса демонстрирует, что используется созданный индекс.
```
 Seq Scan on test  (cost=0.00..14119.00 rows=250 width=66) (actual time=277.666..277.666 rows=0 loops=1)
   Filter: (col2_lexeme @@ to_tsquery('4955'::text))
   Rows Removed by Filter: 50000
 Planning Time: 0.127 ms
 Execution Time: 277.686 ms

```

```
 Bitmap Heap Scan on test  (cost=18.19..658.94 rows=250 width=66) (actual time=0.022..0.023 rows=0 loops=1)
   Recheck Cond: (col2_lexeme @@ to_tsquery('4955'::text))
   ->  Bitmap Index Scan on search_index_col2  (cost=0.00..18.12 rows=250 width=0) (actual time=0.020..0.021 rows=0 loops=1)
         Index Cond: (col2_lexeme @@ to_tsquery('4955'::text))
 Planning Time: 0.147 ms
 Execution Time: 0.048 ms

```

![image](https://github.com/user-attachments/assets/ac2ffdce-e3b5-4f95-829f-7bb084074565)
![image](https://github.com/user-attachments/assets/bc3eaf97-23cb-49be-9a5d-a5b166f951f3)




#### Часть 3. Индекс на часть таблицы или индекс на поле с функцией
1. Создан индекс к части таблице, в которой значение поля id больше 25000 (половина записей).
```
# Просмотрим план запроса со скоростью выполнения (до создания индекса) 
explain analyze
select * from test where id between 30000 and 40000;

# Создадим индекс
create index idx_test_id_25000 on test(id) where id > 25000;

# Просмотрим план запроса со скоростью выполнения (после создания индекса) 
explain analyze
select * from test where id between 30000 and 40000;

drop index idx_test_id_25000;
drop index idx_test_id;

```
2. Результат команды explain. Видим, что по сравнению с обычным индексом выигрыша во времени не получилось. Значит и обычный индекс на таком объёме строк работает хорошо. По сравнению с запросом к таблице без этих индексов результат естественно значительно лучше. Частичный индекс даст эффект, если он будет содержать меньше половины от всего объёма данных. После сужения данных для индекса (20% от общего объёма), получили выигрыш в два раза по сравнению с обычным индексом.

```
 Index Scan using idx_test_id on test  (cost=0.29..619.79 rows=9925 width=66) (actual time=0.013..7.017 rows=10001 loops=1)
   Index Cond: ((id >= 30000) AND (id <= 40000))
 Planning Time: 0.164 ms
 Execution Time: 8.307 ms

```

```
 Index Scan using idx_test_id_25000 on test  (cost=0.29..515.79 rows=9925 width=66) (actual time=0.073..8.148 rows=10001 loops=1)
   Index Cond: ((id >= 30000) AND (id <= 40000))
 Planning Time: 0.621 ms
 Execution Time: 9.501 ms
```

```
 Seq Scan on test  (cost=0.00..1744.00 rows=9925 width=66) (actual time=11.413..20.225 rows=10001 loops=1)
   Filter: ((id >= 30000) AND (id <= 40000))
   Rows Removed by Filter: 39999
 Planning Time: 0.331 ms
 Execution Time: 21.477 ms
```

![image](https://github.com/user-attachments/assets/fcfc2532-6fd1-4fc9-91e3-e03d2fa1a924)


![image](https://github.com/user-attachments/assets/b33b2250-9e92-4f4a-bafb-ba6e0e8cf0ee)

![image](https://github.com/user-attachments/assets/195851a9-e1a9-492a-8064-7e1d53bc4678)

```
# Просмотрим план запроса со скоростью выполнения (до создания индекса) 
explain analyze
select * from test where id = 48000;

# Создадим индекс
create index idx_test_id_25000 on test(id) where id > 40000;

# Просмотрим план запроса со скоростью выполнения (после создания индекса) 
explain analyze
select * from test where id = 48000;

```

```
 Index Scan using idx_test_id_25000 on test  (cost=0.29..8.30 rows=1 width=66) (actual time=0.028..0.030 rows=1 loops=1)
   Index Cond: (id = 48000)
 Planning Time: 0.156 ms
 Execution Time: 0.045 ms

```
![image](https://github.com/user-attachments/assets/ca07baf3-b142-4061-a04f-ba177513749e)

![image](https://github.com/user-attachments/assets/d8b47863-345a-43e7-8f41-199a86cfe3ea)



#### Часть 4. Индекс на несколько полей
1. Создан индекс к таблице
```
# Создадим индекс

```
2. Результат команды explain




