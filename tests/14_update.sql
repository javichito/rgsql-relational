---- Update ----

--- can update a single column with WHERE clause
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (1, 'Alice', 30, 'alice@example.com');
INSERT INTO t1 VALUES (2, 'Bob', 25, 'bob@example.com');
UPDATE t1 SET age = 31 WHERE id = 1;
SELECT id, name, age, email FROM t1 WHERE id = 1;
--- returns:
1, 'Alice', 31, 'alice@example.com'
--- with columns:
id, name, age, email

--- can update multiple columns with WHERE clause
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (2, 'Bob', 25, 'bob@example.com');
UPDATE t1 SET age = 26, name = 'Robert' WHERE id = 2;
SELECT id, name, age, email FROM t1 WHERE id = 2;
--- returns:
2, 'Robert', 26, 'bob@example.com'
--- with columns:
id, name, age, email

--- can update with expression
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (3, 'Charlie', 35, 'charlie@example.com');
UPDATE t1 SET age = age + 1 WHERE id = 3;
SELECT id, age FROM t1 WHERE id = 3;
--- returns:
3, 36
--- with columns:
id, age

--- can update all rows without WHERE clause
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (1, 'Alice', 30, 'alice@example.com');
INSERT INTO t1 VALUES (2, 'Bob', 25, 'bob@example.com');
INSERT INTO t1 VALUES (3, 'Charlie', 35, 'charlie@example.com');
UPDATE t1 SET email = 'updated@example.com';
SELECT email FROM t1 ORDER BY id ASC;
--- returns:
'updated@example.com'
'updated@example.com'
'updated@example.com'
--- with columns:
email

--- can update with FROM clause join
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (1, 'Alice', 31, 'alice@example.com');
INSERT INTO t1 VALUES (2, 'Robert', 26, 'bob@example.com');
INSERT INTO t1 VALUES (3, 'Charlie', 36, 'charlie@example.com');
CREATE TABLE t2 (user_id INTEGER, amount INTEGER);
INSERT INTO t2 VALUES (1, 100);
INSERT INTO t2 VALUES (3, 200);
UPDATE t1 SET age = age + amount FROM t2 WHERE t1.id = t2.user_id;
SELECT id, age FROM t1 ORDER BY id ASC;
--- returns:
1, 131
2, 26
3, 236
--- with columns:
id, age

--- can use RETURNING clause
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (1, 'Alice', 131, 'updated@example.com');
UPDATE t1 SET name = 'Alice_Ret' WHERE id = 1 RETURNING id, name;
--- returns:
1, 'Alice_Ret'
--- with columns:
id, name

--- can use RETURNING with expressions and aliases
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (2, 'Robert', 26, 'updated@example.com');
UPDATE t1 SET age = age + 1 WHERE id = 2 RETURNING id, age AS new_age, name;
--- returns:
2, 27, 'Robert'
--- with columns:
id, new_age, name

--- returns no rows when update matches nothing
CREATE TABLE t1 (id INTEGER, name STRING, age INTEGER, email STRING);
INSERT INTO t1 VALUES (1, 'Alice', 30, 'alice@example.com');
UPDATE t1 SET name = 'Ghost' WHERE id = 999;
SELECT id, name, age, email FROM t1 WHERE id = 999;
--- returns no rows
--- with columns:
id, name, age, email

--- updating multiple rows with RETURNING should have unique column names
CREATE TABLE t1 (id INTEGER, val INTEGER);
INSERT INTO t1 VALUES (1, 10), (2, 20);
UPDATE t1 SET val = val + 1 RETURNING val;
--- returns:
11
21
--- with columns:
val
