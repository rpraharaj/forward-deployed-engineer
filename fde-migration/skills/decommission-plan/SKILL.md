---
name: decommission-plan
description: Turn a system off safely - proving there are no remaining consumers, which is much harder than it sounds, then data retention and archival obligations, a staged darkening sequence, and how long to keep the ability to reverse. Use when a system is being retired, after a migration leaves the old system idle, when someone asks whether something can be switched off, or when a service appears unused. Consumer discovery is the whole job; the switching off is trivial by comparison.
---

# Decommission plan

Proving nothing needs it, then turning it off.

## Why this exists

Decommissioning is common, genuinely hard, and almost never planned properly. Systems get left running for years after their replacement ships because nobody was willing to say it was safe to stop them — which is a rational position, since the evidence to say so was never gathered.

The difficulty is entirely in one place: **proving there are no remaining consumers.** Turning something off takes a minute. Knowing you can is the work, and it's hard because absence of evidence is not evidence of absence. A quarterly report, an annual regulatory extract, or a partner integration used twice a year will not appear in a week of traffic logs.

The second reason this matters: leaving systems running has real costs — licences, infrastructure, patching obligations, audit scope, and the ongoing confusion of two systems where one is authoritative. Nobody attributes those costs to the decommission that didn't happen.

## When this applies

- A system is being retired
- After a migration leaves the old system idle
- "Can we switch this off?"
- A service appears unused
- Cost or audit-scope reduction

## When it doesn't

- The replacement isn't live and proven yet — finish `cutover-plan` first
- Deleting code rather than retiring a running system — that's `safe-change` plus `git-archaeology`
- You're being asked to prove something is unused with no authority to act — that's an assessment

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: use `FDE_WORKSPACE` if set (report an unavailable explicit path rather than falling back), otherwise the charter's recorded Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, run core `fde-orient`; do not create a second workspace. All artifact paths below use that location. Follow core workspace conventions for headers; preserve existing sections when appending.

- `<workspace>/02-system-map.md` and `<workspace>/02b-ownership.md`
- `<workspace>/runbooks/cutover-*.md` if this follows a migration
- Access to logs, monitoring, and network data covering **at least a full business cycle**

## Procedure

### 1. Establish what "off" means

Several distinct states, and conflating them causes most of the confusion:

| State | Meaning | Reversible |
|---|---|---|
| **Read-only** | Still serves reads, accepts no writes | Trivially |
| **Dark** | Running, no traffic routed | Trivially |
| **Stopped** | Not running, data intact | Minutes to hours |
| **Deprovisioned** | Infrastructure released, data archived | Days, if archived properly |
| **Deleted** | Data gone | **Never** |

Decommissioning is a **sequence through these**, not a single event. Each step is cheap to reverse until the last, and staging through them is what makes the whole thing safe.

### 2. Discover consumers by multiple independent methods

The core of the skill. **No single method is sufficient**, and using only one is how decommissions break things.

- **Traffic logs** — access logs, load balancer logs, API gateway metrics. Necessary, and blind to anything less frequent than your retention window.
- **Network connections** — who actually connects. Catches consumers that make no application-level requests.
- **Database sessions** — who queries the database directly. Reporting tools and ops scripts live here, and they appear in no application log.
- **Code search** — org-wide search for the hostname, service name, queue name, table name, or client library.
- **Configuration** — the URL or credentials appearing in other systems' config, which reveals consumers not currently active
- **Credentials and accounts** — service accounts and API keys issued for it. An issued, unrevoked credential is a consumer who might return.
- **Asking** — announce the intent to decommission widely, with a date. The most effective method by a distance, and the one that surfaces the annual regulatory extract.

That last one is worth emphasizing: a broad announcement with a deadline reliably produces consumers no technical method found. People respond when their thing is about to break.

### 3. Observe across a full business cycle

The trap that catches technically careful people.

Weekly, monthly, quarterly, and annual processes will not appear in a week of logs. A regulatory extract that runs each January, a quarterly board report, an annual audit pull — each is a consumer, each is invisible in short observation, and each is exactly the kind of thing whose failure is a serious incident.

**Observe for at least a full cycle**, and where you can't, say so explicitly and account for it in the darkening period. If the system has been running for years and you have four weeks of logs, your evidence covers four weeks.

### 4. Deal with data retention before turning anything off

Data usually outlives the system holding it, and the obligations are rarely the system owner's to waive.

Establish: what must be retained, for how long, under what obligation, and in what form. Retention is frequently a legal or regulatory requirement with a defined period — and it may require the data be *retrievable*, not merely stored, which is a much stronger requirement and changes the archive format.

Also ask who might need to *query* it. An archive nobody can read satisfies a retention clause and fails the actual need. Where the data will be needed for investigation, a queryable export beats a database dump.

**Archive and verify the archive before deprovisioning.** A backup nobody has restored is not an archive.

### 5. Darken in stages, with a wait at each

The sequence that makes this safe. Each stage is cheap to reverse, and the waiting is the point:

1. **Announce** — with a date, widely, to a list you've deliberately over-broadened
2. **Read-only** — stop accepting writes. Wait. Write failures surface consumers immediately and loudly.
3. **Dark** — stop routing traffic, keep it running. Wait. This is the highest-value stage: anything that breaks does so while recovery is instant.
4. **Stopped** — shut it down, data intact. Wait longer than you think.
5. **Archive and verify** — export, confirm the export is readable and complete
6. **Deprovision** — release infrastructure
7. **Delete** — only after the retention period, and only deliberately

Make the waits real. A week at "dark" catches weekly jobs; a full quarter catches quarterly ones. The tension between cost pressure and observation period is genuine — state it explicitly rather than quietly shortening the wait.

**Keep the ability to reverse for as long as it's cheap.** A stopped VM costs almost nothing; an unrecoverable deletion is unbounded risk. There is rarely a good reason to hurry past stage 4.

### 6. Instrument the darkening

Don't rely on someone complaining. Before darkening, ensure a failed access is *visible*: log rejected connections at read-only, alert on attempted access while dark.

A consumer that fails silently and retries — a batch job that logs an error nobody reads — will not complain until something else breaks weeks later, by which point the connection to your decommission is lost.

### 7. Record who agreed and when

Decommissioning is a decision with consequences, and one where "nobody objected" is doing a lot of work. Record who was notified, when, what they said, and who authorized each stage.

Not defensively — because when someone appears in month three saying they needed it, the useful question is which notification they missed and whether the list was wrong. That's a fixable process problem, and it's only answerable if you kept the record.

## Output

Write to `<workspace>/runbooks/decommission-<system>.md`:

```markdown
# Decommission — <system>

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Replaced by:** <system>, live since <date> · **Decision owner:** <name>
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Consumer discovery
| Method | Coverage | Found | Confidence |
|---|---|---|---|
| Access logs | 90 days | 3 internal services | confirmed |
| Network connections | 30 days | 3 services + 1 unknown host | **1 unresolved** |
| DB sessions | 30 days | 2 reporting tools | confirmed |
| Org code search | full | 4 references, 1 in a dormant repo | confirmed |
| Config search | full | credentials in 2 other systems | confirmed |
| Service accounts | full | 6 issued, 4 unused 12m+ | confirmed |
| **Announcement** | sent 03-01 to 40 people | **2 consumers nobody found** | — |

**Business cycle observed:** 90 days. **Annual processes NOT observed** `[unverified]` —
accounted for by a 12-month dark period before deprovisioning.

## Consumers found
| Consumer | Owner | Migrated? | Notes |
|---|---|---|---|
| `billing-web` | Team B | ✅ 03-10 | |
| Quarterly finance extract | Finance | ❌ **not migrated** | Surfaced by announcement only |
| Unknown host 10.x.x.x | ? | — | **unresolved — blocks darkening** |

## Retention
**Obligation:** 7 years, retrievable, per <policy> `[confirmed: Compliance, 03-12]`
**Form:** queryable export to <location>, not a raw dump — Finance may need to query it
**Archive verified:** <date> — restored and spot-checked ✅

## Sequence
| # | Stage | Date | Wait | Reversal | Gate |
|---|---|---|---|---|---|
| 1 | Announce | 03-01 | 4w | — | — |
| 2 | Read-only | 04-01 | 4w | instant | All known consumers migrated |
| 3 | Dark | 05-01 | **12m** | instant | No rejected access in 4w |
| 4 | Stopped | 06-01 | — | ~1h | No access attempts while dark |
| 5 | Archive + verify | 06-15 | — | — | Archive readable ✅ |
| 6 | Deprovision | 2027-05 | — | days | 12m dark, full annual cycle passed |
| 7 | Delete | 2033 | — | **never** | Retention expired |

## Instrumentation
- Rejected writes logged and alerting to <channel> from stage 2
- Any connection attempt while dark alerts <name> from stage 3

## Notification record
| Date | Who | Response |
|---|---|---|
```

## Common traps

**One discovery method.** Each is blind to something. Use all of them.

**Observing for a week.** Misses monthly, quarterly, and annual consumers — the ones whose failure is most serious.

**Treating silence as absence.** A batch job that logs an error nobody reads will not complain.

**Not instrumenting the darkening.** You find out from a downstream incident weeks later, with the connection lost.

**Skipping the dark stage.** The highest-value stage — breakage happens while recovery is instant.

**Archiving without verifying.** A backup nobody has restored is not an archive.

**Storing rather than making retrievable.** Satisfies the clause, fails the need.

**Hurrying past "stopped."** A stopped VM costs almost nothing. Deletion is unbounded risk.

**Not recording notifications.** When someone surfaces in month three, you need to know which list was wrong.
