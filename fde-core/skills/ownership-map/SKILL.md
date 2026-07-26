---
name: ownership-map
description: Work out who owns what and who decides, from evidence rather than the org chart - CODEOWNERS, commit authorship over time, review patterns, ticket references, and directory-level activity - distinguishing who wrote the code from who maintains it now. Use before asking anyone for anything, before opening a PR in an unfamiliar repo, when you need a reviewer or an approver, when nobody seems to own a component, or when a change crosses a team boundary. An FDE's technical work most often dies for organizational reasons, and this is the map that prevents it.
---

# Ownership map

Who to ask, who to tell, and who can say yes.

## Why this exists

The most common way an FDE's work fails is not technical. It is a correct change that never merges, because the reviewer who needed to see it was never identified, or the team that owns the downstream consumer heard about it in the release notes.

Knowing *who* is as load-bearing as knowing *what*. And the org chart won't tell you — it shows reporting lines, not the person who actually knows the batch job, or the one whose approval is treated as decisive regardless of title.

The repository will tell you, though. Commit history, review patterns, and directory activity are evidence, and unlike the org chart they reflect what is currently true.

## When this applies

- Before asking anyone for anything substantial
- You need a reviewer, an approver, or an answer
- A change crosses a team boundary
- Nobody seems to own a component
- Preparing for `knowledge-interview` — this tells you whom to interview

## When it doesn't

- You already know the team and its decision paths
- Solo repository with one obvious owner
- The question is about a business decision rather than a system — that's stakeholder territory, in the charter

## Prerequisites

`.fde/00-engagement.md`, and `.fde/02-system-map.md` if it exists — you map ownership *of* components, so it helps to know what they are.

## Procedure

### 1. Read the declared ownership first

```bash
find . -name "CODEOWNERS" -o -name "OWNERS" -o -name ".github/CODEOWNERS" 2>/dev/null
cat CODEOWNERS .github/CODEOWNERS 2>/dev/null
```

Also check for a service catalogue (`catalog-info.yaml` for Backstage), a `docs/owners.md`, or team metadata in the CI config.

Treat all of it as a **hypothesis**. Declared ownership goes stale faster than almost any other documentation — teams reorganize, people leave, and nobody updates the file. Verify it against activity before relying on it.

### 2. Derive actual ownership from history

The strongest signal, and it's free.

```bash
# Who has been active in this area recently? Recency matters more than volume.
git log --format="%an" --since="12 months ago" -- <path> | sort | uniq -c | sort -rn | head -10

# Original authorship, which is a different question
git log --format="%an" --reverse -- <path> | head -5

# Who reviews, if trailers are used
git log --format="%b" --since="12 months ago" -- <path> | grep -iE "reviewed-by|approved-by" | sort | uniq -c | sort -rn | head
```

**Distinguish three roles, because they're usually different people:**

- **Original author** — often gone, and their absence is itself important
- **Current maintainer** — recent commits. This is who you actually need.
- **Occasional contributor** — drive-by fixes. Not an owner; don't route decisions here.

Recency beats volume. Someone with four hundred commits ending eighteen months ago is a historical resource, valuable for `git-archaeology` and useless for approving your PR.

### 3. Find the boundaries where ownership changes

Ownership is per-area, not per-repo. Run the authorship query per top-level module and look for where the names change — those boundaries are the real team boundaries, and they're where coordination cost appears.

A module where the top contributor differs from the rest of the repo is owned by another team, whatever the directory structure implies.

### 4. Identify the orphans

Areas with no active contributor at all. These matter disproportionately:

```bash
# Last touch per area
for d in <top-level dirs>; do
  echo "$(git log -1 --format=%ad --date=short -- "$d") $d"
done | sort
```

Orphaned code has no reviewer, no context, and nobody to answer questions. `feasibility-probe` treats this as a deceptive cost for exactly that reason — a change there will be slower than its size suggests, and getting it merged is a political problem, not a technical one.

Flag orphans early. Finding a reviewer for unowned code takes days, not hours.

### 5. Establish decision rights, not just knowledge

Knowing who understands a system is different from knowing who can approve a change to it. Establish, for the areas you'll touch:

- **Who must review** — enforced by branch protection, or by convention
- **Who can approve an exception** — to a standard, a freeze, a policy
- **Who is consulted vs. informed** — getting this backwards is a reliable way to create an enemy
- **Whose objection stops things**, regardless of title. Every organization has someone like this, and they are rarely on the approval list.

Much of this isn't in the repository. It comes from asking — and "who normally reviews changes here?" is an easy, low-cost question that people answer readily.

### 6. Record how to reach them, and the etiquette

Practical and frequently the difference between a two-hour answer and a two-week one: preferred channel, timezone, whether they prefer a ticket or a direct message, and whether they want to be asked before a PR appears or after.

Teams differ sharply on that last point. A PR arriving unannounced in a repository whose team expects a conversation first reads as presumptuous, and you only get to make that mistake once per team.

## Output template

Write to `.fde/02b-ownership.md`:

```markdown
# Ownership map

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Confidence:** <derived from history vs. confirmed with people>

## By component

| Component | Declared owner | Active maintainer | Last activity | Confidence |
|---|---|---|---|---|
| `services/billing` | Team Payments (CODEOWNERS) | J. Okafor, 34 commits/12mo | 3 days ago | confirmed |
| `jobs/reconciliation` | — | **none** — last commit 19 months | 19 months | **orphan** |

## Orphans
| Area | Last touched | Last author | Still in use? | Risk |
|---|---|---|---|---|
| `jobs/reconciliation` | 19 months | R. Silva (left) | Yes — runs nightly `[confirmed]` | No reviewer, no context |

## Decision rights

| Decision | Who decides | Who's consulted | How |
|---|---|---|---|
| Merge to `main` | 1 CODEOWNER approval | — | Branch protection |
| Schema change | DBA team | Owning team | Ticket, ~3d |
| Production deploy | Release manager | On-call | CAB for non-standard |

## People

| Name | Role | Owns | Contact | Notes |
|---|---|---|---|---|
| J. Okafor | Senior eng | billing | Slack `#payments`, UTC+1 | Prefers a heads-up before a PR |

## Historical resources
<People no longer active but who hold context. Valuable for git-archaeology and knowledge-interview.>

## Gaps
<Components where ownership couldn't be established, and what would resolve it.>
```

## Common traps

**Trusting CODEOWNERS.** It's a hypothesis. Verify against recent activity.

**Using the org chart.** It shows reporting lines, not who knows the batch job.

**Confusing the author with the maintainer.** The person who wrote it is often gone; the person who fixes it is who you need.

**Ranking by commit volume.** Recency matters more. Four hundred commits ending eighteen months ago is a historical resource.

**Missing the orphans.** They're the highest-risk areas and the slowest changes, and they look like any other directory.

**Confusing knowledge with authority.** The person who understands it best often can't approve it, and vice versa.

**Getting consulted and informed backwards.** Informing someone who expected to be consulted creates an enemy cheaply.

**Ignoring etiquette.** A PR that arrives unannounced in a team that expects a conversation first is a bad first impression you don't get to retake.
