---
name: db-change-management
description: Change a schema against a live production database without taking an outage - expand and contract patterns, zero-downtime DDL, lock and replication-lag behavior on large tables, reversibility, and coordinating the migration with the application deploy that depends on it. Use before any schema change on a system that stays up, when adding or dropping a column on a large table, when a migration must be reversible, or when the deploy order between schema and application matters. Distinct from ordinary application change because the failure mode is a locked table, not a failed test.
---

# Database change management

Schema change against something that has to stay up.

## Why this exists

Schema change is treated as ordinary application change and behaves nothing like it. The failure modes are different, and none of them show up in a test suite.

The characteristic incident: a migration that took forty milliseconds on a developer's laptop and eleven minutes on a forty-million-row production table, holding a lock the whole time, while every request queued behind it. The migration was correct. The test passed. The site was down.

The second characteristic incident is ordering. The application deploys before the column exists, or the old code is still running when the column is dropped. Both are avoidable by construction, and both are common because the deploy pipeline treats schema and application as one step when they are two.

## When this applies

- Any schema change on a system that stays up
- Adding, dropping, or altering a column on a large table
- Adding an index, a constraint, or a foreign key to existing data
- A migration that must be reversible
- The order between schema and application deploy matters

## When it doesn't

- Greenfield with no data and no users
- A maintenance window is genuinely available and agreed — the constraint disappears, though reversibility still matters
- The change is to a small, low-traffic table and you've confirmed the row count

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/traces/data-model.md` or `data-archaeology` — you need to know the eras and the real shape
- `.fde/06-blast-radius-*.md` — ring 5 especially, who else reads this table
- Row counts and table sizes from the actual production database, not from staging. If you cannot get prod numbers, **stop** and put that in `00b-access.md`. Do not classify the lock from staging.

## Procedure

### 1. Get the real numbers first

Staging is not production, and the difference is the whole risk.

```sql
-- Adapt to the engine; the point is production row count and size
SELECT COUNT(*) FROM orders;
-- Postgres
SELECT pg_size_pretty(pg_total_relation_size('orders'));
-- Any engine: how busy is it?
```

Establish: row count, table size, index count, write rate, whether it's replicated, and whether long-running transactions or reporting queries touch it. A table read by a nightly batch has a window where a migration is far cheaper.

Twelve thousand rows and forty million rows are different problems requiring different techniques. Guessing which one you have is the mistake.

### 2. Classify the operation by what it locks

This determines everything. Behavior varies by engine and version, so **verify against your engine's documentation rather than assuming** — but the shape is consistent:

| Operation | Usually |
|---|---|
| Add nullable column, no default | Cheap — metadata only on modern engines |
| Add column **with a default** | Historically a full table rewrite; cheap on recent Postgres/MySQL. Version matters enormously. |
| Add index | Locks writes unless built concurrently (`CREATE INDEX CONCURRENTLY`, `ALGORITHM=INPLACE`) |
| Add NOT NULL to existing column | Full scan to validate |
| Add foreign key | Scan plus lock on both tables |
| Drop column | Usually cheap, but **irreversible** |
| Change column type | Usually a rewrite; frequently the most expensive operation there is |
| Rename | Cheap, and breaks every reader instantly |

Rename deserves its own warning: it is technically trivial and operationally severe, because it breaks all consumers at the moment it lands with no compatibility window. Use expand/contract instead.

### 3. Use expand and contract

The pattern that makes zero-downtime change possible. Never change a thing; add the new thing, migrate to it, then remove the old one — across **separate deploys**.

To rename `amount` to `amount_minor`:

1. **Expand** — add `amount_minor`, nullable. Old code unaffected.
2. **Dual-write** — deploy code writing both columns. Old code still works.
3. **Backfill** — populate `amount_minor` for existing rows, in batches (step 4).
4. **Migrate reads** — deploy code reading `amount_minor`. Both still written.
5. **Stop writing the old** — deploy.
6. **Contract** — drop `amount`, only after confirming nothing reads it.

Slow, and each step is independently safe and reversible. Step 6 often waits weeks, and that's correct — the cost of leaving a dead column is nearly zero, and the cost of dropping one something still reads is an outage.

**Every step must leave old and new code both working**, because during a rolling deploy both are running simultaneously. That constraint is what makes the pattern work, and violating it is the most common way a "zero-downtime" migration causes downtime.

### 4. Backfill in batches, never in one statement

A single `UPDATE` over forty million rows holds a lock, blows up the transaction log, and lags replicas.

Batch it: bounded chunks by primary key, a pause between batches, resumable from where it stopped, and monitored for replication lag. It should be safe to stop and restart at any point.

Watch replica lag specifically. A backfill that outruns replication makes read replicas stale, which breaks reporting and any read-your-writes assumption — usually presenting as a mysterious application bug rather than as a database problem.

### 5. Decide the deploy order explicitly

Write it down; it belongs in the runbook.

- **Additive schema first, then application.** The safe default: the column exists before code uses it.
- **Application first, then destructive schema.** Also safe: stop reading before dropping.
- **Never both in one step**, and never a destructive change in the same deploy as the code that stops using it.

The rolling-deploy constraint again: for a period, both versions run. Every ordering decision must hold under that.

### 6. Establish reversibility honestly

For each migration: can it be reversed, how long does that take, and what happens to rows written in the meantime?

- **Additive** — reversible. Dropping the added column loses only new data.
- **Backfill** — usually not reversible in any meaningful sense, but usually harmless to leave.
- **Destructive** — **not reversible.** "Restore from backup" is a plan only if someone has tested it and knows the RTO.

Where a migration is irreversible, it is a **one-way door** and must be marked as such in `deploy-runbook`. Everything before it should be verified before crossing.

### 7. Rehearse against production-shaped data

Run the migration against a copy with realistic volume and measure how long it takes. This is the only way to know, and it is exactly the discovery you want to make in advance.

Where no production-shaped copy exists, say so, and treat the timing as `[unverified]` in `release-readiness`. Do not extrapolate from staging — the relationship between a thousand rows and forty million is not linear in the way people assume.

## Output

Append to `.fde/runbooks/deploy-<change>.md`, and summarize in the change log:

```markdown
## Schema change — <description>

**Table:** `orders` · **Rows:** 40.2M · **Size:** 12 GB · **Replicated:** yes, 2 replicas
**Engine:** PostgreSQL 15 `[confirmed]`

### Steps
| # | Deploy | Operation | Expected duration | Lock | Reversible |
|---|---|---|---|---|---|
| 1 | schema | `ADD COLUMN currency varchar(3) NULL` | < 1s, metadata only | none | yes |
| 2 | app | dual-write currency | — | — | yes |
| 3 | data | backfill, 10k batches, 200ms pause | ~90 min, resumable | none | n/a |
| 4 | app | read from currency | — | — | yes |
| 5 | schema | *(deferred 30d)* drop legacy column | < 1s | brief ACCESS EXCLUSIVE | **NO — one-way door** |

### Rehearsal
Run against a 40M-row copy on <date>: step 3 took 94 min, peak replica lag 4s. ✅

### Monitoring during backfill
- Replica lag < 30s — abort and pause if exceeded
- Lock waits on `orders` — abort if any statement waits > 5s

### Rollback
Steps 1–4 reversible by reverting the deploy; the column can remain. Step 5 is irreversible
and is scheduled separately, after confirming no reader remains.
```

## Common traps

**Testing on a small table.** The relationship between a thousand rows and forty million is not what people assume.

**A single-statement backfill.** Lock, transaction log, replica lag, and no way to stop it.

**Ignoring replica lag.** Presents as a mysterious application bug, not a database problem.

**Renaming a column.** Trivial to write, breaks every consumer at once. Expand and contract instead.

**Schema and application in one deploy.** During a rolling deploy both versions run. Every step must work for both.

**Dropping a column in the same release that stops using it.** No compatibility window, no way back.

**Assuming a default value is cheap.** Version-dependent. Historically a full rewrite. Check your engine.

**"We'd restore from backup."** Only a plan if someone has tested it and knows the RTO.

**Not rehearsing at volume.** The duration is the risk, and it's knowable in advance.
