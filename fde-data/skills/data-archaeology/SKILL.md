---
name: data-archaeology
description: Reconstruct an undocumented data model from whatever exists - migrations, DDL, ORM definitions, and most reliably the queries actually issued - then surface the gap between the schema's stated intent and its real use. Use when a schema is undocumented, when the domain model is unclear, before a migration or reporting change, when column names do not match their contents, or when you need to know what the data actually looks like rather than what the schema claims. The schema tells you what is allowed; the data tells you what happens.
---

# Data archaeology

Working out what the data actually means.

## Why this exists

In a system of any age the schema is an unreliable narrator. Columns are nullable that are never null, and non-nullable columns hold empty strings meaning "unknown." Enums contain values the code stopped writing four years ago. A column named `status` holds three different vocabularies depending on when the row was created. Foreign keys are declared in some places and merely implied in others.

None of this is in the documentation, because there isn't any. It is discoverable from two sources: the **queries the code actually issues**, which reveal intended meaning, and the **data itself**, which reveals what happened.

The gap between them is where migrations fail and reports go quietly wrong.

## When this applies

- Undocumented schema or unclear domain model
- Before a migration, a reporting change, or a schema change
- Column names that don't match their contents
- You need to know what the data looks like, not what the schema permits
- Before `data-pipeline-work` or `db-change-management`

## When it doesn't

- Well-documented schema with a maintained model
- You need control flow rather than data — that's `trace-the-flow`
- You need current row-level values for testing — that's `test-data-strategy`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: use `FDE_WORKSPACE` if set (report an unavailable explicit path rather than falling back), otherwise the charter's recorded Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, run core `fde-orient`; do not create a second workspace. All artifact paths below use that location. Follow core workspace conventions for headers; preserve existing sections when appending.

- `<workspace>/02-system-map.md` — where data lives
- Read access to a database, ideally. Where you have none, this skill still works from migrations and code, at reduced confidence — say so.
- Understand the organization's data policy before running aggregates. Shape queries live in core `test-data-strategy` step 2 — run those, do not paste a second dialect-specific copy.

## Procedure

### 1. Reconstruct the declared schema

```bash
# Migrations, in order, are the schema's history
find . \( -path "*migration*" -o -path "*/db/*" \) -name "*.sql" | sort | tail -40
# ORM / schema declarations — bind EXT from the language mix, do not assume one framework
grep -rn "CREATE TABLE\|Schema(\|DbSet\|entity-name" --include="*.$EXT" --include="*.sql" --include="*.xml" . | head -30
```

Read migrations **in order**, not just the current state. The sequence tells you what changed and roughly when, which is the closest thing to a changelog the data model has. A column added and then made nullable three migrations later usually marks a failed assumption worth knowing about.

### 2. Find what the code actually queries

More informative than the schema, because it reveals intended meaning.

```bash
grep -rn "SELECT\|INSERT INTO\|UPDATE .* SET" --include="*.*" . | head -40
grep -rn "findBy\|where(\|filter(\|\.query(" --include="*.*" . | head -40
```

You're looking for: which columns are actually used (many won't be), which combinations are filtered together (that's a real relationship, declared or not), and which values are compared against literals — those literals are the live enum, whatever the schema says.

### 3. Ask the data what's true

The highest-value step, and it needs only aggregate queries — usually permitted where row access isn't. **Run the shape queries in core `test-data-strategy` step 2** (ANSI `SUM(CASE)` form). Add only what that set does not cover:

```sql
-- Implied foreign keys: does every child actually have a parent?
SELECT COUNT(*) FROM orders o
LEFT JOIN customers c ON o.customer_id = c.id WHERE c.id IS NULL;

-- When each enum value was live — maps onto undocumented eras
SELECT status, COUNT(*), MIN(created_at), MAX(created_at)
FROM orders GROUP BY status ORDER BY 2 DESC;
```

`MIN`/`MAX` of `created_at` per enum value is the single most informative query here. It tells you *when* each value was in use, which usually maps directly onto a system era nobody documented.

### 4. Find the eras

Mature tables have generations. Rows written before a migration, before a vendor change, before the current code. They differ in shape, and the differences are invisible until something processes all of them.

Look for: date ranges where a column is always null and then never is; format changes in text columns; ID schemes that change partway; enum values that stop or start.

Every era is a case your change must handle, and the reason `test-data-strategy` insists on legacy-shaped fixtures.

### 5. Distinguish declared from actual relationships

Foreign keys are frequently absent in enterprise schemas — dropped for performance, or never added. The relationship still exists; it's just unenforced, which means it's also **sometimes violated**.

For each implied relationship, check for orphans (query above). Orphaned rows are not an anomaly to be cleaned up on sight — they usually mean something, and `git-archaeology` on the code that created them is the way to find out what.

### 6. Note who else reads this

A schema is an interface. Reporting tools, ETL jobs, warehouse syncs, partner extracts, and ops queries read production tables directly, and their owners are usually a different team who will find out about your change a day later, in a dashboard.

This flows straight into `blast-radius` ring 5. Where you can't establish the consumers, say so — it's the most common source of a silent break.

**Stop** when you can name grain, live vocabulary, eras, undeclared relationships, and other readers for the tables in scope — or each of those is `[unverified]`. Do not model the warehouse.

## Output

Write to `<workspace>/traces/data-model.md`:

```markdown
# Data model — <area>

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<SHA> · **Data observed:** <environment>, <date>
**Confidence:** <schema read vs. data queried vs. inferred>

## Entities
| Table | Rows | Grain | Purpose | Confidence |
|---|---|---|---|---|
| `orders` | 40M | one per customer order | | confirmed |

## Column reality
| Column | Declared | Actually | Note |
|---|---|---|---|
| `postcode` | NOT NULL | 3.2% empty string used as "unknown" | Not null-checked in code |
| `status` | varchar(20) | 7 live values, 2 legacy | See eras |

## Live vocabulary
| Value | Count | First seen | Last seen | Still written? |
|---|---|---|---|---|
| `SETTLED` | 31M | 2019-04 | today | yes |
| `PENDING_V1` | 240k | 2017-01 | 2019-03 | **no — legacy** |

## Eras
| Era | Dates | What differs | Must handle |
|---|---|---|---|
| Pre-migration | < 2019-04 | No `currency`; status vocabulary v1 | Yes — 240k rows |

## Relationships
| From | To | Declared FK | Orphans | Note |
|---|---|---|---|---|
| `orders.customer_id` | `customers.id` | **no** | 1,412 | Pre-2019, customer purge |

## Other readers
| Consumer | Reads | Owner | Confirmed |
|---|---|---|---|
| Warehouse sync | `orders`, `refunds` | Data team | `[unverified]` |

## Gaps
<What you couldn't establish and what would resolve it.>
```

## Common traps

**Trusting the schema.** It says what's allowed, not what's there.

**Reading only the current schema, not the migration sequence.** The sequence is the closest thing to a changelog.

**Not querying the data.** Aggregates are usually permitted and are the highest-value step by a distance.

**Missing the eras.** Every generation of rows is a case your change must handle, and they're invisible until something processes all of them.

**Assuming no foreign key means no relationship.** It means an unenforced one, which is sometimes violated.

**Cleaning up orphans on sight.** They usually mean something. Find out what first.

**Forgetting the schema is an interface.** Reporting and ETL consumers read it directly and break silently.

**Treating a null and an empty string as the same thing.** In old schemas they frequently carry different meanings, assigned by different eras of code.
