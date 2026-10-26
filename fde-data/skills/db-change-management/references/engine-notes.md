# Engine-specific migration notes

Load only the section matching the detected engine and version. For an engine not
covered here, use its matching official documentation (or an approved local copy)
and record unresolved lock behavior as unverified. Do not borrow another engine's
syntax or guarantees.

## PostgreSQL 15

`ALTER TABLE ... ADD COLUMN currency varchar(3) NULL` avoids a table rewrite, but
still acquires an `ACCESS EXCLUSIVE` table lock. It can wait behind another
transaction and block other traffic while waiting or until its transaction ends.
Use short transactions and explicit limits; these illustrative limits must be
agreed for the target environment:

```sql
BEGIN;
SET LOCAL lock_timeout = '2s';
SET LOCAL statement_timeout = '10s';
ALTER TABLE orders ADD COLUMN currency varchar(3) NULL;
COMMIT;
```

If a statement fails, issue `ROLLBACK` before doing anything else. Do not leave an
aborted transaction open or automatically retry a busy production table in a
tight loop. Rehearse and verify the actual lock wait and duration.

An `UPDATE` backfill acquires `ROW EXCLUSIVE` on the table and row locks on affected
rows. Commit each bounded batch; enforce statement/lock timeouts and pause on
replica lag or contention. Batching reduces lock duration; it does not remove locks.

Prefer leaving an additive column in place when rolling the application back.
Dropping it loses new data and needs its own consumer and retention assessment.

Sources: [PostgreSQL 15 ALTER TABLE](https://www.postgresql.org/docs/15/sql-altertable.html),
[locking](https://www.postgresql.org/docs/15/explicit-locking.html), and
[statement/lock timeouts](https://www.postgresql.org/docs/15/runtime-config-client.html).
