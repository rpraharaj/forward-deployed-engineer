---
name: test-data-strategy
description: Get realistic test data in an organization where production data cannot be copied - synthesis, subsetting, masking with referential integrity preserved, and fixtures for the awkward edge cases that only real systems produce. Use when tests need data you do not have, when verification is blocked because no usable dataset exists, when someone suggests copying production data, when a staging environment is empty or unrealistic, or when a bug only reproduces against real-shaped data. In regulated organizations this is frequently the actual bottleneck to shipping, not the code.
---

# Test data strategy

Getting data you're allowed to have that behaves like data you aren't.

## Why this exists

In a regulated organization, production data cannot be copied into a test environment. Not "shouldn't" — cannot, without a legal basis, and often not even then. GDPR, PCI-DSS, HIPAA, and internal data policies all land in the same place: the realistic data you need to verify anything is the data you are least allowed to touch.

The result is a specific and very common failure. Tests run against three hand-written rows containing "Test User" and "123 Test Street." They pass. The change ships. It breaks immediately on a customer whose name contains an apostrophe, an address with no postcode, an order placed before the 2019 migration, or an account with forty thousand transactions.

The data wasn't wrong. It was *unrepresentative*, which is harder to notice.

This is frequently the real bottleneck to shipping in an enterprise — not the code, and not the tests, but having anything sensible to run them against.

## When this applies

- Tests need data you don't have
- Verification blocked by an empty or unrealistic environment
- Someone proposes copying production data
- A bug reproduces in production and not locally
- Performance work needing realistic volume

## When it doesn't

- Adequate fixtures already exist — check they're representative, then use them
- Pure unit tests over in-memory logic with no data shape dependency
- The blocker is access to an environment rather than data — that's `access-and-onboarding`

## Prerequisites

- `.fde/03-requirements.md` — the criteria determine what data must exist
- `.fde/02-system-map.md` — where data lives and what shape it takes
- Understand the organization's data policy before starting. See `../_shared/enterprise-constraints.md`.

## Procedure

### 1. Establish what's actually permitted

Ask before designing anything, because the answer determines the whole approach and people's assumptions about it are usually wrong in both directions.

- Can production data be used in a lower environment, under any conditions?
- Is there an approved masking or anonymization pipeline already?
- Is there a pre-approved synthetic dataset?
- What data classifications apply — is *anything* here personal, financial, or health data?
- Who approves an exception, and how long does it take?

Where a masking pipeline already exists, use it. Building a parallel one because you didn't ask is a real and avoidable mistake.

**Never copy production data as an interim measure "just to unblock myself."** It's the one shortcut in this portfolio that can end an engagement, and it is not recoverable by apologizing.

### 2. Understand the shape before generating anything

The failure mode of synthetic data is that it's too clean. To generate data that exercises the code, you need to know what real data actually looks like — which you can learn *without seeing any of it*.

Query for shape, never content:

```sql
-- Distributions and boundaries, no personal data returned
SELECT COUNT(*), COUNT(DISTINCT customer_id),
       MIN(created_at), MAX(created_at),
       AVG(LENGTH(name)), MAX(LENGTH(name))
FROM orders;

-- Null rates reveal which "required" fields are really optional
SELECT COUNT(*) FILTER (WHERE postcode IS NULL) * 100.0 / COUNT(*) AS pct_null_postcode
FROM addresses;

-- Categorical spread, including the values nobody documented
SELECT status, COUNT(*) FROM orders GROUP BY status ORDER BY 2 DESC;

-- Cardinality per parent — the distribution that breaks pagination and N+1 assumptions
SELECT n_orders, COUNT(*) FROM (
  SELECT customer_id, COUNT(*) AS n_orders FROM orders GROUP BY customer_id
) t GROUP BY n_orders ORDER BY 1 DESC LIMIT 20;
```

Aggregate queries are usually permitted where row access isn't, and they tell you what matters: null rates, value distributions, the long tail, the enum values still in the data that the code no longer produces.

That last one is a reliable source of production bugs. A `status` column with a value the current code can't handle, left over from a system three migrations ago, exists in most mature databases.

### 3. Choose an approach

| Approach | Use when | Cost | Realism |
|---|---|---|---|
| **Hand-written fixtures** | Specific scenarios, unit tests | Low | Low — only what you thought of |
| **Generated synthetic** | Volume, distributions, most integration tests | Medium | Medium — as good as your shape analysis |
| **Masked production subset** | High realism needed and a pipeline exists | High | High |
| **Recorded production traffic** | Characterizing existing behavior | Medium | High — real shapes, redact before storing |
| **Shared seeded environment** | Team already has one | Low to use | Varies |

Most engagements need two: generated data for volume and distribution, hand-written fixtures for the specific awkward cases. They answer different questions and neither substitutes for the other.

### 4. Preserve referential integrity

The most common failure in generated data, and the one that produces the most confusing bugs. An order referencing a customer that doesn't exist doesn't test anything real — it tests your generator.

Generate in dependency order, carrying real keys forward. Preserve:

- Foreign keys that actually resolve
- Realistic **cardinality** — most customers have one or two orders; one has four thousand, and that one finds your pagination bug
- Temporal consistency — a shipment cannot precede its order
- State-machine validity — a `REFUNDED` order needs a payment to have existed
- Uniqueness where the schema enforces it, and near-collisions where it doesn't

### 5. Deliberately include the awkward cases

This is where the value is. Synthetic data is uniformly well-behaved unless you make it otherwise, and uniform data tests nothing interesting.

Build in, explicitly:

- **Unicode and diacritics** in names and addresses — and emoji, which some pipelines still cannot handle
- **Apostrophes and hyphens** — `O'Brien`, `Smith-Jones`. The classic, still breaking things.
- **Empty vs. null vs. whitespace** — three different states, frequently conflated
- **Boundary values** — zero, negative, maximum precision, the largest value the column allows
- **Legacy shapes** — records predating a migration, in the old format
- **Dead enum values** the code no longer writes but the data still contains
- **Extreme cardinality** — the customer with four thousand orders
- **Timezone edge cases** — DST transitions, and dates near midnight UTC
- **Long values** at the column maximum

Each of these corresponds to a real production incident somewhere. They're cheap to include and they're the reason to build the dataset rather than hand-write six rows.

### 6. Make it reproducible and version it

Test data that can't be regenerated identically produces flaky tests and unreproducible bugs.

- **Seed the generator.** A fixed seed means the same dataset every time, and a bug found on Tuesday reproduces on Thursday.
- **Commit the generator, not the data** — unless the dataset is small. A generator script is reviewable, diffable, and doesn't bloat the repository.
- **Version it alongside the schema.** A migration that changes the schema must change the generator, or the data silently stops being valid.

### 7. Document what it does and doesn't represent

The dataset's limitations are part of the verification story. If your data has no records predating the 2019 migration, then "the migration path is verified" is false, and `verification-plan` needs to know.

State the coverage explicitly, so a later reader doesn't over-trust a green test run.

## Output template

Write to `.fde/03c-test-data.md`:

```markdown
# Test data strategy

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Confidence:** <how well this represents production>

## Policy position
**Production data in lower environments:** not permitted `[confirmed: per data policy, J. Okafor 03-14]`
**Existing masking pipeline:** none
**Approved synthetic dataset:** none

## Approach
<Which of the five, and why. Usually two in combination.>

## Shape analysis
| Aspect | Production | Source |
|---|---|---|
| `orders` row count | ~40M | `SELECT COUNT(*)` |
| Orders per customer | median 2, p99 340, max 4,112 | aggregate query |
| `postcode` null rate | 3.2% | aggregate query |
| `status` values | 7 active, **2 legacy still present** | `GROUP BY status` |

## Generated dataset
**Generator:** `tools/gen-testdata.<ext>` · **Seed:** `20260326` · **Volume:** 5,000 customers / 12,000 orders

**Deliberate edge cases:**
| Case | Why | Count |
|---|---|---|
| Apostrophe in name | Historic escaping bugs | 50 |
| Null postcode | 3.2% in production | 160 |
| Pre-migration format | Migration path coverage | 200 |
| Legacy `status` values | Still present in prod | 40 |
| Extreme cardinality customer | Pagination / N+1 | 1 @ 4,000 orders |
| Unicode + emoji | Encoding path | 30 |

## What this does NOT represent
<The honest limits. Feeds the gap list in `07-verification.md`.>
- No data older than 2019 — pre-migration path is **not** covered by this dataset
- Volume is 5k customers vs 40M production — not suitable for performance verification
- No multi-currency records — added in a later phase

## Refresh
<How to regenerate, and when it must be updated — e.g. on any schema migration.>
```

## Common traps

**Copying production data to unblock yourself.** The one shortcut that can end an engagement.

**Data that's too clean.** Uniformly well-behaved synthetic data passes tests that real data fails. The awkward cases are the point.

**Broken referential integrity.** Tests your generator, not the system.

**Uniform cardinality.** Every customer with exactly three orders never finds the pagination bug. Real distributions are long-tailed.

**Unseeded generation.** Flaky tests and bugs that won't reproduce.

**Committing a large dataset instead of the generator.** Unreviewable, and it rots against the schema.

**Not updating it with migrations.** The data silently stops being valid and the tests silently stop meaning anything.

**Overstating coverage.** If there's no pre-migration data, the migration path isn't verified. Say so — `verification-plan` needs it in the gap list.

**Building a masking pipeline that already exists.** Ask first.
