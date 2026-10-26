---
name: knowledge-interview
description: Extract what only a person knows - structured preparation and questioning for a short session with a long-tenured engineer, system owner, or business expert, then conversion of what you learn into cited artifacts. Use before or after meeting someone who knows a system you do not, when the code cannot answer a question, when preparing for a handover conversation, when you have limited time with a busy expert, or when you keep hitting unverified gaps that only a human can close. Covers how to distinguish what someone knows from what they assume.
---

# Knowledge interview

Getting what isn't written down.

## Why this exists

The most valuable source in a legacy organization is a person who has been there nine years. They know why the retry count is three, which customer the special case exists for, what broke in 2021, and which of the four services named `payments-*` actually processes payments. None of it is written down, and much of it cannot be derived from the code at any cost.

You will get forty minutes of their time, probably once.

The default failure is going in with a vague "can you walk me through the system?" and getting a forty-minute monologue that is genuinely interesting and answers none of your actual questions. The second failure is subtler: treating everything they say as fact. People misremember, describe intended rather than actual behavior, and confidently explain systems that changed underneath them two years ago.

## When this applies

- Before or after meeting someone who knows a system you don't
- Repeated `[unverified]` gaps that only a person can close
- Handover conversations, in either direction
- Business rules with no written source
- Limited time with a busy expert

## When it doesn't

- The code answers it — read the code, don't spend the person's goodwill
- You need a decision rather than knowledge — that's a different conversation
- Formal requirements gathering with a stakeholder — that's `requirements-to-spec`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/02-system-map.md` and any `[unverified]` gaps from other artifacts — these *are* your question list
- `<workspace>/02b-ownership.md` — so you're asking the right person

## Procedure

### 1. Exhaust the code first

Never spend an expert's time on something you could have grepped. It's the fastest way to be deprioritized, and it wastes the scarcest resource in the engagement.

Go in having read the code. The questions that survive that filter are the good ones — the *whys*, the history, the things not written down.

Signal that you've done the work: *"I traced the refund path as far as the event publish at `OrderService:132` and couldn't find the consumer — is it in another service?"* That question demonstrates preparation, is easy to answer, and gets you a better forty minutes than "how do refunds work?"

### 2. Rank your questions ruthlessly

Assume you'll get through a third of what you plan. Sort by what unblocks the most work.

Three tiers:

- **Must** — blocking, and only this person can answer. Usually two or three.
- **Should** — valuable, could eventually be derived at cost
- **Nice** — context and background

Lead with the Musts. Do not save the important question for the end; the meeting will overrun, someone will join late, or they'll be pulled away.

### 3. Ask questions that produce specifics

The phrasing does most of the work.

| Weak | Better |
|---|---|
| "How does the payment system work?" | "What happens when a payment times out mid-authorization?" |
| "Is there anything I should know?" | "What's broken about this that everyone has learned to work around?" |
| "Is this code still used?" | "When did you last see this path run in production?" |
| "Are there any gotchas?" | "What's the last thing that broke in this area, and why?" |
| "Who owns this?" | "If I break this at 2am, whose phone rings?" |

Four questions worth asking almost every time, because they reliably surface things nobody thinks to mention:

1. **"What would you tell someone who's about to change this?"** — surfaces landmines directly
2. **"What's here for a reason nobody remembers?"** — Chesterton's Fences, named
3. **"What did the last person who tried this get wrong?"** — rescue engagements especially
4. **"What are you worried about that nobody's asking you about?"** — frequently the single most valuable answer of the session

### 4. Separate knowledge from assumption, live

The critical discipline, and the reason this is a skill rather than a meeting.

People state three different things in the same confident tone: what they *know*, what they *believe*, and what they *designed and assume still holds*. That third category is the dangerous one, because the person is genuinely authoritative and genuinely out of date.

Probe gently, and make it about the record rather than about them:

- "Have you seen that recently, or is that how it was designed?"
- "Would that still be true after the migration last year?"
- "Is that documented somewhere, or is that from memory?"

Nobody minds these questions when framed as diligence. Tag accordingly: what they've observed recently is `[inferred]` until you check the code; what they designed years ago is `[unverified]`.

**Then verify the load-bearing ones against the code afterwards.** An expert's recollection is a strong hypothesis, not a citation.

### 5. Capture as you go, and read back

Take notes during, not after — you will lose specifics within the hour, and the specifics are the value.

Read back the two or three most important points before the session ends: *"So if I change the event schema, the reconciliation job breaks because it parses positionally — have I got that right?"*

This catches misunderstandings while they're free to fix, and it's the highest-value ninety seconds in the meeting.

### 6. Convert into artifacts, with attribution

Findings go into the relevant artifact — system map, trace, feasibility, ownership — not into a notes file nobody reads again. A finding that stays in your notes has the same durability problem as one that stays in a chat transcript.

Attribute with a person+date citation, and tag confidence honestly. A person is never `[confirmed]` — that tag is for code you read or behavior you ran (`../_shared/evidence-discipline.md`).

- What they observed recently: `[inferred: per J. Okafor, platform team, 2026-03-14]` until you check the code
- What they designed years ago: `[unverified: per J. Okafor, 2026-03-14 — confirm against current code]`

An FDE who presents a nine-year veteran's knowledge as their own discovery is noticed immediately and doesn't recover from it.

### 7. Close the loop

Send back what you wrote, briefly. *"Here's what I captured — correct me on anything I got wrong."*

Costs you five minutes. It catches errors, it demonstrates that their time produced something, and it makes the second conversation far easier to get — which matters, because you will need one.

**Record facts and decision rights, never opinions about colleagues.** You'll hear candid commentary. None of it belongs in a durable document that outlives the engagement. See `../_shared/workspace-conventions.md`.

## Output template

Findings go into existing artifacts. Keep a session record at `<workspace>/interviews/<date>-<person>.md`:

```markdown
# Interview — <name>, <role>

**Date:** <YYYY-MM-DD> · **Duration:** <n> min
**Their relationship to the system:** <built it / maintains it / consumes it / inherited it>
**Prepared from:** <gaps in which artifacts>
**Engagement:** <name>
**Author:** FDE
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"
**Confidence:** <what is confirmed, inferred, or unverified>

## Must-answer questions
| # | Question | Answer | Confidence | Verified against code? |
|---|---|---|---|---|
| 1 | Who consumes `OrderPlaced`? | Reconciliation job in `finops-batch`, parses positionally | `[inferred: per J. Okafor, 2026-03-14]` | ⏳ pending repo access |
| 2 | Why is retry count 3? | 2021 incident, downstream flapping; 3 was empirical | `[unverified]` until checked | ✅ then `[confirmed: commit 8b21f0]` |

## Volunteered, unprompted
<Often the most valuable section. What they raised that you didn't ask about.>

- Worried the recon job has no alerting — "if it fails on a Friday we find out Monday"

## Landmines named
| What | Where | Why |
|---|---|---|

## Follow-ups
| # | Action | Owner | By |
|---|---|---|---|

## Artifacts updated
- `02-system-map.md` — added reconciliation consumer
- `traces/customer-places-order.md` — hop 8 gap closed

## Read-back confirmed
<What you played back and they agreed to.>
```

## Common traps

**Asking what the code answers.** Wastes the scarcest resource and signals you didn't prepare.

**Open-ended opener.** "Walk me through the system" produces forty interesting minutes that answer nothing.

**Saving the important question for last.** The meeting will overrun. Lead with it.

**Treating recollection as fact.** People describe intended behavior, and systems change underneath their model. Verify the load-bearing claims.

**Not distinguishing observed from designed.** The most dangerous input: authoritative, sincere, and years out of date.

**No read-back.** Misunderstandings are free to fix in the room and expensive later.

**Notes that never become artifacts.** Same durability failure as leaving it in a chat transcript.

**Not attributing.** Inaccurate, and it's noticed.

**Recording opinions about people.** You'll hear them. They don't go in a document that outlives you.
