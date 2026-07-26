---
name: repo-recon
description: Build a breadth-first map of an unfamiliar codebase in a bounded amount of time - entry points, module boundaries, persistence and integration surface, churn hotspots, test topology, config surface, and landmines - then write it up as a durable system map plus a working CLAUDE.md. Use when dropped into a codebase you do not know, when asked "help me understand this repo", when you need to know where a change would land before committing to anything, or when inheriting a system whose original authors have left. Deliberately maps the territory rather than exploring any one region deeply. Run before feasibility-probe, trace-the-flow, or any change.
---

# Repo recon

The first structured pass over an unfamiliar system.

## Why this exists

Dropped into a large codebase, the natural instinct is to start reading something. It feels productive and it isn't: after two hours you know one component deeply, have no idea whether it matters, and can't answer the questions people are about to ask you.

This skill trades depth for coverage on purpose. Its job is to make you able to say *where things are* and *what you'd be scared to touch* — the two things that make every subsequent decision cheaper. Depth comes later, from `trace-the-flow`, and only where the work actually lands.

The other job is durability. A map that exists only in this session's context is worthless in week three.

## When this applies

- Any unfamiliar codebase you'll work in for more than a day
- Before estimating, designing, or changing anything
- Inheriting a system whose authors have left
- Someone asks what a repository does and you don't know

## When it doesn't

- You already know the system — read `CLAUDE.md` and go
- You need one specific fact — grep for it
- The repository is small enough to read outright (under ~500 files)
- You need deep behavior of a single flow — that's `trace-the-flow`

## Prerequisites

- `.fde/00-engagement.md` — scopes what you're looking for
- `.fde/01-environment.md` *(optional)* — if `env-bootstrap` already ran, you know it builds
- Read `../_shared/stack-detection.md` before step 2
- On anything over ~5,000 files, apply `context-strategy` first and set a budget

## Procedure

Ordered cheapest to most expensive. Each step should sharpen where the next one looks. **Read the stopping test in step 10 before you start** — it's what stops this becoming a week.

### 1. Shape

```bash
git ls-files | wc -l
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
ls -a
find . -maxdepth 2 -type d -not -path "*/.git*" -not -path "*/node_modules*" | sort
git log -1 --format="%ad %an" --date=short
git log --oneline --since="6 months ago" | wc -l
```

You're establishing: how big, what languages, is it alive, is it one system or several. A repository with three commits in six months and a top language you didn't expect is telling you something before you read a line.

### 2. Stack

Follow `../_shared/stack-detection.md`. Record every stack present with its root, and state which one you're scoping to. In enterprise repositories, several is the norm, not the exception.

Read the CI configuration properly at this point. It is the single most informative file for an arriving engineer: the real build and test commands, the pinned versions, the service dependencies, and the deploy path.

### 3. Entry points

How does anything get *into* this system? Everything else hangs off the answer.

**Read `references/entry-points-by-stack.md` before searching.** Two checks in that reference come *before* any language-specific pattern, and skipping either produces a confidently wrong map:

- **Are the entry points in the code at all?** In config-driven enterprise platforms they are declared in XML, YAML, or database tables, and every code search returns near-zero while the system has thousands of routes. The file-extension counts from step 1 are the tell: config files rivalling source files means config-driven.
- **Does this codebase use its framework's vocabulary?** Mature systems wrap framework primitives in house abstractions, so the canonical interface name returns nothing.

Then use the section matching what step 2 detected. Do not run patterns for a stack you didn't detect — "few hits" reads as "few entry points" rather than "wrong search," and that failure is silent.

Before searching, establish the **deployment shape** — service, CLI, library, batch, event consumer, serverless. Entry points differ more by shape than by language, and most real systems are two or three shapes at once. A CLI tool has no HTTP routes, and concluding it has no entry points because you searched for routes is a mistake you won't notice.

Then run the stack-independent sweep from the same reference — scheduled work in config, container entrypoints, k8s jobs, CI-invoked scripts. **Non-obvious entry points are where surprises live.** A nightly job or queue consumer nobody mentioned is exactly what breaks when you change a shared component.

Sanity-check the result against the repository's own shape. If a 1,300-file codebase appears to have two entry points, you searched wrong — say so and re-search rather than recording the number.

### 4. Boundaries and layering

Which modules exist, and which direction do dependencies run?

```bash
# Top-level packages
find src -maxdepth 3 -type d | sort

# Where imports cross module boundaries
grep -rhoE "^import com\.acme\.[a-z]+" --include="*.java" src/ | sort | uniq -c | sort -rn | head -30
```

You're looking for the intended architecture and where reality departs from it. A "domain" package importing from "web" is a finding worth recording — it constrains what can be changed independently, and it usually explains a lot about why the tests are slow.

### 5. Persistence and integration surface

What does this system store, and what does it talk to? This is the highest-value step for blast-radius work later.

```bash
# Schema
find . -path "*migration*" -o -name "*.sql" -o -name "schema*" | head -30
grep -rn "@Entity\|@Table\|CREATE TABLE" --include="*.java" --include="*.sql" . | head -40

# Outbound calls and external hosts
grep -rnE "https?://[a-zA-Z0-9.-]+" --include="*.yml" --include="*.yaml" --include="*.properties" . \
  | grep -v "schema\|xmlns\|w3.org\|localhost" | head -30

# Messaging
grep -rn "topic\|queue\|exchange\|@KafkaListener\|SQS\|ServiceBus" --include="*.yml" --include="*.java" . | head -30
```

`docker-compose.yml`, if present, usually names every database, cache, broker, and stubbed downstream in one file. Read it — it's often the fastest dependency map available.

### 6. Churn — where the risk concentrates

```bash
git log --format= --name-only --no-renames --since="12 months ago" 2>/dev/null \
  | grep -v '^$' \
  | grep -vE "(^|/)(CHANGELOG|Cargo\.lock|package-lock\.json|pnpm-lock\.yaml|yarn\.lock|go\.sum|poetry\.lock|Gemfile\.lock)" \
  | grep -vE "(^|/)(Cargo|pom|package|build\.gradle)" \
  | sort | uniq -c | sort -rn | head -25
```

**Filter the noise or the signal disappears.** Manifests, lockfiles, and changelogs top the churn list in almost every repository — they change on every release and tell you nothing about where the logic moves. Unfiltered, they occupy the first several rows and the actual hotspots start below the fold.

`--no-renames` avoids a rename-detection warning and a long pause on large histories.

If the clone is shallow (`git rev-parse --is-shallow-repository` returns true), churn analysis is meaningless — say so and tag any churn claim `[unverified]` rather than reporting numbers from a truncated history.

High-churn files are where the business is changing, where bugs cluster, and where your change is most likely to conflict. They deserve attention out of proportion to their size.

Then the inverse — files untouched for years. Some are stable and fine; some are load-bearing code nobody understands any more. Both matter, for opposite reasons.

### 7. Test topology

Counting files under `test/` directories works for languages that separate tests, and badly misleads for languages that don't. Check both:

```bash
# Separate-directory convention (JVM, .NET, JS, Ruby)
find . -path "*test*" -name "*.*" -not -path "*/node_modules/*" -not -path "./.git/*" \
  | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -15

# Inline convention (Rust, Go, Python doctests) — count files containing tests, not files in test dirs
grep -rl "#\[test\]\|#\[tokio::test\]" --include="*.rs" . 2>/dev/null | wc -l
grep -rl "func Test" --include="*_test.go" . 2>/dev/null | wc -l
grep -rl "def test_\|class Test" --include="*.py" . 2>/dev/null | wc -l
```

**Watch for fixture directories masquerading as tests.** Snapshot, golden-file, and input-corpus directories can hold hundreds of files and will dominate a file count while containing no test logic at all. A "top test location" with 216 files named `snapshots/` is data, not tests.

Establish: where tests live, what kinds exist (unit / integration / e2e / contract), roughly how many, whether they currently pass, and how long they take. Then the question that actually matters — **is the code you'll change covered?** If not, `characterization-tests` is in your path before any change.

Test count is a weak signal; a test suite nobody runs is decoration. Check CI for whether they gate the merge.

### 8. Config surface

```bash
find . -name "*.properties" -o -name "application*.y*ml" -o -name "appsettings*.json" -o -name ".env*" | head -25
grep -rhoE "\$\{[A-Z_]+\}|process\.env\.[A-Z_]+|os\.getenv\(['\"][A-Z_]+" . 2>/dev/null | sort -u | head -40
```

Which environments exist, what's configurable, where feature flags live. Never record values — locations only. See `../_shared/workspace-conventions.md`.

### 9. Landmines

The section people actually read.

```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND\|DO NOT" --include="*.java" --include="*.ts" --include="*.py" . \
  | wc -l
grep -rn "HACK\|DO NOT\|CAREFUL\|WARNING" --include="*.*" . | head -25
```

Look for: comments warning future readers, generated files that must not be hand-edited, deprecated paths still in use, commented-out blocks near active code, retry and timeout constants that look arbitrary, anything named `legacy`, `old`, `v1`, or `temp` still on a live path.

Where a landmine looks deliberate, `git-archaeology` will usually tell you why in two minutes. The ugly branch is frequently an incident fix, and removing it re-opens the incident.

### 10. Stop

You have enough when you can answer these five without looking anything up:

1. **Where does a request enter this system?**
2. **Where does its data live?**
3. **What else does it talk to?**
4. **Where would I add a feature like the one being asked for?**
5. **What would I be scared to touch, and why?**

If you can answer all five, stop and write it up. Continuing is depth, and depth belongs to a skill with a specific question.

If you *can't* answer one after a reasonable pass, that gap is itself the finding — record it as `[unverified]` with what would resolve it. An honest map with a labelled hole beats a confident one that quietly omits a third of the system.

### 11. Write both artifacts

`02-system-map.md` is the engagement record. `CLAUDE.md` is the working aid that loads every session. They are different documents with different audiences — see `context-strategy` step 6 for what belongs in each. Extend an existing `CLAUDE.md` rather than replacing it.

## Output template

Write to `.fde/02-system-map.md`:

```markdown
# System map — <system>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** <coverage, and what you couldn't reach>

## Scope
<What this map covers, and explicitly what it doesn't. Required in a monorepo.>

## At a glance
- **Purpose:** <what it does, one sentence, in business terms>
- **Size:** <n> files, ~<n> LOC
- **Stack:** <detected, with citation>
- **Activity:** <n> commits in 6 months; last commit <date>
- **Health:** <does it build, do tests pass, is CI green>

## Entry points
| Type | Entry | Handler | Notes |
|---|---|---|---|
| HTTP | `POST /api/orders` | `OrderController:44` | |
| Scheduled | nightly 02:00 | `ReconJob:19` | `[inferred: cron in config]` |
| Event | topic `payments.settled` | `SettlementListener:31` | |

## Module map
| Module | Responsibility | Depends on | Notes |
|---|---|---|---|

## Data
| Store | What lives there | Accessed via | Shared with |
|---|---|---|---|

## Integrations
| System | Direction | Protocol | Where configured | Owner |
|---|---|---|---|---|

## Test topology
- **Location:** · **Kinds:** · **Count:** · **Runtime:** · **Gates merge:** yes/no
- **Coverage of the area we're changing:** <the answer that matters>

## Config and environments
| Environment | Config source | Notes |
|---|---|---|

## Churn hotspots
| File | Commits (12mo) | Why it matters |
|---|---|---|

## Landmines
| What | Where | Why it matters | Confidence |
|---|---|---|---|

## The five questions
1. **Where does a request enter?** …
2. **Where does data live?** …
3. **What does it talk to?** …
4. **Where would a feature like this go?** …
5. **What would I be scared to touch?** …

## Gaps
<What you could not establish, and what would resolve it. Be specific.>
```

## Common traps

**Depth-first drift.** You open one interesting file and lose an hour. Note it as worth revisiting and move on — the map is the deliverable.

**Mapping the whole monorepo.** Above ~50,000 files, "I mapped the repo" isn't credible. Scope to a subtree and say so in the Scope section.

**Trusting the README.** It records what was true when someone last cared. CI config is ground truth; the README is a hypothesis.

**Recording structure instead of meaning.** "There is a `services` package containing 14 services" is a directory listing. Which ones matter, and why, is a map.

**Confident silence about gaps.** Omission reads as absence. A section you couldn't investigate must appear, labelled.

**Skipping non-HTTP entry points.** Batch jobs, queue consumers, and schedulers are where the surprises are.

**Answering "is it tested?" with a number.** The question is whether *the code you'll change* is covered, and whether the suite gates the merge.

**Writing the map and not the `CLAUDE.md`.** The map serves the engagement; `CLAUDE.md` serves every session after this one. Both, or you'll re-derive this in week three.
