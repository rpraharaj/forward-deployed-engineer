---
name: requirements-to-spec
description: Turn a vague ask into a testable specification - separate the stated request from the underlying need, write acceptance criteria as observable behavior, state what is explicitly out of scope, and record every assumption with who can confirm it. Use when handed an ambiguous requirement, a one-line ticket, a feature request relayed secondhand, meeting notes, or when someone says "they want us to add X" and nobody has written down what that means. Also use before estimating anything, since an estimate against an unwritten requirement is a guess. Produces the spec that feasibility-probe grounds in real code.
---

# Requirements to spec

Converting prose into something you can verify against.

## Why this exists

An FDE almost never receives requirements from the person who has the problem. They arrive relayed — through a delivery lead, a ticket someone wrote after a meeting, or a conversation with an engineer repeating what they were told. Each hop drops context and silently resolves ambiguity, usually toward whatever the relayer assumed.

The result is a request that sounds specific and isn't. "Add a currency field to refunds" is a sentence everyone nods at, and it conceals at least five decisions nobody has made.

This skill's job is to surface those decisions **before** they're made accidentally in code, and to write the requirement down in a form where "is it done?" has an answer. Everything downstream depends on it: `feasibility-probe` grounds this spec in code, `verification-plan` maps these criteria to evidence, and `release-readiness` reports against them.

## When this applies

- A vague or one-line ask
- Requirements relayed through intermediaries
- Before estimating or designing anything
- Meeting notes that need to become work
- Nobody can state what "done" means

## When it doesn't

- A well-specified ticket with acceptance criteria already written — check it's testable, then proceed
- A production incident. Fix it; specify later.
- Pure investigation with no behavior change — that's an assessment engagement

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

`<workspace>/00-engagement.md` — the sponsor and the real problem from the charter are the frame for everything here.

Read `discovery/workflow-*.md`, `discovery/opportunities.md`, and `outcomes/<initiative>.md` when available. If no problem has been chosen, use `use-case-selection`; if the human process is unclear, use `workflow-discovery`. Existing clear requirements do not need those extra steps.

## Procedure

### 1. Capture the ask verbatim

Record the original wording before you interpret it. Paraphrasing is the first place ambiguity gets silently resolved, and once the paraphrase is written down the original is gone.

Also record **who said it, when, and to whom**. Provenance matters: a requirement from the sponsor and a requirement from a developer's recollection of a corridor conversation are different objects, and should not look identical in the document.

### 2. Find the underlying need

For each requirement, ask: **what happens if we don't do this?**

The answer reveals the real need, which is often adjacent to the request rather than identical. "Make the export faster" may mean "I need the figures before the 9am meeting" — solvable by scheduling, caching, or a partial result, none of which involve optimizing the export.

This is where an FDE earns disproportionate credibility. Solving the stated ask when a cheaper solution to the real need existed is a technically successful outcome nobody thanks you for.

Record both. Where they differ, say so explicitly — that sentence often changes the shape of the whole engagement.

### 3. Identify actors and observable change

For each requirement, be able to complete: **who** does **what**, and **what is observably different afterwards?**

If you can't name the actor, you don't have a requirement — you have a technical task in search of a justification. If you can't name the observable difference, you can't test it, and "done" will be a matter of opinion.

Observable means visible from outside the system: a response contains a field, a report shows a figure, a record appears, a notification is sent. "The service handles currencies correctly" is not observable. "A refund for a EUR order returns `currency: EUR` and an amount matching the original charge" is.

### 4. Write acceptance criteria

One criterion per behavior, each independently checkable. Use the repository's existing convention if it has one — a Cucumber suite or a ticket template is a convention worth matching, and matching it costs nothing.

Absent a house style, plain conditional statements work:

> **AC-3** — Given an order placed in EUR, when a full refund is issued, then the refund record stores `currency = EUR` and `amount` equal to the original charge amount.

Each criterion needs to be:

- **Observable** — checkable from outside the system
- **Unambiguous** — two engineers would build the same thing
- **Independent** — passes or fails on its own
- **Bounded** — no "and so on", no "etc."

Cover the unhappy paths deliberately. Most ambiguity hides there: what happens on a partial refund, an unsupported currency, a missing rate, a refund against an order predating the change. Each is a decision somebody must make, and if you don't ask, code will make it silently.

**Undecided unhappy paths stay Open questions, not acceptance criteria.** A spec that invents the behavior so the table looks complete is fiction, and `feasibility-probe` will ground the fiction.

### 5. Write down what's out of scope

The most valuable and most skipped section.

Scope disputes at the end of an engagement are almost never about what was in the spec — they're about what a stakeholder assumed was implied. Writing "historical refunds will not be backfilled" costs one line now and settles an argument later that would otherwise cost days and goodwill.

List what a reasonable person might assume is included and isn't: adjacent features, other channels, historical data, other environments, migration of existing records, UI changes accompanying an API change.

### 6. Separate requirements from design decisions

Requirements that arrive pre-designed are common and worth unpacking: "add a Kafka topic for refund events" is a solution, not a requirement. The requirement underneath is that something needs to know when a refund happens.

Record the requirement, and note the suggested design separately. Sometimes the design constraint is real — a platform standard, an existing contract — and then it's a constraint, which belongs in the charter. Sometimes it's one person's preference wearing a requirement's clothes, and `solution-design` should evaluate it against alternatives.

Do this carefully rather than pointedly. The goal is a better outcome, not demonstrating that someone over-specified.

### 7. Record assumptions and open questions

Every question you couldn't get answered becomes one of:

- **Assumption** — you've picked an answer and are proceeding. State it prominently, because if it's wrong the work changes.
- **Open question** — genuinely blocking. Name **who can answer it** and whether work can proceed meanwhile.

An assumption nobody sees isn't an assumption; it's a defect waiting for acceptance testing. Put them where a stakeholder skimming the document will read them.

### 8. Get it confirmed

Send the spec to the requester and the sponsor. Ask specifically about the assumptions and the out-of-scope list, since that's where disagreement hides — people read acceptance criteria and nod; they read "will not be backfilled" and object.

Record who confirmed and when. Unconfirmed, the spec is your interpretation, and should say so in the Confidence line.

## Output template

Write to `<workspace>/03-requirements.md`:

```markdown
# Requirements — <feature>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | confirmed by <name> on <date>
**Source revision:** <repo>@<short SHA>
**Confidence:** <confirmed by the sponsor, or still your interpretation>

## The ask, as received
> <verbatim>

**From:** <name, role> · **Via:** <direct | relayed by …> · **Date:** <date>

## Underlying need
<What happens if this isn't done. Where this differs from the ask, say so.>

## In scope
| ID | Requirement | Actor | Observable outcome |
|---|---|---|---|
| R1 | | | |

## Acceptance criteria
| ID | Req | Criterion | How it's checked |
|---|---|---|---|
| AC-1 | R1 | Given …, when …, then … | automated test / manual / metric |

### Unhappy paths
| ID | Condition | Expected behavior | Decided by |
|---|---|---|---|

## Explicitly out of scope
| Not doing | Why | Who agreed |
|---|---|---|

## Constraints
<Platform standards, published contracts, compliance obligations, freeze windows. Distinguish real constraints from suggested designs.>

## Design decisions pushed downstream
| Arrived as | Actual requirement | To be decided by |
|---|---|---|

## Assumptions
| # | Assumption | If wrong | Who can confirm |
|---|---|---|---|

## Open questions
| # | Question | Who can answer | Blocking? | Asked on |
|---|---|---|---|---|

## Confirmation
| Name | Role | Confirmed | Date |
|---|---|---|---|
```

## Common traps

**Paraphrasing the ask.** The original wording carries the ambiguity. Keep it verbatim, then interpret separately.

**Skipping the out-of-scope section.** One line now; days of argument later.

**Criteria that aren't observable.** "Handles errors gracefully" cannot be tested and will be disputed. Name the error, name the behavior.

**Ignoring the unhappy paths.** That's where the ambiguity is concentrated, and where code will otherwise decide for you.

**Accepting a design as a requirement.** Ask what it's for. Sometimes it's a real constraint; sometimes it's a preference that would lose a fair comparison.

**Hiding assumptions at the bottom.** If it changes the work when wrong, put it where a skimming stakeholder sees it.

**Specifying alone.** A spec nobody confirmed is your interpretation. That's fine to proceed on — say so in the Confidence line rather than letting it read as agreed.

**Estimating here.** This skill produces the spec. `feasibility-probe` grounds it in code and `estimation` sizes it. An estimate written before the code has been looked at is a number people will hold you to.
