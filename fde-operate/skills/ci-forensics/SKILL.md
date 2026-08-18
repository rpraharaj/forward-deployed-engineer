---
name: ci-forensics
description: Diagnose a red, flaky, or slow pipeline by identifying the failure class first - genuine break, flake, environment drift, ordering dependency, or resource contention - before attempting fixes, and distinguishing making it green from making it right. Use when the build is failing, when tests pass locally but not in CI, when a suite is intermittently red, when the pipeline is too slow to be useful, or when someone says "just re-run it". A pipeline nobody trusts provides no signal, which is worse than having no pipeline.
---

# CI forensics

Getting the pipeline back to meaning something.

## Why this exists

A flaky pipeline is worse than no pipeline. Once "just re-run it" becomes the standard response to a red build, the suite has stopped being a signal — and the genuine failure it eventually catches gets re-run away like all the others.

Teams reach this state gradually and rarely climb out, because each individual re-run is cheaper than each individual investigation. The economics only look right locally.

An FDE lands in this often, and has a specific advantage: no accumulated tolerance for it. You haven't learned which failures to ignore, which means you notice that the team has learned to ignore them.

The main discipline is diagnosing the **class** of failure before fixing anything. The classes look identical from the outside — a red build — and have completely different causes and fixes.

## When this applies

- The build is failing and the cause isn't obvious
- Tests pass locally, fail in CI
- Intermittent red builds
- The pipeline is too slow to be useful
- "Just re-run it" has become normal

## When it doesn't

- A single obvious failure with a clear cause — just fix it
- Production is broken — that's `incident-triage`
- You need to build a pipeline that doesn't exist yet

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/01-environment.md` — a working local build, so you can compare against CI
- Access to CI logs and history. Build history is the primary evidence here.

## Procedure

### 1. Classify the failure before fixing anything

Five classes. They present identically and have nothing else in common.

| Class | Signature | Fix direction |
|---|---|---|
| **Genuine break** | Fails consistently, same point, correlates with a change | Fix the code |
| **Flake** | Same commit passes and fails | Find the nondeterminism |
| **Environment drift** | Passes locally, fails in CI; or worked last week | Align the environments |
| **Ordering dependency** | Fails only in some run orders or in parallel | Isolate the shared state |
| **Resource contention** | Fails under load; timeouts; more common on busy days | Resource limits |

The distinguishing question for a flake: **does the same commit both pass and fail?** That's the definitive test, and it's usually answerable from build history in a minute.

```bash
# Re-run the same commit a few times — flakes surface fast
for i in 1 2 3 4 5; do <test command> >/dev/null 2>&1 && echo "$i pass" || echo "$i FAIL"; done
```

### 2. Read the build history, not just the latest failure

The most informative source, and routinely skipped in favour of staring at one log.

- When did this start failing? Correlate with commits, dependency updates, and infrastructure changes.
- Is it every run, or a percentage? Estimate the rate — a 5% flake and a 60% flake are different problems.
- Which tests, and do they cluster? Clustering points at shared state.
- Do failures correlate with time of day, day of week, or agent identity? All point at contention or drift.

### 3. Find what differs between local and CI

Where it passes locally and fails in CI, something differs. It's almost always in this list:

- Toolchain or runtime version — three-layer survey in `fde-core` `_shared/stack-detection.md`. Do not conclude a pin is missing from dedicated files alone.
- Environment variables present locally, absent in CI
- Timezone and locale, which CI usually runs as UTC and `C`
- Available memory, CPU count, and disk
- Network access, which CI may restrict
- Test execution order — CI often parallelizes or randomizes
- Filesystem case sensitivity — macOS local, Linux CI, and a filename that differs only by case
- Clean checkout versus your incrementally-built local state

That last one catches people constantly: a stale artifact locally makes a broken build pass on your machine.

### 4. For flakes, find the nondeterminism

Flakes come from a short list. Work through it:

- **Time** — tests asserting on `now()`, timeouts too tight for a loaded agent, dates crossing midnight or DST
- **Order** — shared static state, a database not reset, files left behind. Run the suite in reverse or randomized order to confirm.
- **Concurrency** — races surfacing under parallel execution, or on a machine with a different core count
- **External dependencies** — network calls in tests. These should not exist; where they do, that is the finding.
- **Randomness** — unseeded generators. Seed them.
- **Resource limits** — memory or connection pools sized for a quiet machine

The strongest signal for order dependence is a test that passes alone and fails in the suite. Bisect the suite to find the pair.

### 5. Distinguish making it green from making it right, and say which

Both are legitimate. Conflating them is not.

- **Green now** — quarantine the flaky test, retry the flaky step, pin the drifting version. Legitimate as a *stated* stopgap when the pipeline is blocking everyone.
- **Right** — fix the nondeterminism, align the environments, resolve the contention.

Where you take the stopgap, **record it with an owner and a date**. A quarantined test with no removal plan is a permanently reduced test suite, and after enough of them the pipeline is green because it stopped checking.

Never add a blanket retry to make a suite green. It converts a visible flake into an invisible one and destroys the pipeline's value as a signal — the exact failure this skill exists to reverse.

**Stop** when the failure is classified, one class has been treated (fixed or a dated quarantine), and the verification impact is written. A flaky estate can absorb a week; this skill does not.

### 6. Treat slowness as a correctness problem

A pipeline slow enough that people avoid running it has the same effect as an unreliable one.

Find where the time goes — most suites have a small number of dominant contributors. Common wins: parallelize, cache dependencies, split fast checks from slow ones so feedback arrives early, and remove tests that make real network calls.

Establish what feedback time the team actually needs, and optimize toward that rather than toward an abstract "faster."

### 7. Report the state honestly

If the suite is quarantined heavily, or the flake rate is 30%, that is a **verification finding** and it belongs in `verification-plan` and `release-readiness`. A green build from an untrustworthy pipeline is not evidence, and reporting it as evidence is how a bad change ships with a passing build behind it.

## Output

Write to `.fde/07b-ci-notes.md`:

```markdown
# CI forensics

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Pipeline:** <name> · **Observation window:** <n> builds, <dates>

## State
- **Pass rate:** 61% on unchanged commits — **suite is not trustworthy**
- **Median duration:** 34 min · **Team's needed feedback time:** < 10 min
- **Quarantined tests:** 7, oldest quarantined 14 months ago

## Failures by class
| Class | Count | Examples | Status |
|---|---|---|---|
| Flake | 12 | `OrderSyncTest` — order dependence | 4 fixed, 8 open |
| Environment drift | 1 | Agent had Java 17, build needs 21 | fixed — pinned in CI config |
| Ordering | 3 | Shared static cache not reset | fixed |
| Resource contention | 2 | Timeouts on busy agents | mitigated — timeout raised |
| Genuine | 1 | Real null-handling regression | fixed |

## Root causes
| # | Cause | Tests affected | Fix | Done |
|---|---|---|---|---|
| 1 | Static `OrderCache` not reset between tests | 3 | Reset in teardown | ✅ |
| 2 | `PaymentTest` calls a real sandbox API | 1 | Replaced with a fake | ✅ |
| 3 | Unseeded random in fixture builder | 2 | Seeded | ✅ |

## Stopgaps in place
| What | Why | Owner | Remove by |
|---|---|---|---|
| `ReconciliationTest` quarantined | Order-dependent, needs restructure | <name> | <date> |

## Verification impact
Before this work the suite could not be used as release evidence (61% pass on unchanged
commits). Now at 97%. The 7 quarantined tests mean **reconciliation logic is not covered**
by CI — recorded as a gap in `07-verification.md`.
```

## Common traps

**Fixing before classifying.** Five classes, identical symptoms, unrelated fixes.

**Staring at one log instead of reading history.** History tells you when it started and how often.

**Blanket retries.** Converts a visible flake into an invisible one and finishes off the pipeline's value.

**Quarantining with no owner or date.** A permanently reduced suite that's green because it stopped checking.

**Not saying which mode you're in.** Green-now and right are both legitimate; conflating them isn't.

**Ignoring slowness.** A suite people avoid has the same effect as one they don't trust.

**Tolerating network calls in tests.** A guaranteed flake source and usually easy to remove.

**Treating a green build from an untrusted pipeline as evidence.** It isn't, and `release-readiness` needs to know.
