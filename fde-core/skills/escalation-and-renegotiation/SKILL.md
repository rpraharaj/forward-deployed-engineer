---
name: escalation-and-renegotiation
description: Raise a problem early with evidence and a recommendation, or reopen scope without losing credibility - when the plan is no longer achievable, a dependency is not moving, the requirement turns out to be wrong, or you are being asked to commit to something you believe is not deliverable. Use as soon as you know, not when you are certain, and use when a blocker has passed its expected date. This is the conversation and the decision record. For anyone above tech lead, write it as a stakeholder-brief - that skill is the vehicle, this skill is the decision.
---

# Escalation and renegotiation

Saying the difficult thing, early, in a way that gets acted on.

## Why this exists

This is the hardest thing an FDE does, and the most consequential. Engagements are rarely judged on code quality. They're judged on whether the people paying for them felt informed and in control — and that is decided almost entirely by how you handle the moment when things stop going to plan.

Two failure modes, both common:

**Waiting until certain.** The instinct is to raise a problem only once you fully understand it and have a solution. By then the options that existed at first suspicion — re-scoping, adding help, resetting expectations while there's still time — have expired. The delivery lead loses those options without ever knowing they had them, and *that* is what damages trust, far more than the problem itself.

**Escalating without evidence or a recommendation.** Arriving with a problem and no analysis reads as complaining, and it transfers work to someone with less context than you.

The FDE's position makes both harder. You have no track record, you're often perceived as expensive, and you may be raising a problem the permanent team has already learned to live with.

## When this applies

- The plan is no longer achievable
- A dependency has passed its expected date
- A requirement turns out to be wrong or unbuildable as specified
- You're being asked to commit to something you don't believe is deliverable
- A quality or safety concern is being deprioritized
- **As soon as you suspect** — not when you're certain

## When it doesn't

- Normal in-flight variance you can absorb without affecting anything visible
- A technical decision within your remit — make it, record it in an ADR
- You haven't yet done the work to establish what's true. Spend an hour on that first; arriving with evidence is the whole difference.
- A routine status update with no decision needed — that's `stakeholder-brief`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/00-engagement.md` — who can actually decide
- The artifact that holds the evidence (`04-feasibility.md`, `05b-estimate.md`, `00b-access.md`, …)
- `../_shared/comms-register.md` before writing to anyone above tech lead

If those files are missing, spend the hour gathering evidence first. Do not escalate from an empty workspace.

## Procedure

### 1. Establish what's actually true before raising it

An hour of grounding transforms the conversation. Not weeks — an hour.

Get to: what specifically is blocked or wrong, what it affects, what you've already tried, and what the options are. Cite the artifacts. The difference between *"I'm worried R2 might be bigger than we thought"* and *"R2 touches a contract with four consumers, one of whom hasn't responded in two weeks — that's the whole slip"* is the difference between being managed and being believed.

### 2. Raise it at first suspicion, not at certainty

The timing rule that matters most: **communicate the suspicion, labelled as a suspicion.**

> "Early signal, not confirmed — R2 may be materially bigger than estimated. I'll know by Thursday. Flagging now because if it is, we'd want to decide about scope before the CAB deadline on Tuesday."

That message costs nothing if the suspicion is wrong, and preserves every option if it's right. It also establishes something valuable: that you tell people things early. After a few of these, your assessments get believed quickly, which is worth a great deal in an organization where you have no history.

Being wrong occasionally is the price, and it's cheap. Nobody remembers the flag that came to nothing; everyone remembers the one that came too late.

### 3. Bring options, not a problem

Always arrive with at least two paths, with consequences attached. The standard levers:

| Lever | What it costs |
|---|---|
| **Reduce scope** | Something doesn't get built. Name which, and what's lost. |
| **Move the date** | Downstream commitments shift. Name them. |
| **Add people** | Rarely helps quickly, and costs the existing team's time. Say so honestly. |
| **Defer non-mandatory work** | Name the tests or checks deferred, the uncovered behavior, and the risk owner. Required controls and must-have criteria remain gates unless their authorized owner grants a permitted exception. |
| **Remove the blocker** | Escalate the dependency, buy access, get a decision made faster. |
| **Change approach** | A cheaper design that meets the real need. Usually the best option and the least considered. |

Recommend one. A menu with no recommendation hands the work back to someone with less context.

**Reducing scope is usually the strongest option**, and the one engineers propose least. Go back to `requirements-to-spec` — the underlying need is frequently satisfiable by less than the stated ask.

### 4. Pitch it to what the person controls

Escalate to the person who can actually decide. A delivery lead can move a date; only a sponsor can cut scope; only a functional head can unblock another team.

Escalating to someone without the authority produces sympathy and no change, and it burns the escalation — the second one is harder.

Use `../_shared/comms-register.md` to pitch it correctly. For anyone above tech lead: recommendation first, then facts, then detail.

### 5. Keep it about the work

The framing rule. Facts about the situation, never characterizations of people.

> Weak: *"Team D has been unresponsive and it's blocking us."*
>
> Better: *"We asked Team D on 12 March to confirm contract compatibility and haven't had a response after two follow-ups. It's the last open item on R2. Could you help us get an answer this week?"*

The second is more likely to work, doesn't create an enemy, and is more credible precisely because it's specific and unemotional. As an outsider you have very little margin here — a blame-shaped escalation confirms whatever suspicion exists about why you were brought in.

### 6. Record what was decided

Briefly and without defensiveness, in the engagement log or a brief.

Two reasons. Decisions made verbally get remembered differently by different people, especially the ones about accepted risk. And when a risk that was knowingly accepted materializes, the fact that it was knowingly accepted is the most important fact in the room — not to protect yourself, but because a decision made with full information is a completely different thing from a failure of information, and the retrospective should know which it was.

Record it as fact, never as evidence. The moment it reads defensive, it costs more than it protects.

### 7. If overridden, proceed properly

Sometimes you'll be told to continue anyway. First establish whether the person has authority to accept this particular risk; delivery authority does not automatically include authority over security, safety, or data protection controls.

Note the decision and who made it, then commit to the chosen path properly. Half-hearted execution of a decision you disagreed with is worse than either alternative, and visibly so.

For safety, legal, data protection, or other mandatory controls, pause the affected action and escalate to the relevant control owner. Proceed only when the concern is resolved or that owner grants an exception permitted by policy, with scope, conditions, and expiry recorded. If an exception is prohibited or authority is unclear, do not carry out the affected action. Continue independent work that does not cross that boundary.

## Output template

Usually a conversation, backed by a short written record. Use `stakeholder-brief` format, or log in `<workspace>/00-engagement.md`:

```markdown
## Escalation — <date>

**Raised with:** <name, role>
**Status when raised:** suspicion | confirmed
**Issue:** <one sentence>
**Evidence:** <citations to artifacts>
**Affects:** <what specifically — dates, scope, risk>

**Options presented:**
| # | Option | Consequence | Recommended |
|---|---|---|---|
| 1 | Move reporting requirement to phase 2 | Full scope slips ~3 weeks; core ships on time | ✅ |
| 2 | Hold release until all four complete | Whole feature slips to next window (~1 month) | |
| 3 | Ship with manual reporting workaround | Finance does it by hand for ~2 months | |

**Decision:** <what was decided, by whom, when>
**Risk accepted:** <if any, stated plainly>
**Follow-up:** <actions and owners>
```

## Common traps

**Waiting for certainty.** You're spending options that belong to someone else. Raise the suspicion, labelled.

**Escalating without doing the hour of work.** Reads as complaining, and transfers work upward to someone with less context.

**A problem with no options.** Same effect.

**A menu with no recommendation.** You have the most context. Use it.

**Escalating to someone without authority.** Produces sympathy, no change, and makes the next escalation harder.

**Making it about people.** As an outsider you have almost no margin here, and it confirms the worst assumption about why you're there.

**Not proposing scope reduction.** Usually the strongest lever and the least offered.

**Defensive record-keeping.** Record decisions because they matter, not to build a case. The tone is visible immediately.

**Sulking after an override.** Visible, and worse than either the concern or the decision.
