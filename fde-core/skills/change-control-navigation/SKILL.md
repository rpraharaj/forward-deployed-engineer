---
name: change-control-navigation
description: Find and work with the organization's change process before it blocks you - which gates apply, what evidence each requires, submission deadlines, freeze periods, release calendars, and segregation of duties - then work backwards from the release window. Use early in any engagement that will reach production, when a CAB or stage gate exists, when a release calendar or freeze period constrains the plan, or when work is technically complete and cannot ship. Discovering the process at go-live is a self-inflicted slip.
---

# Change control navigation

The process between "it works" and "it's live."

## Why this exists

In a large organization, technically complete and deployable are separated by a process: a change advisory board, a stage gate, a release calendar, a freeze window, mandatory lead times, and often segregation of duties meaning the person who wrote the change may not deploy it.

Engineers routinely treat this as bureaucracy to be endured at the end. That's the expensive reading. The process has **lead times**, and lead times only work if you start them early. A change completed on Monday that needs ten working days' notice for a fortnightly board doesn't ship this month.

An FDE is unusually exposed. You don't know this organization's process, it isn't written anywhere useful, and everyone around you has internalized it so thoroughly they won't think to mention it.

The good news: it's discoverable in about an hour, and knowing it early is close to free.

## When this applies

- Any engagement whose work will reach production
- A CAB, stage gate, or formal approval exists
- A release calendar or freeze period constrains the plan
- Work is complete and can't ship
- Planning — this belongs in `delivery-plan`, not after it

## When it doesn't

- Nothing reaching production this engagement
- A mature continuous-delivery pipeline where the process is the pipeline. Confirm that's genuinely true rather than assuming it.
- Executing an emergency change during an incident — follow the emergency path you already recorded; do not discover process under fire. Finding that path *before* you need it is part of this skill.

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

`<workspace>/00-engagement.md`, and `<workspace>/02b-ownership.md` for who holds each gate.

## Procedure

### 1. Find out what applies, by asking

This is not usually discoverable from the repository. It's a conversation, and it's a good early use of a `knowledge-interview` slot — or simply a direct question to a release manager or delivery lead.

This is usually a conversation. If no one is available, **do not stall** — reconstruct a first draft from the repo and tag it `[inferred]`:

- The deploy job in CI (who it requires, which branches, which environments)
- `CODEOWNERS` and branch-protection docs
- The last production release PR and any linked change ticket
- Existing runbooks and `CHANGELOG` / release calendar files
- ServiceNow / Jira / Azure Boards templates named `change`, `CAB`, `release`

Then ask to confirm. Ask specifically:

- What does a change like this need before it can go to production?
- Is there a CAB or equivalent? How often does it meet, and what's the submission deadline?
- Are there freeze periods coming up?
- Is there a release calendar or fixed deployment window?
- Can the person who writes a change deploy it?
- Is there a lighter path for low-risk or standard changes?
- What's the emergency path, and who can invoke it?

That last pair matters. Most organizations have a **pre-approved standard change** category — routine, low-risk, repeatable changes that skip the board. Getting your change classified as standard, where it genuinely qualifies, can remove weeks. Almost nobody asks.

### 2. Establish the evidence each gate wants

Gates are usually asking a consistent set of questions, whatever their local vocabulary:

- What's changing, in plain language
- Who's affected, and how many
- What testing was done, and what the result was
- What the rollback is, and whether it's been rehearsed
- What the residual risk is
- Who approved it technically

`release-readiness` produces exactly this. Knowing the format in advance means the artifacts are shaped correctly the first time, rather than being reformatted under deadline pressure.

Ask for a **recent successful submission** as a template. It's the fastest way to learn the house expectations, and people are generally happy to share one.

### 3. Work backwards from the release window

Take the target release date and subtract every lead time:

```
Target release          Thu 18th
CAB approval needed     Tue 16th   (board meets fortnightly)
Submission deadline     Tue 2nd    (10 working days ahead)
Technical sign-off      Fri 28th prev
Verification complete   Wed 26th prev
Code complete           Mon 24th prev
```

The result is frequently uncomfortable and always useful: code complete is often three weeks before the release date. That's the real deadline, and it belongs in `delivery-plan` as the date that matters.

### 4. Check the calendar for freezes

Freeze periods are the most common cause of a plan collapsing late. They cluster around: quarter and year end, peak trading periods, major organizational events, holiday coverage gaps, and other major releases.

Find them now and plan around them. A freeze discovered in week five converts a two-week slip into a six-week one.

### 5. Get classified correctly, early

Change classification — standard, normal, emergency; or low, medium, high risk — determines which path applies, and the difference between paths is often weeks.

Classification is usually driven by blast radius, which `blast-radius` has already established with evidence. That artifact is the argument. A change with a rehearsed rollback, no schema change, and internal-only consumers has a genuine case for the lighter path, and evidence makes the case persuasive rather than pleading.

**Don't misrepresent risk to get a lighter path.** It works once, and it ends the relationship with the people who let it through.

### 6. Identify who acts, given segregation of duties

In many regulated organizations the author cannot deploy. That changes several things: the runbook is written for someone else (which `deploy-runbook` already assumes), the deployer must be available in the window, and they may need a walkthrough beforehand.

Establish this early. Discovering on release day that you can't press the button, and the person who can is on leave, is a preventable and quite common failure.

### 7. Record it, because it applies to every future change

Write it down once. It's stable, it applies to every subsequent change in the engagement, and it's one of the more useful things in a handover — most teams have never written their own process down.

## Output template

Write to `<workspace>/08b-change-control.md`:

```markdown
# Change control

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA> · **Source:** <who told you, when>
**Confidence:** <confirmed with a release manager vs. inferred from CI / last release PR>

## Applicable path
**Classification:** normal change *(pursuing reclassification to standard — see below)*

| Gate | Who | Cadence | Deadline | Evidence needed |
|---|---|---|---|---|
| Technical sign-off | Owning team lead | ad hoc | — | PR approval |
| Security review | Security | 3 weeks' notice | — | Data classification |
| CAB | Change board | fortnightly, Tue | 10 working days prior | Submission pack |
| Release window | Release mgmt | Thursdays | 24h notice | Runbook |

## Backwards schedule
| Milestone | Date | Note |
|---|---|---|
| Target release | Thu 18 | |
| CAB approval | Tue 16 | |
| **CAB submission** | **Tue 2** | Hard deadline — miss it and the next board is 2 weeks later |
| Technical sign-off | Fri 28 prev | |
| **Code complete** | **Mon 24 prev** | The real deadline |

## Freezes
| Period | Dates | Effect |
|---|---|---|
| Quarter end | <dates> | No non-emergency changes |

## Segregation of duties
**Author may deploy:** no
**Who deploys:** release engineer, on rota
**Implication:** runbook written for a stranger; confirm availability in the window

## Classification argument
<Why this change qualifies for a lighter path, citing blast-radius evidence. Or why it doesn't.>

## Emergency path
**When invocable:** <criteria> · **Who authorizes:** <role> · **Retrospective approval:** <required within X>

## Templates
<Link or path to a recent successful submission.>
```

## Common traps

**Finding out at the end.** The single most common cause of a late slip, and entirely preventable.

**Not asking about the standard-change path.** It exists in most organizations and can remove weeks. Almost nobody asks.

**Not checking for freezes.** Converts a two-week slip into a six-week one.

**Treating the release date as the deadline.** Code complete is often three weeks earlier. That's the date the plan needs.

**Assuming you can deploy.** Segregation of duties is common in regulated organizations, and discovering it on release day is preventable.

**Understating risk to get a lighter path.** Works once, and permanently.

**Writing the submission from scratch.** Ask for a recent successful one. Faster, and it matches house expectations.

**Not recording it.** It applies to every subsequent change and is one of the more useful things you can leave behind.
