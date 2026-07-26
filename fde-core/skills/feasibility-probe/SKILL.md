---
name: feasibility-probe
description: Ground a specification in the actual codebase - for each requirement establish whether the capability already exists, exactly where a change would land, what shape the change takes, what is missing entirely, and which items look cheap but are not. Use after a spec exists and before anyone estimates, commits to a date, or starts building. Also use when asked "how hard would it be to..." or "can we do X by <date>", when a plan feels optimistic, or when scoping an assessment. This is what turns "we think it's two weeks" into "here are the seven files it touches and the integration nobody owns". Does not produce an estimate - it produces the grounding an estimate needs.
---

# Feasibility probe

The highest-value thing an FDE does.

## Why this exists

Everyone in the organization can write a spec. Almost nobody can tell you, in hours rather than weeks, what that spec means against the real code. That gap is where estimation failures come from — not from bad arithmetic, but from sizing work nobody had looked at.

The characteristic failure isn't the requirement that looks hard and is. It's the one that looks trivial: a field added to a response, which turns out to flow through a shared DTO used by four teams, a published contract with external consumers, and a batch job that parses the payload positionally. Nobody estimated that because nobody looked.

This skill looks. It is deliberately **bounded** — hours, not weeks — because its value is being fast enough to change the plan before the plan hardens.

## When this applies

- A spec exists and someone is about to size it
- "How hard would it be to…?"
- A plan or a date feels optimistic and you can't yet say why
- Assessment engagements, where this plus a brief is the whole deliverable
- Before committing to anything in front of a stakeholder

## When it doesn't

- Requirements aren't written yet — run `requirements-to-spec` first
- You already know the system deeply and the change is genuinely local
- You need the deep behavior of one flow — that's `trace-the-flow`, which this may tell you to run

## Prerequisites

- `.fde/03-requirements.md` — you're probing *these* requirements
- `.fde/02-system-map.md` — you need to know where things are before asking whether they exist

Missing the system map, you'll re-derive it inline, badly and without citations. Run `repo-recon` first. If the engagement genuinely doesn't warrant it, say so in the Confidence line.

## Procedure

Work requirement by requirement. Steps 1–5 per requirement, then 6–8 across the set.

### 1. Does this already exist?

Search before assuming absence. In a large enterprise system the capability frequently exists — partially, under a different name, disabled behind a flag, or built for a neighbouring use case two years ago.

```bash
# Search the domain vocabulary, not your own words for it
grep -rin "refund.*currenc\|currenc.*refund" --include="*.java" --include="*.sql" . | head -20

# Feature flags often hide finished work
grep -rn "featureFlag\|toggle\|isEnabled\|LaunchDarkly\|unleash" --include="*.*" . | head -20

# History: someone may have tried already
git log --all --oneline --grep="currency" -i | head -20
```

Four possible answers, and they have very different costs:

| Answer | Implication |
|---|---|
| **Exists and works** | The requirement may already be met — confirm and close it. This happens more than people expect. |
| **Exists, partially** | Usually cheapest. Extend rather than build. |
| **Existed, was removed** | `git-archaeology` — find out *why* before rebuilding it. |
| **Doesn't exist** | Genuine new work. |

Finding that a requirement is already satisfied is a first-class outcome. Report it prominently — it's free scope reduction, and it demonstrates you looked.

### 2. Where would the change land?

Name **specific files**, with lines. This is the section people will actually use, and vagueness here defeats the purpose of the whole exercise.

```bash
grep -rn "class RefundService\|interface Refund" --include="*.java" . | head
grep -rl "RefundRequest" --include="*.java" . | head -20
```

Distinguish three things, because they carry different risk:

- **Core change sites** — where the new behavior lives
- **Ripple sites** — DTOs, mappers, serializers, interfaces, tests that must change in sympathy
- **Contract sites** — anything published beyond this repository

Ripple sites are the usual source of underestimation. A field added to a domain object in a layered system commonly touches six to ten files before anything new has been built.

### 3. Classify the shape of the change

The strongest predictor of cost, and far more reliable than intuition about difficulty:

| Shape | What it means | Relative cost |
|---|---|---|
| **Configuration** | A value, flag, or mapping changes. No code. | Lowest — but check who owns the config and whether the environment is reachable |
| **Extend existing** | New case in an existing abstraction that anticipated it | Low, and predictable |
| **New component** | Genuinely new, but self-contained behind a clear boundary | Moderate, and usually well-estimated |
| **Modify shared** | Change to something many callers depend on | High — cost is in the callers, not the change |
| **Cross-cutting** | Touches many modules: a new field through every layer, an auth change, a new tenant dimension | Highest, and the most underestimated shape there is |

Cross-cutting is the category to name loudly. It looks small at every individual site, which is exactly why the total is wrong.

### 4. Look specifically for deceptive cost

The core of the skill. Run this checklist against every requirement that looked easy — those are the ones that hurt.

**Shared component with many callers.** The change is one line; verifying twenty callers is the work.
```bash
grep -rl "RefundService" --include="*.java" . | wc -l
```

**Schema change on a large or replicated table.** Row count, replication, and downstream consumers determine whether this is a migration or a project. See `db-change-management`.
```bash
grep -rn "CREATE TABLE refunds\|@Table(name = \"refunds\")" --include="*.sql" --include="*.java" .
```

**Crosses a published contract.** OpenAPI specs, `.proto` files, event schemas, WSDLs, published client libraries. Once consumers exist outside the repository, versioning and coordination dominate the cost.
```bash
find . -name "*.proto" -o -name "openapi*.y*ml" -o -name "swagger*.json" -o -name "*.wsdl" -o -name "*.avsc" | head
```

**Needs data that isn't collected.** The cheapest-looking and most expensive class of requirement. A report needing a field nobody has ever stored means a schema change, a backfill of unknown feasibility, and a wait for data to accumulate — often months of calendar time no amount of engineering compresses.

**No test coverage, and no easy way to add it.** Untested code isn't just risky; it's *slow* to change safely, because `characterization-tests` becomes a prerequisite. Check whether the change site is covered at all.

**No clear owner.** Code nobody maintains has no reviewer, no context, and no one to answer questions. Feeds `ownership-map`.
```bash
git log --format="%an" --since="18 months ago" -- path/to/area | sort | uniq -c | sort -rn | head
```

**Config in an environment you can't reach.** A one-line change you cannot make yourself is gated by someone else's queue, which belongs in `00b-access.md` today rather than the day before release.

**Duplicated logic.** Change one, miss four. Search for the *behavior*, not the class name — copy-paste rarely keeps the name.
```bash
grep -rn "amount \* rate\|convertCurrency\|applyFxRate" --include="*.java" . | head -20
```

**Generated code.** If the change site is generated, editing it is wrong and will be silently reverted by the next build. Find the generator and the schema it reads.
```bash
grep -rln "DO NOT EDIT\|auto-generated\|@Generated" --include="*.*" . | head
```

**Auth, audit, or compliance surface.** Anything touching permissions, personal data, money, or audit trails brings a review process whose lead time usually exceeds the implementation.

**Long feedback loop.** A change to a nightly batch that can only be verified overnight has a hard floor on iteration speed regardless of how simple the code is.

**COTS customization.** On a vendor platform, ask whether the customization survives the next upgrade. If not, the true cost includes re-doing it every upgrade, forever. See `cots-configuration`.

### 5. Assign a confidence

Per requirement, using the tags from `../_shared/evidence-discipline.md`:

- **`[confirmed]`** — you found the code, you know where the change goes, you've checked the callers
- **`[inferred]`** — the structure is clear, you haven't verified every site
- **`[unverified]`** — you couldn't reach what you needed; name what would resolve it

**Do not average these away.** A feature with four confirmed requirements and one unverified one is not "mostly confirmed" — the unverified one is where the schedule risk lives, and flattening it is precisely the failure this skill exists to prevent.

### 6. Collect the unknowns as a work item

Every `[unverified]` becomes an entry naming: what's unknown, why it matters, what would resolve it (access, an interview, a spike), and how long that takes.

This list is more valuable to a delivery lead than the estimate they asked for. It converts "we're not sure" into a set of actions with owners — which is the difference between a risk that gets managed and one that surfaces in week five.

### 7. Note the alternatives you spotted

While in the code you'll see cheaper routes the spec didn't consider: an existing extension point, a config-only path, a solution outside this system entirely, or a scope reduction that removes most of the cost for little loss of value.

Record these as observations, not decisions — `solution-design` evaluates them properly. But surface them now, because the plan is still soft and this is the moment they can change it.

### 8. Do not estimate

Deliberate separation. This skill establishes what's true about the code; `estimation` turns that into ranges and dates, and does so knowing the team's velocity, availability, and the org's overheads — none of which are in the codebase.

When someone asks for a number here — and they will — give them the shape instead: *"Three of these are extend-existing and well understood. One is cross-cutting through eleven files. One depends on data we don't currently collect, and that one isn't an engineering problem."* That is more useful than a number and it's defensible, which a number produced on the spot is not.

## Output template

Write to `.fde/04-feasibility.md`:

```markdown
# Feasibility — <feature>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** <overall, plus where the uncertainty concentrates>

## Summary
| Req | Exists? | Shape | Sites | Confidence | Deceptive cost |
|---|---|---|---|---|---|
| R1 | partial | extend existing | 3 | confirmed | — |
| R2 | no | cross-cutting | 11 | inferred | shared DTO, 4 consuming teams |
| R3 | no | new component | 2 | unverified | needs data not currently collected |

**Headline:** <the two or three sentences a delivery lead needs. Lead with the thing that changes the plan.>

## Per requirement

### R1 — <requirement>
**Already exists:** partial — `RefundService:88` handles single-currency `[confirmed]`
**Change lands:**
- `src/refunds/RefundService.java:88-120` — core
- `src/refunds/RefundRequest.java:14` — ripple, add field
- `src/api/v2/RefundResponse.java:22` — **contract**, published

**Shape:** extend existing
**Deceptive cost:** none identified
**Confidence:** `[confirmed]`
**Notes:** <anything the implementer needs to know>

### R2 — …

## Deceptive costs found
| Req | What | Evidence | Consequence |
|---|---|---|---|
| R2 | `RefundRequest` used by 4 external consumers | `grep -rl` → 4 repos | Contract versioning + coordination |

## Unknowns
| # | Unknown | Why it matters | To resolve | Effort | Owner |
|---|---|---|---|---|---|
| 1 | Does the nightly recon job parse this payload positionally? | Would break silently on a new field | Read `ReconJob` — needs repo access | 1h after access | FDE |

## Alternatives spotted
| Instead of | Consider | Why it might be cheaper | Trade-off |
|---|---|---|---|

## Already satisfied
<Requirements the system already meets. Free scope reduction — say so clearly.>

## What this document is not
This is not an estimate. It establishes what is true about the code. Sizing belongs to `estimation`, which needs team velocity and availability this document does not contain.
```

## Common traps

**Assuming absence without searching.** The most common error, and the most embarrassing when a long-tenured engineer points at the existing implementation.

**Naming modules instead of files.** "It'd be in the refunds module" is not feasibility. `RefundService.java:88` is.

**Missing the ripple sites.** The core change is rarely the work. Count the DTOs, mappers, interfaces, and tests.

**Skipping the deceptive-cost checklist on easy items.** Those are exactly the items it exists for. The hard ones are already being treated as hard.

**Averaging confidence.** One `[unverified]` requirement among five is not "mostly confident" — it's the whole risk, and flattening it is the failure mode this skill was built to prevent.

**Being talked into a number.** Give the shape. A number produced in the room becomes the commitment, and you will not get to revise it.

**Probing forever.** This is bounded. When each requirement has a shape, sites, and a confidence tag, stop — remaining uncertainty belongs in the Unknowns table as tracked work, not as more investigation now.

**Silence about the cheaper route.** If you spotted one, say so while the plan is still soft. Two weeks later it's a criticism instead of a contribution.
