---
name: access-and-onboarding
description: Turn getting access into a tracked critical path instead of a passive wait. Enumerate every credential, permission, environment, and account the engagement needs, identify who approves each and its lead time, request long-lead items first, find workarounds for what is blocked, and keep a queue of useful work that does not depend on the blocker. Use in the first days at a new organization, whenever you are blocked on permissions, VPN, repository access, database grants, pipeline rights, or environment credentials, or when someone says "I'm still waiting for access". Use for access and permissions, not a failing login in application code and not a CAB that will not approve a deploy.
---

# Access and onboarding

The most reliably underestimated part of an enterprise engagement.

## Why this exists

FDEs routinely lose one to two weeks to access. Not because approvals are slow in aggregate, but because they're discovered **serially**: you request repository access, wait three days, get it, discover you also need the artifact registry, wait four more days, get it, then find the database grant needs a manager's signature and a ticket in a system you don't have an account for.

The lead times aren't the problem. Discovering them one at a time is. Requested in parallel on day one, the same set often lands in under a week.

This skill front-loads the discovery, so the waiting overlaps instead of stacking.

## When this applies

- First days at a new organization or on a new system
- Blocked on any permission, credential, or environment
- An engagement is about to widen into systems you don't yet have access to
- You notice you're waiting on something and don't know who to chase

## When it doesn't

- You already have everything you need — don't manufacture a register for a one-day task
- The blocker is a person's time rather than a permission. That's `escalation-and-renegotiation`.

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

`<workspace>/00-engagement.md` — the archetype determines what access is actually needed. Without it, you'll request either too much (which slows every approval and makes you look careless with privilege) or too little.

## Procedure

### 1. Enumerate what this engagement needs

Work from the candidate list below. It's deliberately over-inclusive — go through it and mark each **needed / not needed / unsure**, using the archetype as the filter.

Ask for the least privilege that does the job. Requesting production write access on day one, when read-only would do, slows the approval and tells a security team something about your judgment that you'd rather not tell them.

**Foundation**
- Network access — VPN, or the office network, or a jump host / VDI
- SSO or directory account, and any MFA enrolment
- Corporate email and chat, plus the specific team channels
- Laptop or VDI itself, with whatever developer entitlement it needs

**Source and build**
- Source control read, on every repo the change touches — usually more than one
- Source control write or fork rights, plus the branch protection rules that apply
- CI/CD: view builds, trigger builds, view secrets *(names, not values)*
- Artifact registry read; publish rights only if you'll release
- Any pre-commit or quality gate that needs an account (Sonar, licence scanning)

**Runtime and data**
- Environments: which of dev / test / staging / pre-prod / prod, and read vs. deploy
- Database access per environment, read-only first
- Secrets manager or vault — paths, not values
- Cloud console, scoped to the relevant subscription or project
- Monitoring, APM, and log aggregation — often overlooked, and the fastest way to understand a live system
- Message brokers, queues, or event streams
- Feature flag console

**Organizational**
- Ticket system, on the right project and board
- Wiki / Confluence / SharePoint, on the right space
- Architecture or service catalogue (Backstage or equivalent)
- Change management tooling, if you'll take anything to a CAB
- On-call or paging tooling, if you'll be in the rotation
- Vendor or partner portals, for COTS and integration engagements

**Human**
- Introduction to the system owners named in `02b-ownership.md`
- A named onboarding buddy — worth asking for explicitly, and rarely refused
- Standing invitations to the ceremonies where decisions actually get made

### 2. For each item, find the approver and the lead time

This is the step that pays for the skill. For every needed item, establish:

- **Who approves it** — a named person or a specific role, not "IT"
- **How it's requested** — self-service portal, ticket type, email, a form
- **Typical lead time** — ask someone who's been through it; new joiners in the team are the best source because they did it recently
- **Prerequisites** — many requests require a manager's approval, a completed training module, or another access that must land first

Chained prerequisites are what turn a three-day wait into three weeks. Look for them specifically.

### 3. Sequence by lead time, not by need date

Request long-lead items **first**, even when you won't need them for weeks. A production database grant needing two approvals and a compliance training module should be in flight on day one, not the day before you need it.

Order the register by `lead time` descending, and submit in that order.

### 4. Find the workaround for anything blocked

Blocked access rarely blocks all the work behind it. For each blocker, spend two minutes on the question: *what would give me eighty percent of this?*

| Blocked on | Frequently available instead |
|---|---|
| Production database | Read replica, staging with representative data, or a saved query someone runs for you |
| Prod deploy rights | Pair with someone who has them — often faster than the approval, and better for the relationship |
| A repository | A colleague's local clone, an artifact with sources attached, or the mirror in the registry |
| Monitoring console | Exported dashboards, or asking someone to screenshot the panel |
| Real data | Synthesized fixtures — see `test-data-strategy` |
| Environment access | A recorded walkthrough from someone who has it |

Record the workaround *and* keep the request open. Workarounds are how you keep moving; they are not a substitute, and quietly abandoning the request means you hit the same wall harder later.

### 5. Keep a queue of unblocked work

Maintain, visibly, the list of things you can do right now that don't depend on any pending request. See `../_shared/enterprise-constraints.md`. Reading available source, drafting the spec, preparing interview questions, and building this register itself are almost always available.

The point is partly practical and partly reputational: an FDE visibly productive during week one's access limbo is judged very differently from one who spent it waiting.

### 6. Track, and escalate on the date

Give every pending request an **expected-by date**. When it passes, chase — once, politely, to the named approver, with the request reference.

A blocker without a date is invisible and drifts indefinitely. A blocker with a date, an owner, and a record of two chases is a fact you can escalate with, and it makes the eventual conversation about a slipped timeline a matter of record rather than opinion.

**Stop for today** when every *needed* item has an approver, a request path, a request reference or a reason it cannot be filed yet, and an expected-by date. Granted is not the stop — requested-and-tracked is.

If `00-engagement.md` is missing, offer `fde-orient` first. Without the archetype you will request too much or too little.

## Output template

Write to `<workspace>/00b-access.md`:

```markdown
# Access register

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** live *(update as items land)*
**Confidence:** <what's confirmed granted vs. believed pending>
**Source revision:** <repo>@<short SHA>, or "no repository yet"

## Summary
- **Granted:** <n> · **Pending:** <n> · **Blocked:** <n> · **Not needed:** <n>
- **Critical path:** <the item whose lead time currently gates the engagement>

## Register

| # | Access | Why needed | Status | Approver | Request ref | Requested | Expected | Lead time | Workaround |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Repo read: `billing-service` | Primary system | granted | J. Okafor | JIRA-102 | 03-02 | 03-04 | 2d | — |
| 2 | Prod DB read-only | Verify data shape | pending | DBA team | DBA-441 | 03-02 | 03-12 | ~10d | Staging replica, stale by 24h |
| 3 | Deploy rights, staging | Test the release path | blocked | Platform lead | — | 03-03 | — | — | Pair with T. Nakamura |

**Status:** `granted` · `pending` · `blocked` · `not needed` · `workaround in use`

## Chained prerequisites
<Requests that can't start until something else lands. These drive the critical path.>

## Unblocked work queue
<What can proceed right now, in priority order.>

## Chase log
| Date | Item | Action | Outcome |
|---|---|---|---|
```

## Common traps

**Requesting access serially.** The single most costly habit. Enumerate everything up front, submit in parallel, ordered by lead time.

**Requesting more privilege than you need.** Slows approvals, and a security reviewer who sees an unjustified prod-write request treats everything else you ask for with more suspicion.

**Treating "waiting for access" as a status.** It isn't. The status is: what you requested, from whom, when, when it's expected, what you're doing meanwhile.

**Not writing down who approved what.** You'll need the same access again in another environment, and the second request is trivial if you know who granted the first.

**Missing chained prerequisites.** A request that silently depends on a training module you haven't started doesn't queue — it sits at zero progress while you assume it's moving.

**Letting the workaround become permanent.** Verifying against a stale replica for six weeks and forgetting you never got the real thing is how an `[unverified]` claim quietly becomes a stated fact.

**Forgetting that access is also social.** Being introduced to the person who owns a system is frequently worth more than the permission itself, and has a lead time of about one message.
