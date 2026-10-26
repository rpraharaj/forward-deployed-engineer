---
name: solution-design
description: Generate genuine alternatives for a non-trivial change - including do-nothing and solve-it-outside-this-system - evaluate them against the real constraints already established, recommend one, and record why the others were rejected, as an ADR that survives your departure. Use when a change has more than one plausible approach, when a design decision arrived pre-made and should be checked, before committing to an architecture, or when someone asks "how should we build this". Do not use for changes with one obvious implementation.
---

# Solution design

Choosing an approach, and recording why.

## Why this exists

Two failure modes, and an FDE is exposed to both.

The first is **the single-option design**: the first workable approach becomes the approach, because it works and time is short. Nobody compared it to anything, so nobody knows if it was good — including you, when it turns out badly in month three.

The second is **the imported default**. An FDE arrives with patterns that worked elsewhere and applies them without checking whether the constraints that made them right still hold. This is the specific way outside expertise goes wrong, and the team can see it happening even when you can't.

The defence for both is the same: generate real alternatives, evaluate against *this* organization's constraints, and write down why you rejected the others. That last part matters most, because the rejected options are what a future engineer needs — otherwise they'll propose one of them in a year, and nobody will remember why it doesn't work.

## When this applies

- More than one plausible approach
- A design decision arrived pre-made in the requirements and deserves checking
- Before committing to an architecture, a contract, or a dependency
- The change is expensive to reverse

## When it doesn't

- One obvious implementation — don't manufacture alternatives for ceremony
- Reversible, local changes
- The decision has genuinely already been made by someone with the authority to make it. Record it as a constraint and move on.

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/03-requirements.md` — what must be true
- `<workspace>/04-feasibility.md` — what the code can actually support, and the alternatives it spotted
- `<workspace>/03b-nfrs.md` if it exists, `<workspace>/02b-ownership.md` for who must agree

## Procedure

### 1. State the decision precisely

One sentence, in the form of a question. "How should refund currency be resolved?" not "Refund currency design."

If you can't state it as a single question, you have several decisions bundled together. Split them — bundled decisions get approved or rejected as a unit, which means the good parts fail with the bad.

### 2. Generate genuinely different options

At least three, and they must differ in *approach*, not in detail. Two variations of the same idea plus a strawman is the most common way this step is faked, and reviewers recognize it.

Always consider these two, because they are frequently right and almost never proposed:

- **Do nothing.** What actually happens if this isn't built? Sometimes the honest answer is "very little," and that is an enormously valuable finding.
- **Solve it outside this system.** A config change, a manual process, a report, a scheduled query, a different team's existing capability. Engineers under-propose this because it isn't engineering, and it is often the cheapest correct answer.

Then the real technical alternatives. Push for one that is *cheaper and worse* and one that is *more expensive and better* — bracketing the recommendation makes the trade-off visible instead of implicit.

### 3. Evaluate against real constraints, not general principles

This is where the artifacts pay off. Judge each option against what you actually established:

- The feasibility findings — which options are cheap given where the code actually is
- The measurable NFRs, not aspirational ones
- Compliance and data-handling obligations
- Who owns what, and how much coordination each option needs
- The team's skills and what they'll maintain after you leave
- Freeze windows and the release calendar

**Maintainability by this team after you leave is a first-class criterion.** An elegant approach the team can't maintain is a worse outcome than a plain one they can. This is the criterion an FDE is most likely to under-weight, because you won't be there to feel the consequences.

### 4. Be explicit about reversibility

Sort the options by how expensive it is to change your mind. A cheap, reversible option that might be wrong frequently beats an expensive, correct-looking one — especially early, when you know least about the organization.

Where an option is a one-way door — a published contract, a data migration, a vendor commitment — say so prominently. One-way doors deserve more analysis than reversible decisions, and reversible ones deserve less than they usually get.

### 5. Recommend one, and say why the others lose

Give a recommendation. A document presenting three options and no view is work handed back to the reader.

For each rejected option, record the *specific* reason. "Too complex" is not a reason and won't help anyone later. "Requires coordinating a schema change across three teams during a Q4 freeze" is.

Note anything worth **grafting** from a rejected option. The winner plus one good idea from a runner-up is often the actual best answer.

### 6. Write it as an ADR

Architecture Decision Record format, because it's widely understood, it ages well, and it's designed for exactly this: the reasoning outliving the people.

Number sequentially, never delete one. When a decision is later reversed, write a new ADR that supersedes it and link both. The trail of superseded decisions is genuinely valuable to whoever inherits the system.

### 7. Circulate before building

Send it to the people `ownership-map` identified. An ADR reviewed before implementation is a design discussion; the same document after implementation is a justification, and everyone can tell the difference.

Where you can't get a response — common — say so in the ADR, note whom you asked and when, and proceed. That's a defensible position. Silently proceeding is not.

## Output template

Write to `<workspace>/adr/NNNN-<slug>.md`:

```markdown
# ADR-NNNN — <decision as a statement>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** proposed | accepted | superseded by ADR-NNNN
**Deciders:** <who agreed, and when>
**Consulted:** <who was asked; note non-responses>
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Decision
<One sentence: what we are doing. State it first — the reader may stop here.>

## Question
<The decision as a single question.>

## Context
<What's true that makes this a decision. Cite the artifacts — feasibility findings, NFRs, constraints. Keep it factual.>

## Options

### A — <name> **← recommended**
<What it is, in two or three sentences.>
**Cost:** <effort, coordination, calendar>
**Reversibility:** <cheap / moderate / one-way door>
**Trade-off:** <what you give up — every option gives something up>

### B — <name>
…
**Rejected because:** <specific and checkable>

### C — Do nothing
**What happens:** <honestly>
**Rejected because:** <or accepted, sometimes>

## Consequences
**Accepted:** <what becomes true, including the bad parts>
**Follow-on work:** <what this creates>
**Revisit if:** <the condition that should reopen this>

## Grafted from rejected options
<Good ideas kept from options that lost overall.>
```

## Common traps

**One real option and two strawmen.** Reviewers see it immediately, and it costs credibility for no benefit.

**Never considering do-nothing.** Sometimes it wins, and it always calibrates the others.

**Never considering outside-the-system.** Engineers under-propose the config change, the manual process, the scheduled report. Often the cheapest correct answer.

**Importing a pattern that worked elsewhere.** Check whether the constraints that made it right still hold. This is the characteristic way outside expertise goes wrong.

**Judging against general principles instead of this system's constraints.** "Microservices scale better" is not an argument about your situation.

**Under-weighting maintainability by the team you're leaving behind.** The criterion you'll never personally feel.

**Treating all decisions as equally weighty.** One-way doors deserve real analysis; reversible decisions deserve a decision.

**"Too complex" as a rejection reason.** Unhelpful to everyone, including you in six months.

**Writing the ADR after building.** Then it's a justification, and it reads like one.
