---
name: safe-change
description: Implement a change in an unfamiliar or high-stakes codebase with the smallest viable diff - establish a green baseline first, match the surrounding idiom rather than importing your own, separate refactor commits from behavior commits, gate behind a flag where blast radius warrants it, and draft the rollback before executing the change. Use whenever writing or modifying code in a system you did not build, in legacy code, in anything touching money, data, auth, or a published contract, or when a change must be reviewed by a team that does not know you yet. Prefer this over ad-hoc implementation any time being wrong is expensive.
---

# Safe change

Implementation discipline for code you don't own.

## Why this exists

An FDE writes code under two constraints an in-house engineer doesn't have: no intuition for what's fragile, and no credibility yet to spend on a mistake. Both push the same direction — **smaller, more legible, more reversible changes than you'd otherwise make.**

There's a second, less obvious constraint. Your diff is being read by people deciding whether you're safe to let near their system. A change that works but sprawls across unrelated files, reformats things, and introduces a library nobody asked for gets merged reluctantly and remembered. A tight, idiomatic diff that reads like the person who wrote the surrounding code buys latitude for the next one.

## When this applies

- Any change in a system you didn't build
- Legacy code, code with thin coverage, or anything touching money, personal data, auth, or audit
- A change reviewed by a team that doesn't know you
- Anywhere being wrong is expensive to undo

## When it doesn't

- Your own scratch code or a throwaway spike
- A genuine emergency mitigation — do the minimum, then come back and do this properly
- Large-scale extraction or restructuring — that's `refactor-seams`

## Prerequisites

- `.fde/04-feasibility.md` — you should know where the change lands before opening a file
- `.fde/06-blast-radius-*.md` — for anything beyond a local change
- If the change site has no test coverage, run `characterization-tests` **first**. Changing untested legacy code and verifying by inspection is the single highest-risk thing in this portfolio.

## Procedure

### 1. Establish a green baseline

Before touching anything, know the state you're starting from:

```bash
git status && git rev-parse --short HEAD
<build command>       # from .fde/01-environment.md
<test command>
```

Record what passes and what already fails. Pre-existing failures are common in enterprise repositories, and discovering them *after* your change means an hour spent proving you didn't cause them.

If the baseline isn't green, decide explicitly: fix it first, or note it and proceed. Don't leave it ambiguous — and never let a pre-existing failure quietly become attributed to your change.

Branch off before you start:

```bash
git switch -c <ticket>-<short-slug>
```

Match the repository's branch naming convention. It's visible, trivial to get right, and getting it wrong is a small unforced signal that you didn't look.

### 2. Read the neighbourhood

Before writing, read two or three files adjacent to your change site. Not for behavior — for **idiom**. You're establishing:

- Naming: casing, prefixes, how the domain vocabulary is used
- Error handling: exceptions vs. result types, what gets wrapped, what propagates
- Logging: which framework, what level, structured or not, what's conventionally logged
- Null and absence handling: `Optional`, nullable, sentinel values
- Test style: naming, fixture setup, assertion library, mocking approach
- Comment density and where comments are actually used

**Match what's there, even where you'd do it differently.** A codebase with one file in a different style is worse than a codebase consistently in a style you dislike, and the FDE who imports their own conventions is a recognizable and unwelcome type. If a convention is genuinely harmful, raise it separately as an ADR — don't litigate it inside an unrelated diff.

### 3. Plan the diff before writing it

State, to yourself or in the task notes, the smallest set of changes satisfying the acceptance criteria:

```markdown
## Planned diff
- RefundService.java:88     add currency resolution        ← behavior
- RefundRequest.java:14     add field                      ← ripple
- RefundResponse.java:22    add field (published contract) ← needs versioning
- V219__refund_currency.sql new migration
- RefundServiceTest.java    3 new cases
```

If the list is longer than you expected from `feasibility-probe`, stop and work out why. Either the feasibility work missed something — worth recording — or scope is creeping.

### 4. Do the smallest thing that satisfies the criterion

Concretely:

- Prefer extending an existing abstraction over introducing a new one
- Don't add a dependency without an ADR. New third-party libraries in an enterprise repo carry licence review, security scanning, and registry mirroring — costs invisible from inside the diff.
- Don't generalize for hypothetical future requirements. You don't know this domain well enough yet, and speculative abstraction in someone else's codebase ages badly.
- Don't rename things you didn't need to rename.
- Leave the code marginally better where you touch it, and no further.

### 5. Separate refactoring from behavior

If a change needs restructuring first, make it **two commits**, or better, two pull requests:

```
commit 1: refactor: extract currency resolution from RefundService   [no behavior change]
commit 2: feat: resolve refund currency from the original order
```

This is worth real effort. A reviewer can verify a pure refactor by reading, and a behavior change by testing — but a diff mixing both requires them to do the hardest kind of review, and they will either miss something or take a week. It also keeps `git bisect` useful, which matters to whoever debugs this in a year.

Never reformat files you're editing. A formatting change buried in a functional diff destroys blame history and makes the real change invisible. If the repository has a formatter that wants to run on save, configure your editor not to reformat untouched regions.

### 6. Decide about a feature flag

Flag it when any of these hold:

- Blast radius is medium or high per the blast-radius artifact
- You can't fully verify before production
- A staged or per-tenant rollout is wanted
- Rollback by deploy is slow, gated, or awkward
- The change is behaviorally risky even though the code is simple

Don't flag when the change is genuinely local and well covered — flags carry their own cost: two code paths, two test paths, and a cleanup task that in practice never happens. Where you do add one, **write down who removes it and when**, in `06b-change-log.md`.

Use whatever flag mechanism the repository already has. Introducing a flag framework as a side effect of a feature change is its own, larger change.

### 7. Draft the rollback before executing

Before merging, write down how this gets undone. Not as an appendix — as a precondition.

- **Code:** revert the commit? Is the revert clean, or does a later migration make it not?
- **Schema:** is the migration reversible? Additive changes usually are; destructive ones aren't, and "we'd restore from backup" is a plan that needs someone to have tested it.
- **Data:** if the change writes data in a new shape, what happens to records written before a rollback?
- **Flag:** is disabling the flag genuinely sufficient, or does partially-written state persist?
- **Time:** how long does rollback take, and who can execute it?

The one-way doors are the point of this step: a destructive migration, a consumed message, a sent notification, a published event. Find them before merging, because after that you're negotiating with reality instead of a plan.

Where the rollback is anything more than "revert and redeploy," it belongs in `deploy-runbook`.

### 8. Verify against the acceptance criteria

Not "the tests pass" — walk each criterion from `03-requirements.md` and state how it's satisfied:

```markdown
- AC-1 ✅ RefundServiceTest#eurRefundStoresCurrency
- AC-2 ✅ RefundServiceTest#unsupportedCurrencyRejected
- AC-3 ⚠️  manual — needs a staging order predating the migration
```

Anything not automatically verified goes into `07-verification.md` as a gap. Don't quietly count it as done.

Then confirm you didn't break the baseline: full suite, and specifically the callers identified in the blast-radius work.

### 9. Self-review before opening the PR

Read your own diff top to bottom as a reviewer would:

```bash
git diff main...HEAD
```

Look for: debug output, commented-out code, TODOs you meant to resolve, stray formatting, files you didn't intend to touch, secrets or real data in fixtures, and anything that would make a reviewer ask "why is this here?"

That last question is the test. Every hunk should have an obvious reason for existing. Any that doesn't either needs a comment in the PR description or shouldn't be there.

Then write a PR description that answers what changed, why, how it was verified, what the blast radius is, and how to roll it back. In a team that doesn't know you, the description is doing as much work as the code.

## Output

The change itself, plus an entry in `.fde/06b-change-log.md`:

```markdown
## <date> — <change>

**Requirement:** R2 · **Branch:** `<branch>` · **PR:** <link>
**Baseline:** <n> tests passing, <n> pre-existing failures
**Files:** <count> — core: <n>, ripple: <n>, contract: <n>
**Flag:** `refund-currency` — remove by <date>, owner <name>
**Rollback:** revert PR; migration is additive and safe to leave `[confirmed: V219 adds a nullable column]`
**Verification:** AC-1 ✅ AC-2 ✅ AC-3 ⚠️ manual — see `07-verification.md`
**One-way doors:** none
**Notes:** <anything the next person needs>
```

## Common traps

**Drive-by fixes.** You'll see genuine bugs while working. Fixing them here dilutes review, breaks bisect, and makes your diff hard to reason about. Note them, raise them separately. Fix them in the same PR only if your change would otherwise be broken by them.

**Reformatting.** Destroys blame, hides the real change, and reads as carelessness.

**Importing your own conventions.** The most reliable way to be perceived as a visitor rather than a colleague.

**Adding a dependency casually.** In an enterprise repo that's a licence review, a security scan, and possibly a registry mirroring request — all invisible from inside the diff.

**Skipping the baseline.** Then spending an hour proving a pre-existing failure isn't yours.

**Mixing refactor and behavior.** Forces the reviewer into the hardest kind of review. They'll either miss something or stall.

**Treating rollback as an afterthought.** Discover the one-way door before merging, not during the incident.

**"The tests pass" as verification.** The tests verify what they were written to verify. Walk the acceptance criteria explicitly.

**A flag with no removal owner.** It will be there in three years, and by then nobody will know whether it's safe to delete.
