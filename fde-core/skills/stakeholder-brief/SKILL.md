---
name: stakeholder-brief
description: Translate the current technical position into something a busy non-engineer reads in ninety seconds - what changed, what it means, what decision is needed, what the risk is - pitched at the right register for the reader. Use at every phase boundary rather than only at the end, when a sponsor or delivery lead needs an update, when presenting findings from an assessment, or when technical facts need to reach people who will not read the artifacts. Recommendation first, detail second. If the content is "the plan is no longer achievable," run escalation-and-renegotiation and use this format as the vehicle.
---

# Stakeholder brief

Making technical facts usable by people who won't read the artifacts.

## Why this exists

The FDE artifacts are written for engineers: cited, precise, and long. A sponsor will not read them, and shouldn't have to. But sponsors make the decisions that determine whether the work matters — funding it, prioritizing it, accepting the residual risk, approving the release.

So the facts have to travel, and travelling means changing form. Not simplifying to the point of uselessness, and not dumping the technical document with an apologetic summary on top, but genuinely re-writing for a reader whose question is *"what do I need to do about this?"*

There's a second function. An FDE has no track record here, and people calibrate on how you communicate long before they can judge your code. A brief that respects a busy reader's time and states its uncertainty honestly does more for your standing than the work it describes.

## When this applies

- Phase boundaries — after recon, after feasibility, before a release
- A sponsor or delivery lead needs an update
- A decision is needed from outside the team
- Presenting assessment findings
- Bad news. Especially bad news.

## When it doesn't

- Communicating with engineers — give them the artifact, they'd rather have the detail
- Nothing has changed and no decision is needed. A brief with no content trains people to skim the next one.
- A formal change submission — that's `release-readiness`

## Prerequisites

Whichever artifacts hold the current position. Read `../_shared/comms-register.md` before writing — the register for each reader type is the substance of this skill.

## Procedure

### 1. Identify the reader and what they can act on

Different readers need different documents from the same facts. From `../_shared/comms-register.md`:

- **Tech lead / architect** — the options and the trade-off
- **Delivery lead / EM** — impact on plan, people, and date
- **Sponsor / executive** — the decision, the risk, the cost of being wrong

Then ask the sharper question: **what can this person actually do?** A brief that describes a problem the reader has no power over wastes their time and yours. Write toward the decision they can make or the help they can give.

Where several readers need the same facts, write separate short briefs rather than one long one. A merged brief serves nobody.

### 2. Invert the engineering order

Engineers build to a conclusion: context, investigation, finding, therefore recommendation. That's right for a peer and wrong for everyone above them.

**Invert it.** Recommendation first, then the two or three facts supporting it, then detail. Assume the reader stops after the first paragraph — because they will — and make sure that paragraph is enough to act on.

If the first sentence isn't the most important thing you have to say, it's the wrong first sentence.

### 3. Lead with what changed

Busy readers are tracking many things and don't hold your engagement in their head. Open with the delta since they last heard from you, not with a re-statement of context they already have.

Where the date moved, that's the first sentence. Burying schedule impact under technical explanation is read as evasion, whether or not it was.

### 4. Quantify, or label the uncertainty

"There could be some performance impact" is not information. It can't be acted on and it can't be checked.

> Weak: *There may be a performance impact on reporting.*
>
> Better: *Reporting will query a table roughly 4× larger. Current p95 is 1.2s; we haven't measured the post-change figure and can't until we have a load environment.*

The second is longer and far more useful, and it does something the first doesn't: it tells the reader exactly what would resolve the uncertainty. That converts a vague worry into a request they can grant.

Carry the confidence discipline across from the artifacts, but in plain words. "We've confirmed" / "we believe but haven't checked" / "we don't know" reads naturally and preserves the distinction.

### 5. Ask for exactly one thing

Most briefs need a decision, an approval, or help removing a blocker. Name it, name who you need it from, and name when.

Multiple asks dilute each other; a brief with four requests typically gets none of them actioned. If there are genuinely several, rank them and mark which is blocking.

### 6. Deliver bad news early, with a recommendation

The instinct is to wait until you have a solution. Resist it.

A delivery lead who learns about a two-week slip four weeks late has lost every option they had at week one — re-scoping, adding help, resetting expectations upward. They will remember losing those options far longer than they'd have remembered the slip.

Structure: **what changed → what it means → what I recommend → what I need.** No preamble, no apology paragraph. State it and move to the fix.

### 7. Keep it to one screen

A brief that runs to three pages is a report, and it will be skimmed or deferred. If the detail matters, link the artifact — that's what the artifacts are for.

The discipline of fitting one screen also forces you to decide what actually matters, which is most of the value.

## Output template

Write to `.fde/briefs/<date>-<topic>.md`, or send directly:

```markdown
# <Topic> — <date>

**For:** <name, role> · **From:** FDE · **Read time:** ~90 seconds

## Recommendation
<One or two sentences. The decision you're asking for, or the position you're taking. If the reader stops here, this must be enough.>

## What changed
<Since they last heard. Lead with schedule impact if there is any.>

## Why it matters
<Two or three facts. Business terms. Numbers where you have them, honest uncertainty where you don't.>

## What I need from you
<One thing. Who, what, by when.>

## Risk
<The residual risk in plain language, and what would reduce it. Naming it yourself builds more confidence than claiming there is none.>

---
*Detail: `04-feasibility.md`, `06-blast-radius-refund-currency.md`*
```

### Worked example

```markdown
# Multi-currency refunds — feasibility — 26 Mar

**For:** A. Reyes, Delivery Lead · **From:** FDE · **Read time:** ~90 seconds

## Recommendation
Proceed with three of the four requirements now. The fourth — refunds in the daily
finance report — needs data we've never collected, and isn't an engineering problem.
I'd suggest scoping it out of this release and treating it separately.

## What changed
I've now grounded the requirements in the actual code. Three are straightforward
and land where expected. The reporting requirement is a different shape than assumed.

## Why it matters
- Currency data has never been stored on refunds, so there's no history to report on.
  Even after the change, the report would show nothing for past refunds.
- Backfilling isn't possible — the original currency isn't recoverable from what we hold.
- The other three requirements touch 14 files across a path with good test coverage.

## What I need from you
A decision by Friday on whether the reporting requirement moves to a later phase.
It's the only thing blocking a firm plan for the rest.

## Risk
One team (D) consumes the refund API and hasn't responded since 12 Mar. The change is
backward compatible as far as we can tell, but we haven't confirmed with them. If they
have a strict parser, they'd need a coordinated release. Chasing this week.

---
*Detail: `04-feasibility.md`*
```

## Common traps

**Building to the conclusion.** Right for peers, wrong for everyone above them. Invert it.

**Burying schedule impact.** If the date moved, it's the first sentence. Anything else reads as evasion.

**Unquantified risk.** "Some risk around performance" can't be acted on or checked.

**More than one ask.** Four requests typically produce zero actions.

**Waiting for a solution before reporting bad news.** You're spending options that belong to someone else.

**Sending the artifact with a summary on top.** Different document, different reader. Rewrite it.

**Three pages.** It's a report, and it'll be deferred.

**Claiming no risk.** Naming residual risk yourself builds more confidence than claiming there is none — and it's the thing experienced sponsors specifically look for.

**Briefing when nothing changed.** Trains people to skim the one that matters.
