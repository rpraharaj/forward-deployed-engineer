---
name: characterization-tests
description: Pin the current behavior of untested legacy code before changing it - including behavior that looks like a bug, because something downstream may depend on it - using golden master and approval test patterns so a refactor or fix can be verified as behavior-preserving. Use before modifying code with thin or no test coverage, before any refactor of legacy code, when a change site has no tests and you need a safety net, or when someone says "we can't change that, nobody knows what it does". This is what makes legacy change safe rather than brave.
---

# Characterization tests

Pinning what the code does now, so you can tell whether you changed it.

## Why this exists

Changing untested legacy code and verifying by inspection is the highest-risk activity in this portfolio. You cannot hold the behavior of a two-thousand-line method in your head, and neither can the reviewer, so "it looks equivalent" is the standard being applied — and it fails silently.

Characterization tests invert the usual purpose of a test. They don't assert what the code *should* do; nobody knows that. They record what it **currently does**, so that a change which alters behavior fails loudly instead of shipping. The specification is the existing code, and the test is a fixed point you can refactor against.

The counter-intuitive part, and the part people resist: **you pin the bugs too.** Something downstream has probably adapted to the wrong rounding, the off-by-one, the empty string where null was meant. Preserving current behavior is the point. Fixing bugs is a separate, later, deliberate change with its own blast radius.

## When this applies

- About to change code with thin or no coverage
- Any refactor of legacy code
- "Nobody knows what that does, so we don't touch it"
- Before `refactor-seams` or a risky `safe-change`

## When it doesn't

- The code is already well covered — check what the existing tests actually assert, then proceed
- Genuinely new code — write real tests asserting intended behavior
- You're deliberately changing behavior and the current behavior is agreed wrong — still consider pinning the *surrounding* behavior you're not changing
- Throwaway code

## Prerequisites

- `.fde/01-environment.md` — you need to be able to run tests
- `.fde/04-feasibility.md` — the change sites you're protecting
- Read `references/harness-by-stack.md` for the framework and approval-test tooling matching your stack

## Procedure

### 1. Find the seam

A seam is a place where you can observe behavior without modifying the code under test. Testability is entirely a question of where the seams are.

Ordered by preference, because each is more work than the last:

1. **Public function with in-memory inputs and outputs** — ideal, test directly
2. **Class with injectable dependencies** — substitute fakes at the constructor
3. **HTTP or CLI boundary** — slower, but requires no code change and no understanding of internals
4. **Database or file state** — set up, run, snapshot the resulting state
5. **No seam** — you must introduce one, which is itself a change. Make it the smallest possible, commit it separately, and characterize *before* and *after* to prove the seam introduction changed nothing.

Testing at a coarse boundary is a legitimate choice. A characterization test at the HTTP layer that pins fifty responses is more valuable than three perfect unit tests, even though it's slower and less precise.

### 2. Capture inputs that actually occur

Coverage of realistic inputs matters more than coverage of lines. Sources, roughly in order of value:

- **Production logs or request samples** — the real distribution. Redact before use; see `../_shared/workspace-conventions.md`
- **Existing test fixtures**, even from tests that are disabled or broken
- **The database** — real stored values show the shapes that actually exist
- **Boundary values** — empty, null, zero, negative, maximum, unicode, very long
- **The weird ones** the code visibly special-cases; those branches exist for a reason

Never copy production data into a test fixture. Derive the *shape*, synthesize the values, and say you did. See `test-data-strategy`.

### 3. Record current behavior, don't assert intended behavior

Run the code and capture what comes out. Where the output is large, use an approval or snapshot test — write the output to a file, eyeball it once for obvious catastrophe, and commit it as the baseline.

**When the output looks wrong, keep it and annotate it:**

```
// CHARACTERIZATION: records current behavior, not correct behavior.
// Rounds half-down; correct financial rounding is half-up.
// Do not "fix" here — see ADR-0007. Downstream reconciliation may depend on this.
```

That comment is essential. Without it, the next engineer sees a test asserting wrong behavior and helpfully corrects it, which is precisely the failure the test existed to prevent.

### 4. Cover the branches you're about to touch

You don't need to characterize the whole class — you need the region your change lands in.

Where a coverage tool is available, use it to confirm your tests actually reach the change site. Where it isn't, a temporary log line or a deliberate exception at the change site proves the test reaches it. Untested confidence that a test covers something is worth very little.

### 5. Verify the tests fail when behavior changes

**Do not skip this.** A characterization test that passes regardless of behavior is worse than none — it produces confidence with no basis.

Mutate the code under test deliberately: invert a condition, change a constant, return early. Confirm the test goes red. Revert.

If it stays green, the test isn't reaching the behavior you think it is, and the seam or the input set is wrong.

### 6. Commit them separately, before the change

Their own commit or PR, ahead of the behavior change. Three reasons: the reviewer can see the safety net exists before reviewing the risky part; the tests are demonstrably passing against unmodified code; and if the change is abandoned, the tests remain as a contribution.

`git bisect` also stays useful, which whoever debugs this in a year will appreciate.

### 7. Then make the change

Run the characterization suite. Anything that goes red is a behavior change — either unintended, in which case fix it, or intended, in which case update the test **and say so explicitly in the PR description**, because a modified characterization test is exactly what a reviewer needs to look at hardest.

## Output

Tests in the repository's own convention, plus a short note in `.fde/06b-change-log.md`:

```markdown
## Characterization — <component>

**Protecting:** `RefundCalculator` before multi-currency change
**Seam:** public `calculate()` — in-memory, no substitution needed
**Cases:** 24 — 18 from prod log shapes (synthesized values), 6 boundary
**Coverage of change site:** confirmed via coverage report — lines 88-140
**Mutation check:** inverted condition at :94 → 7 tests failed ✅
**Known-wrong behavior pinned:**
  - Rounds half-down at :112 — annotated, see ADR-0007
  - Returns empty string, not null, for unknown currency at :131
**Committed:** PR #418, ahead of the behavior change in #419
```

## Common traps

**Fixing bugs while characterizing.** The most common and most damaging. Pin the bug, annotate it, raise it separately. Something downstream has probably adapted to it.

**Not annotating the wrong behavior.** The next engineer will helpfully "fix" the test, defeating its purpose entirely.

**Skipping the mutation check.** A test that can't fail is worse than no test, because it manufactures confidence.

**Characterizing the whole class.** Cover the region you're changing. The rest is someone else's problem today.

**Only using clean inputs.** The value is in the ugly real ones — the empty strings, the legacy formats, the records from before the last migration.

**Copying production data into fixtures.** Derive the shape, synthesize the values.

**Mixing the tests into the change commit.** The reviewer needs to see the net exists before assessing the trapeze act.

**Treating them as permanent.** These are scaffolding. Once real behavior is specified and properly tested, characterization tests can be replaced by tests that assert intent. Note that in the handover rather than leaving them to be mistaken for a specification.
