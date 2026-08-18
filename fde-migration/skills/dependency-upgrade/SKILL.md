---
name: dependency-upgrade
description: Run an EOL or version-driven upgrade where the scope is fixed, the deadline is external, and the risk is concentrated in transitive breakage - ordering the upgrade, building a compatibility matrix, cutting over incrementally, and telling a real break from a warning. Use for end-of-life work, runtime or framework major-version jumps, expiring vendor support, security-driven dependency bumps, or when a library upgrade cascades further than expected. Behaves unlike feature work and should not be planned like it.
---

# Dependency upgrade

Work where you don't get to choose the scope or the date.

## Why this exists

EOL-driven work — a runtime going out of support, a framework major version, a database version, an expiring vendor contract — is an enormous share of enterprise IT and it behaves unlike feature work in three ways:

- **Scope is fixed.** You can't descope your way out of Java 8 losing support.
- **The deadline is external.** Nobody in the organization can move it.
- **The risk is transitive.** The library you're upgrading is fine; the four things depending on it are the problem, and they surface one at a time.

Planned like a feature, it goes wrong predictably: an estimate based on the direct change, then weeks of cascading incompatibilities nobody sized. The work isn't the upgrade. It's the fallout.

The compensating advantage: it's unusually amenable to systematic treatment. The compatibility matrix is knowable up front, and most of the pain comes from not building one.

## When this applies

- End-of-life: runtime, framework, database, OS, vendor product
- Major version jumps
- Security-driven bumps that cascade
- A library upgrade pulling in more than expected

## When it doesn't

- Routine patch bumps handled by automation
- The upgrade is genuinely one line and the tests pass — just do it
- Replacing rather than upgrading — that's `refactor-seams` or a migration

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/02-system-map.md`
- `.fde/01-environment.md` — you need a working build before changing what it builds with
- `characterization-tests` where coverage is thin. An upgrade with no tests is a rewrite you can't verify.

## Procedure

### 1. Establish the real deadline and what happens after it

"End of life" means different things and the difference matters enormously to how much leverage you have:

- No more feature releases — soft
- No more security patches — hard for most compliance regimes
- Vendor refuses support tickets — hard operationally
- Service actively stops working — hard, absolute

Also find out whether **extended support** can be bought. It frequently can, it frequently isn't considered, and it converts an impossible deadline into a budget conversation. That's worth raising even if the answer is no — see `escalation-and-renegotiation`.

### 2. Build the compatibility matrix before touching anything

The step that determines whether this goes well.

List every dependency, its current version, the version required for the target, and whether that version exists. You are looking specifically for **blockers**: dependencies with no compatible version, abandoned libraries, and internal shared libraries owned by another team.

```bash
# Use the tree command for the stack you detected (see fde-core stack-detection
# if that pack is installed). Do not run every ecosystem's tool.
```

If you cannot find the tree command, record the direct dependencies from the manifest and tag transitives `[unverified]`.

Three findings matter most:

- **Abandoned dependencies.** No compatible version will ever exist. Each is a replacement project inside your upgrade, and it must be sized separately.
- **Internal shared libraries.** Another team must upgrade first. That's a dependency with a lead time and possibly a negotiation — surface it in week one.
- **Transitive conflicts.** Two dependencies requiring incompatible versions of a third. The hardest category and the least visible.

The matrix is the single most useful artifact this skill produces, and it turns an unbounded upgrade into a bounded list.

### 3. Order the upgrade

Rarely a single jump. Sequence matters:

- **Bottom-up.** Shared internal libraries before their consumers.
- **Intermediate versions.** Two major versions is often two upgrades, not one — and the intermediate step frequently has migration tooling the direct jump doesn't.
- **Blockers first.** An abandoned dependency needing replacement should start immediately; it has the longest lead time and it can invalidate the whole plan.
- **Test infrastructure early.** If your test framework doesn't support the new runtime, you're upgrading blind. Fix that before anything else.

That last point catches people out constantly. An upgrade where the tests won't run has removed the only mechanism for verifying it.

### 4. Separate the mechanical from the semantic

Two very different kinds of change, and they should be different commits:

- **Mechanical** — renamed packages, moved classes, changed signatures. High volume, low risk, often automated by a migration tool the vendor supplies. Look for one before doing it by hand.
- **Semantic** — changed default behavior, different null handling, altered ordering, stricter parsing. Low volume, high risk, and invisible in a diff.

Semantic changes are where upgrades break in production. Read the release notes and the migration guide specifically for behavior changes, not just for API changes. A method that kept its signature and changed what it does is the worst case, and it will pass compilation.

### 5. Tell a real break from a warning

Upgrades generate enormous noise: deprecation warnings, new lint failures, changed log formats, stricter compiler checks. Most of it doesn't matter now.

Triage explicitly:

- **Breaks the build** — must fix
- **Breaks a test** — must understand. Distinguish "the test asserted old behavior" from "behavior is now wrong." These look identical and mean opposite things.
- **Deprecation warning** — record, don't fix. It's the next upgrade's work, and fixing it now inflates this change and its review.
- **New lint or style failure** — usually suppress for this change and address separately

The discipline is scope control. An EOL upgrade that also fixes four hundred deprecation warnings is unreviewable, and the review is where a semantic break would have been caught.

### 6. Cut over incrementally where you can

A big-bang upgrade of every module at once maximizes blast radius. Where the codebase permits, upgrade module by module, shipping each.

Where it doesn't — a runtime version usually applies to everything at once — you can still stage the *rollout*: one instance, then a percentage, then all, watching for the semantic differences that tests didn't catch. See `deploy-runbook`.

### 7. Verify behavior, not just compilation

An upgrade that compiles and passes tests can still be wrong, because the tests were written against the old behavior and may assert things that are no longer correct.

Highest-value checks: run the characterization tests, compare outputs before and after on real inputs, and watch the semantic-change list from step 4 specifically. A **parallel run** — see `refactor-seams` — is unusually valuable here, because the two implementations are supposed to be identical, so any divergence is a finding.

## Output

Write to `.fde/05c-upgrade-matrix.md`:

```markdown
# Upgrade — <from> → <to>

**Engagement:** <name> · **Date:** <YYYY-MM-DD>
**Deadline:** <date> · **What happens after:** no further security patches — hard for PCI scope
**Extended support available:** yes, ~<cost> — raised with <name> on <date>

## Compatibility matrix
| Dependency | Current | Needed | Available? | Status |
|---|---|---|---|---|
| framework-core | 2.7 | 3.2 | yes | direct upgrade |
| internal-auth-lib | 1.4 | 2.0 | **not yet** | **blocked — Team Platform, ETA <date>** |
| legacy-xml-parser | 1.1 | — | **abandoned 2019** | **replacement needed — size separately** |
| test-framework | 4.x | 5.x | yes | **do first — else upgrading blind** |

## Blockers
| # | Blocker | Impact | Plan | Owner |
|---|---|---|---|---|
| 1 | `legacy-xml-parser` abandoned | Used in 6 places | Replace with <x> — separate work item | FDE |
| 2 | `internal-auth-lib` not ready | Hard blocker | Team Platform; chase weekly | FDE |

## Order
1. Test framework 4 → 5 *(so we can verify anything)*
2. Replace `legacy-xml-parser`
3. Wait on `internal-auth-lib`
4. framework-core 2.7 → 3.0 → 3.2 *(intermediate has migration tooling)*
5. Module-by-module cutover

## Semantic changes to verify
| Change | Where it bites | Verified |
|---|---|---|
| Default date parsing now strict | 4 endpoints accept loose ISO | ⏳ |
| Map iteration order no longer insertion-ordered | Report generation | ⏳ |

## Deferred
<Deprecation warnings recorded, not fixed. Next upgrade's work.>
```

## Common traps

**Planning it like feature work.** Fixed scope, external deadline, transitive risk. Different shape.

**Estimating the direct change.** The work is the fallout, and the matrix is how you size it.

**Not building the matrix.** Turns a bounded list into an unbounded series of surprises.

**Upgrading before the test framework.** You've removed the only way to verify anything.

**Missing abandoned dependencies.** Each is a replacement project hiding inside the upgrade.

**Fixing every deprecation warning.** Makes the change unreviewable, which is where a semantic break would have been caught.

**Confusing "test asserted old behavior" with "behavior is now wrong."** Identical symptoms, opposite meanings.

**Trusting compilation.** Semantic changes keep the signature and change the meaning.

**Not asking about extended support.** Frequently available, rarely considered, converts a deadline into a budget question.
