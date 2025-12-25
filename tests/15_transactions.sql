---- Transactions ----

--- Rollback
CREATE TABLE t1 (id INTEGER, val INTEGER);
BEGIN;
INSERT INTO t1 VALUES (1, 100);
ROLLBACK;
SELECT id, val FROM t1;
--- returns no rows
--- with columns:
id, val

--- Commit
CREATE TABLE t1 (id INTEGER, val INTEGER);
BEGIN;
INSERT INTO t1 VALUES (2, 200);
COMMIT;
SELECT id, val FROM t1;
--- returns:
2, 200
--- with columns:
id, val

--- Update + Commit
CREATE TABLE t1 (id INTEGER, val INTEGER);
INSERT INTO t1 VALUES (2, 200);
BEGIN;
UPDATE t1 SET val = 300 WHERE id = 2;
COMMIT;
SELECT id, val FROM t1;
--- returns:
2, 300
--- with columns:
id, val
