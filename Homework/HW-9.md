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

2. Создан индекс к таблице
```
# Просмотрим план запроса со скоростью выполнения (до создания индекса) 
explain analyze
select * from test where col2_lexeme @@ to_tsquery('4955') limit 10;

# Создадим индекс
CREATE INDEX search_index_col2 ON test USING GIN (col2_lexeme);

# Просмотрим план запроса со скоростью выполнения (после создания индекса) 
explain analyze
select * from test where col2_lexeme @@ to_tsquery('4955') limit 10;
```

3. Результат команды explain
```
...
```


#### Часть 3. Индекс на часть таблицы или индекс на поле с функцией
1. Создан индекс к таблице
```
# Создадим индекс

```
2. Результат команды explain

#### Часть 4. Индекс на несколько полей
1. Создан индекс к таблице
```
# Создадим индекс

```
2. Результат команды explain




