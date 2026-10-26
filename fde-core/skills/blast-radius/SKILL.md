---
name: blast-radius
description: Map everything a proposed change could break before making it - direct callers, cross-repository consumers, published contracts, event subscribers, feature flags, shared database objects, and config coupling - ending with a risk rating and the specific things to verify. Use before any non-trivial change, when asked "what breaks if we touch this", before modifying anything shared or published, or before a schema change. Do not use for a release go/no-go - that is release-readiness; this skill supplies the consumer list.
---

# Blast radius

Establishing what a change can break, before it breaks it.

## Why this exists

The changes that cause incidents are almost never the ones that looked dangerous. They're the one-line additions to a shared DTO, the extra field in a response, the "obviously safe" nullable column. They cause incidents because the danger wasn't in the change — it was in the twenty-three things that depended on the thing being changed, and nobody enumerated them.

An FDE is unusually exposed here. An engineer who has worked on a system for five years carries an approximate blast radius in their head and will flinch at the right moments. You have no such instinct, and you cannot acquire one in time. Enumeration is the substitute, and done properly it is *better* than instinct — it produces a list somebody else can check.

## When this applies

- Before any change beyond a genuinely local one
- Modifying anything shared, published, or widely called
- Any schema change
- "What breaks if we touch this?"
- Feeding `release-readiness` — this skill is the consumer list, not the go/no-go

## When it doesn't

- Genuinely local change: private method, one caller, well covered by tests
- Net-new code nothing calls yet
- You need to know how something works rather than what depends on it — that's `trace-the-flow`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/02-system-map.md` — integration surface and module boundaries
- `<workspace>/04-feasibility.md` — the change sites you're assessing
- A trace helps where the change is on a request path, but isn't required

## Procedure

Work outward. Each ring is harder to see than the last, and the outer rings are where incidents come from.

### Ring 1 — Direct callers, in this repository

```bash
# Count before reading — see context-strategy
grep -rl "<SymbolName>" --include="*.<ext>" . | wc -l
grep -rn "<SymbolName>" --include="*.<ext>" . | head -40
```

Where the count is large, that is itself the finding: a symbol with sixty callers is not a local change regardless of how small the diff is. **Stop reading ring-1 hits after about forty.** Record the count, sample the rest, and move out — rings 3–6 are where incidents come from.

**Grep is necessary and not sufficient.** It cannot see dynamic dispatch, reflection, config-driven wiring, or string-built queries. Where the codebase uses those — see `../trace-the-flow/references/following-indirection.md` — any "nothing else calls this" conclusion is `[inferred]`, and must be labelled that way. Say what you searched and what the search can't see.

### Ring 2 — Interface and type ripple

Changing a shared type propagates further than changing a method. Follow the type through DTOs, mappers, serializers, interfaces it implements, and the tests that construct it.

Look specifically for **serialization surfaces**. A field added to a type that gets serialized may appear in an API response, a cached value, a persisted document, an event payload, or a log — several of which have consumers you don't control.

### Ring 3 — Published contracts

The most commonly missed ring, and the most expensive.

```bash
find . -name "*.proto" -o -name "openapi*.y*ml" -o -name "swagger*.json" -o -name "*.wsdl" -o -name "*.avsc" -o -name "*.graphql" | head -20
```

For each contract the change touches, establish:

- **Who consumes it** — other services, other teams, external partners, mobile clients you cannot force to upgrade
- **Is the change compatible** — additive optional fields usually are; removals, renames, type changes, and required additions are not
- **Is there a version strategy** already in place, and does this change need a new version
- **Can consumers be coordinated**, or must this be backward-compatible indefinitely

Mobile and external partners deserve separate thought. You cannot deploy a fix to an app on someone's phone, and "backward compatible for two years" is a materially different design constraint from "compatible until Tuesday."

### Ring 4 — Cross-repository consumers

The ring an FDE is worst equipped to see, because you may not have the other repositories.

Approaches, cheapest first:

- Search an org-wide code search if one exists
- Check the service catalogue or dependency graph, if the organization maintains one
- If this repo publishes a library, find who depends on that artifact — the registry may report downstream usage
- Grep the local package cache for consumers you have on disk
- Ask. `ownership-map` tells you whom, and this is a good use of a `knowledge-interview` slot

Where you cannot establish this ring, **say so explicitly and prominently**. "No cross-repo consumers found" and "I could not check for cross-repo consumers" are completely different statements, and conflating them is how contract breaks reach production.

### Ring 5 — Data and shared state

Database objects are frequently shared with systems nobody remembers.

- Is the table, view, or column read by anything other than this application — a report, an ETL job, a warehouse sync, a partner extract, an ops query?
- Are there triggers, materialized views, or downstream replicas?
- Does anything parse the data positionally, or by column order?
- Is the table large enough that a migration takes a lock that matters? See `db-change-management` *(fde-data)*.

Reporting and analytics consumers are the classic blind spot: they read the production schema directly, they're owned by a different team, and they discover breakage a day later in a dashboard.

### Ring 6 — Behavioral and operational coupling

Not everything that breaks is a compile error.

- **Timing** — does anything depend on how long this takes, or on ordering?
- **Volume** — does the change alter how many rows, calls, or messages are produced?
- **Idempotency** — if retried, does the new behavior stay safe?
- **Feature flags** — does this interact with an existing flag, and is any combination untested?
- **Monitoring** — do alerts or dashboards depend on a log line or metric this changes? Renaming a log field silently breaks alerting, and nobody finds out until the alert fails to fire.
- **Config** — is there configuration that must change in lockstep, in environments you can't reach?

### 7. Rate the risk and name the verification

Combine **reach** (how many things are affected) with **detectability** (how fast you'd know) with **reversibility** (how easily undone).

| Rating | Means |
|---|---|
| **Low** | Local, well covered, quickly reversible |
| **Medium** | Multiple internal consumers, all identified and testable |
| **High** | Published contract, cross-team consumers, or shared data |
| **Critical** | External or uncoordinatable consumers, irreversible data change, or unidentified consumers |

**Unknown consumers means Critical, not Low.** Absence of evidence is not evidence of absence, and this is the single most important judgment in the skill.

Then — the part that makes the artifact actionable — list the **specific things to verify** for each ring. That list flows directly into `verification-plan` and `release-readiness`.

**Stop** when every ring has a row, including `not checked` / `[unverified]`, and the verification list is written. Unknown consumers stay Critical. See `db-change-management` *(fde-data)* for ring 5 lock behavior if that pack is installed.

## Output template

Write to `<workspace>/06-blast-radius-<change>.md`:

```markdown
# Blast radius — <change>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** <which rings you could actually check>

## The change
<What is changing, precisely. File and symbol level.>

## Rating: **<Low | Medium | High | Critical>**
<One paragraph: what drives the rating, and what would lower it.>

## Rings

| Ring | Found | Confidence | Notes |
|---|---|---|---|
| 1 Direct callers | 12 in-repo | confirmed | `grep -rl` → 12 files |
| 2 Type ripple | 4 DTOs, 2 mappers | confirmed | |
| 3 Published contracts | `openapi.yml` — `RefundResponse` | confirmed | Additive optional field |
| 4 Cross-repo consumers | **not checked** | **unverified** | No org code search; access requested |
| 5 Data | `refunds` table, 40M rows | confirmed | Also read by nightly warehouse sync |
| 6 Operational | metric `refund.processed` unchanged | confirmed | |

## Consumers
| Consumer | Type | Owner | Impact | Coordinated? |
|---|---|---|---|---|
| `billing-web` | internal service | Team B | Additive, no action | notified 03-12 |
| Partner extract | external | Data team | Reads `refunds` directly | **not yet contacted** |

## What must be verified
| # | Ring | Verification | How |
|---|---|---|---|
| 1 | 1 | 12 callers compile and pass | full suite |
| 2 | 3 | Contract change is additive | schema diff against published spec |
| 3 | 5 | Warehouse sync tolerates the new column | ask data team / test in staging |

## Unknowns
| # | Unknown | Why it matters | To resolve |
|---|---|---|---|
| 1 | Cross-repo consumers of `RefundResponse` | Could break an unknown service | Org code search — needs access |

## Mitigations
<Feature flag, versioning, staged rollout, backward-compatible shim, advance notice to consumers.>
```

## Common traps

**Treating grep as complete.** It cannot see reflection, DI, config wiring, or string-built SQL. Label the conclusion `[inferred]` and say what you couldn't search.

**"No consumers found" when you mean "I couldn't look."** The most dangerous sentence in the artifact.

**Rating unknown-consumer changes as Low.** Unknown reach is Critical until established.

**Stopping at ring 1.** Direct callers are the easy ring and rarely where incidents come from.

**Forgetting the analytics and reporting consumers.** They read production schemas directly, they're owned elsewhere, and they break silently.

**Ignoring operational coupling.** Renaming a log field breaks alerting invisibly, and you find out when the alert doesn't fire.

**Assuming additive is always safe.** It usually is — but not against positional parsers, strict schema validators, or consumers that reject unknown fields.

**Producing a rating without a verification list.** The rating informs a decision; the list is what someone actually does.
