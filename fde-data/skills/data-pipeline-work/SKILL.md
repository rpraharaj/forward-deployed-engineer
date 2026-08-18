---
name: data-pipeline-work
description: Build or change ETL, ELT, warehouse, and reporting pipelines where the failure modes are silent - data quality decay, late-arriving and duplicate records, backfill and reprocessing, idempotency, lineage, and reconciliation against a source of truth. Use for analytics and reporting engagements, when a pipeline produces wrong numbers, when a job needs backfilling or reprocessing, or when a downstream report disagrees with the source system. Pipelines fail differently from services - they usually keep running and produce wrong answers.
---

# Data pipeline work

Where the failure mode is a wrong number, not an error.

## Why this exists

Analytics and reporting are roughly half of large-organization IT, and pipelines fail in a way services don't: **they keep running.** A service that breaks throws errors, pages someone, and gets fixed within the hour. A pipeline that breaks produces plausible numbers that are wrong, and nobody notices until month-end — or until a regulator asks, or until a decision has already been made on them.

That single difference drives everything here. In service work you optimize for fast detection of loud failures. In pipeline work you optimize for **detecting silence** — building the checks that turn a quiet wrong answer into a loud one.

The second thing that catches service engineers out: pipelines are re-run. Re-running a service request is an edge case; re-running a pipeline is Tuesday. Idempotency is not a nice property here, it is the baseline requirement.

## When this applies

- Analytics, ETL/ELT, warehouse, or reporting engagements
- A pipeline produces wrong or disputed numbers
- A job needs backfilling or reprocessing
- A report disagrees with the source system
- Adding a field that must flow through to reporting

## When it doesn't

- Transactional service work — different failure modes entirely
- You need to understand the schema first — that's `data-archaeology`
- Live production incident — `incident-triage`, then come back

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/traces/data-model.md` — the shape and eras of the source data
- `.fde/02-system-map.md` — where the pipeline sits
- Access to both source and destination, ideally, plus the orchestrator

## Procedure

### 1. Establish the lineage end to end

Before changing anything, know the full path: source system → extraction → transformations → destination → the report someone actually reads.

For each hop record what it does, what it filters, what it joins, what it aggregates, and **where the grain changes**. Grain changes — one row per order becoming one row per customer per day — are where numbers stop reconciling and where almost every disputed figure originates.

Name the **source of truth** explicitly. When a report and the operational system disagree, you need to have decided in advance which one is right.

### 2. Establish the semantics of the existing numbers

Before touching a pipeline that produces a figure someone uses, find out what that figure currently means. Not what it should mean — what it does.

Does "revenue" include tax? Refunds? Cancelled orders? In which currency, converted at which rate, on which date? Is it booking date or settlement date?

These are almost never documented, they are frequently inconsistent between reports, and changing one silently is how you break a business process. Where the current definition is wrong, that's a finding to raise — not to fix quietly.

### 3. Design for re-running

Assume every step runs more than once, because it will: backfills, late data, recovery from failure, a fixed bug.

- **Idempotent writes.** Re-running a step produces the same result, not duplicates. Usually means upsert on a natural key, or delete-then-insert of a bounded partition, rather than append.
- **Partitioned by time**, so a single day can be reprocessed without touching the rest.
- **Deterministic**, given the same input. Anything depending on wall-clock time at run time — `today()`, `now()` — makes re-runs produce different answers. Parameterize the date and pass it in.

That last point is the most common defect in enterprise pipelines and the reason backfills produce wrong numbers.

### 4. Handle late and duplicate data explicitly

Real source systems deliver late, deliver twice, and amend records after the fact.

- **Late arrivals** — a record for Monday arriving Wednesday. Does Monday's figure get corrected, or is it frozen? Both are valid; the pipeline must state which.
- **Duplicates** — at-least-once delivery is common. Deduplicate on a business key, not on arrival.
- **Amendments and deletes** — a cancelled order after the aggregate was computed. Does the source send a delete, a reversal, or silently drop the row? Each needs different handling, and "silently drop" is the dangerous one because it's undetectable downstream.

### 5. Build the reconciliation, not just the pipeline

The check that turns a silent failure into a loud one, and the single highest-value thing in this skill.

Compare the pipeline's output against the source of truth on a schedule: row counts by day, sums of the key measure, and distinct counts of the main entity. Alert on divergence beyond a stated tolerance.

Without reconciliation, a pipeline that silently drops 2% of records looks completely healthy. With it, you know within a day.

Also assert **within** the pipeline: row counts don't drop unexpectedly between stages, null rates stay within expected bounds, key columns stay unique where they should, and totals survive each transformation. Fail the run loudly rather than writing a plausible wrong answer.

### 6. Plan backfills as their own operation

A backfill is a production operation with the same discipline as a deploy — see `deploy-runbook`.

Establish: how far back, in what batch size, at what cost (warehouse compute is metered and backfills are expensive), how long it will take, whether it can run alongside the normal schedule or must be sequenced, and how you verify it worked.

**Verify a backfill by reconciliation, not by completion.** "The job finished" is not evidence; matching the source is.

### 7. Check who consumes the output

Dashboards, scheduled reports, downstream pipelines, extracts to partners, and models. Each is a consumer whose numbers change when yours do.

A changed definition — even a corrected one — will be noticed by someone whose figures moved. Tell them beforehand. A silently corrected number is indistinguishable from a new bug to the person reading it, and you will spend a week proving otherwise.

## Output

Write to `.fde/traces/pipeline-<name>.md`:

```markdown
# Pipeline — <name>

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Source of truth:** <system> · **Confidence:** <what's confirmed vs. inferred>

## Lineage
| # | Stage | Does | Grain | Idempotent | Confidence |
|---|---|---|---|---|---|
| 1 | Extract `orders` | CDC → landing | one per order | yes — upsert on `order_id` | confirmed |
| 2 | Transform | joins customer, converts currency | one per order | yes | confirmed |
| 3 | Aggregate | daily by region | **one per region per day** | yes — partition replace | confirmed |
| 4 | Report | finance dashboard | — | — | — |

## Semantics
| Measure | Definition as built | Documented? | Notes |
|---|---|---|---|
| `revenue` | Net of refunds, excl. tax, booking date, EUR @ daily close | **no** | Differs from the ops dashboard, which uses settlement date |

## Late, duplicate, amended
| Case | Current behavior | Correct? |
|---|---|---|
| Late arrival | Restates the affected day | yes |
| Duplicate delivery | Deduped on `order_id` | yes |
| Cancellation after aggregate | **Source silently drops the row** — aggregate not corrected | **no — defect** |

## Reconciliation
| Check | Against | Tolerance | Schedule | Alerts to |
|---|---|---|---|---|
| Daily row count | source `orders` | 0 | daily 06:00 | #data-oncall |
| Daily revenue sum | source | 0.01 | daily 06:00 | #data-oncall |

## Consumers
| Consumer | Owner | Notified of change |
|---|---|---|

## Backfill
**Range:** · **Batches:** · **Est. duration/cost:** · **Verification:** reconciliation over the range
```

## Common traps

**Treating pipeline failure like service failure.** Pipelines keep running and produce wrong answers. Build for detecting silence.

**Non-idempotent steps.** Re-running is routine, not exceptional.

**Wall-clock dependence.** `now()` inside a transformation makes backfills produce different answers than the original run.

**No reconciliation.** A pipeline silently dropping 2% looks perfectly healthy.

**Changing a measure's definition quietly.** Even a correction. Whoever reads it can't distinguish that from a new bug.

**Not establishing what the number currently means.** Almost never documented, frequently inconsistent, and load-bearing for someone's process.

**Missing the grain change.** Where numbers stop reconciling, and where nearly every dispute originates.

**Verifying a backfill by completion.** Finished is not correct. Reconcile.

**Ignoring silent source deletes.** Undetectable downstream, and they quietly corrupt every aggregate built on them.
