# Communication register

The same facts need different framing for different readers. Used by `stakeholder-brief`, `release-readiness`, `escalation-and-renegotiation`, and any artifact that leaves the engineering team.

## Why register matters more for an FDE

You have no track record in this organization. Nobody knows yet whether to trust your judgment, so they are calibrating on *how you communicate* as a proxy — usually unconsciously. Writing to an executive the way you'd write to an engineer reads as poor judgment about their time; writing to an engineer the way you'd write to an executive reads as evasive, and engineers are the people who have to work with you daily.

## The four readers

### Engineer / peer

**Wants:** what specifically, where in the code, what breaks.
**Give them:** file paths and line numbers, the actual error, the reasoning. Detail is respect here — vagueness reads as not having done the work.
**Never:** summarize away the specifics. "There's a concurrency issue in the payment path" is useless; the class, the method, and the interleaving are the message.

### Tech lead / architect

**Wants:** the options you considered, the trade-off, why this one.
**Give them:** the alternatives *including* the ones you rejected and why. This is the reader who most values seeing your reasoning, because they're deciding whether to trust your future judgment unsupervised.
**Never:** present one option as though it were the only one. It reads as not having looked.

### Engineering manager / delivery lead

**Wants:** what it means for the plan, the people, and the date.
**Give them:** impact on sequence and dependencies, what you need from whom, and the decision you're asking for. Lead with the change since last time.
**Never:** bury the schedule impact under the technical explanation. If the date moved, that's the first sentence.

### Executive sponsor / change board

**Wants:** the decision, the risk, and the cost of being wrong.
**Give them:** ninety seconds of reading. Recommendation first, then the two or three facts supporting it, then the residual risk in plain language.
**Never:** technical detail they can't act on, unquantified risk ("there's some risk around performance"), or a status with no decision attached.

## The inversion

Engineers build to a conclusion: context, investigation, finding, therefore recommendation. That ordering is correct for a peer and wrong for everyone above them.

For a lead and above, **invert it**: recommendation, then the reasoning, then the detail. Assume the reader stops after the first paragraph — because they will — and make sure that paragraph is sufficient for the decision.

## Quantify or label

"This might affect performance" is not information; it can't be acted on and it can't be checked. Every risk statement should carry either a number or an explicit confidence tag.

> Weak: *There could be some performance impact on the reporting path.*
>
> Better: *Reporting queries will run against a table roughly 4× larger. Current p95 is 1.2s `[confirmed: APM, 30-day]`; I have not measured the post-change figure `[unverified — needs a load test in staging]`.*

The second version is longer and enormously more useful. It also does something the first doesn't: it tells the reader exactly what would resolve the uncertainty, which converts a vague worry into an actionable request.

## Bad news

Deliver it early, in writing, with a recommendation attached.

The instinct is to wait until you have a solution. Resist it — a delivery lead who learns about a two-week slip four weeks late has lost the options they had at week one, and they will remember that far longer than they'd have remembered the slip.

Structure: **what changed → what it means → what I recommend → what I need from you.** No preamble, no apology paragraph. State it, then move to the fix.

## Writing for a change board

CABs read many submissions and are looking for reasons to defer. What they reliably want:

- What is changing, in one sentence a non-specialist understands
- Blast radius: which systems and users, and how many
- Verification evidence: what was tested and what the result was
- Rollback: the procedure, how long it takes, and whether it has been *rehearsed* — not merely written
- Residual risk, stated plainly

The last one is counter-intuitive: naming the residual risk yourself gets changes approved more often than claiming there is none. A submission with no acknowledged risk reads as one where the risk hasn't been looked for. `release-readiness` produces this format directly.

## Attribution

You will present findings derived from other people's explanations. Attribute them — "per the platform team" — for two reasons: it's accurate, and it means the room can correct the record before you build on a misunderstanding. An FDE who claims a long-tenured engineer's knowledge as their own discovery is noticed immediately, and it is very hard to recover from.
