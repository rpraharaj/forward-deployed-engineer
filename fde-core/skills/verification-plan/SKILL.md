---
name: verification-plan
description: Map every acceptance criterion to the specific evidence that proves it - which test, which manual check, which measurement - and surface the gap list of criteria with no verification at all. Use once implementation is underway, before claiming anything is done, before a release decision, or when someone asks "how do we know this works". Also use when a definition of done exists but nobody has said how each part will be checked. The main output is the gap list, not the coverage claim.
---

# Verification plan

Connecting what was promised to what was proven.

## Why this exists

"The tests pass" is not verification. It means the assertions someone wrote earlier still hold — which says nothing about whether the thing that was asked for actually works. The two diverge constantly, because tests are written against the implementation as built and acceptance criteria were written against the need as understood.

The gap between them is where the awkward release conversations live: seven criteria agreed, five with automated tests, one checked manually by someone who has since moved teams, and one that nobody ever verified and nobody noticed.

This skill's real output is not the coverage table. It's the **gap list** — the criteria with no evidence. That list is short, uncomfortable, and the most useful thing you can put in front of a release decision.

## When this applies

- Implementation underway or complete
- Before claiming a requirement is done
- Feeding `release-readiness`
- "How do we know this works?"
- Done is defined but how it will be checked isn't

## When it doesn't

- No acceptance criteria exist yet — run `requirements-to-spec` first, or you're verifying against nothing
- Pure spike or throwaway work
- Diagnosing a broken pipeline — that's `ci-forensics`

## Prerequisites

- `.fde/03-requirements.md` — the criteria being verified. **Required.** Without it this skill has no input.
- `.fde/03b-nfrs.md` — non-functionals, if they exist
- `.fde/06-blast-radius-*.md` — the verification list it produced
- `.fde/06b-change-log.md` — what actually shipped

## Procedure

### 1. Start from the criteria, never from the tests

Direction matters enormously.

Starting from the tests and asking "what do these prove?" produces a comfortable document that always looks complete, because every test verifies *something*. Starting from the criteria and asking "what proves this?" produces the gaps.

List every acceptance criterion from the spec. Add the verification items from `blast-radius`, and every NFR. That's your row set, and it's fixed before you look at a single test.

### 2. For each row, name the specific evidence

Not "unit tests" — the **named test**, the **named check**, the **named measurement**.

| Evidence type | What makes it acceptable |
|---|---|
| Automated test | Named test that fails if the behavior regresses |
| Manual check | Who did it, when, in which environment, what they observed |
| Measurement | The metric, the value, where it was measured, against what target |
| Inspection | Only for things genuinely not executable — a config value, a permission grant. Say who inspected it. |
| **None** | The gap list |

The test for whether evidence is real: **could someone else re-run it and get the same answer?** "It was tested" fails that. "`RefundServiceTest#eurRefundStoresCurrency`" passes it.

Manual checks are legitimate — some things can't be automated economically. But they decay: a manual check performed once against a build three weeks ago proves very little about what's shipping today. Record the date and the revision.

### 3. Confirm the evidence actually verifies the claim

A named test is not automatically proof. Two failure modes worth checking directly:

**The test doesn't assert what you think.** A test named `shouldRejectInvalidCurrency` that asserts only "no exception thrown" verifies almost nothing. Read the assertions, not the name.

**The test can't fail.** Over-mocked tests frequently assert on the mock rather than the code. If you're unsure, mutate the production code and confirm the test goes red — the same discipline as `characterization-tests` step 5.

Where you haven't confirmed this, tag the row `[inferred]` rather than `[confirmed]`.

### 4. Check the regression surface, not just the new behavior

Verification covers two questions: does the new thing work, and did anything else break?

The second is answered by the blast-radius verification list. Each identified consumer needs a specific check — the full suite passing is necessary and rarely sufficient, particularly for consumers outside this repository, which the suite by definition cannot cover.

### 5. Verify the non-functionals as measurements

An NFR verified by assertion isn't verified. "Performance is fine" is not evidence; "p95 measured at 0.9s in staging on 03-19 against a 1.0s target" is.

Where a measurement is impossible in the environments you have — no prod-scale load environment, common in enterprise — that is a **gap**, not a pass. Record what you couldn't measure and what would be needed. `release-readiness` will surface it as residual risk, which is exactly where it belongs.

### 6. Produce the gap list

Extract every row with no evidence, or with evidence you couldn't confirm. For each:

- What's unverified
- Why — no environment, no data, no access, no time, not automatable
- What it would take
- **Is it detectable in production if wrong?** A failure that alerts within minutes is a very different risk from one that corrupts data silently for a month

That last column matters more than the others. It converts the gap list from a list of anxieties into a ranked risk register, and it's what a release decision actually needs.

### 7. Say what "done" means now

Close with a plain statement of the position: how many criteria have confirmed evidence, how many are gaps, and whether you'd call this verified.

Resist rounding up. A feature with six of seven criteria verified is not "done" — it's six of seven, and the seventh is either acceptable or it isn't. Making that explicit is the skill's contribution.

## Output template

Write to `.fde/07-verification.md`:

```markdown
# Verification — <feature>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** <how much evidence you confirmed vs. took on trust>

## Position
**<n> of <m> criteria have confirmed evidence. <k> gaps, of which <j> would be silent in production.**

<Two sentences. Would you call this verified?>

## Criteria → evidence

| ID | Criterion | Evidence | Type | Confirmed | Date |
|---|---|---|---|---|---|
| AC-1 | EUR refund stores currency | `RefundServiceTest#eurRefundStoresCurrency` | automated | ✅ | CI @ `a3f9c1` |
| AC-2 | Unsupported currency rejected | `RefundServiceTest#unsupportedCurrencyRejected` | automated | ✅ | CI @ `a3f9c1` |
| AC-3 | Pre-migration orders still refundable | manual, staging, T. Nakamura | manual | ✅ | 03-19 |
| AC-4 | Refund appears in daily report | **none** | — | ❌ | — |

## Regression surface
| Consumer (from blast radius) | Check | Result |
|---|---|---|
| `billing-web` | contract test | ✅ |
| Nightly warehouse sync | asked data team to confirm | ⏳ no response since 03-12 |

## Non-functional
| NFR | Target | Measured | Where | Result |
|---|---|---|---|---|
| Refund p95 | < 1.0s | 0.9s | staging, 03-19 | ✅ |
| Under prod volume | < 1.0s | **not measured** | — | ❌ gap |

## Gap list

| # | Unverified | Why | To close | Detectable if wrong? |
|---|---|---|---|---|
| 1 | AC-4 — refund in daily report | Report runs nightly; no staging schedule | Trigger report manually in staging — 1h | **No** — silently wrong figures until month-end |
| 2 | Prod-volume latency | No prod-scale load environment | Load test env, or staged rollout with monitoring | Yes — p95 dashboard, minutes |
| 3 | Warehouse sync compatibility | Data team unresponsive | Escalate, or test in staging against a sync copy | **No** — fails next daily run |

## Evidence quality notes
<Tests whose assertions are weaker than their names suggest; manual checks that are now stale.>
```

## Common traps

**Starting from the tests.** Produces a complete-looking document with the gaps invisible. Always start from the criteria.

**"Unit tests" as evidence.** Name the test, or it isn't evidence.

**Trusting a test by its name.** Read the assertions. `shouldRejectInvalidInput` that only asserts no-exception verifies nothing.

**Counting a stale manual check.** Performed against a three-week-old build in an environment that has since changed, it proves very little. Record the date and revision.

**Treating an unmeasurable NFR as a pass.** It's a gap. Record it and let the release decision weigh it.

**Ignoring the regression surface.** Half of verification is "did anything else break," and the suite can't see cross-repo consumers.

**Rounding up.** Six of seven is six of seven.

**Burying the gap list.** It's the output. Put it where it will be read.
