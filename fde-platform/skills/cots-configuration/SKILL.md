---
name: cots-configuration
description: Work on a vendor platform where the deliverable is configuration rather than code - SAP, Salesforce, ServiceNow, Workday, Dynamics, Guidewire and similar - where the binding constraint is the vendor upgrade path, config lives in the platform rather than in git, and the right answer is often not to build it. Use for package implementation engagements, when customizing a vendor product, when asked whether something can be configured or must be coded, or when a platform upgrade is threatened by existing customization. Engineers new to COTS reliably misjudge this.
---

# COTS configuration

Where building it yourself is usually the wrong answer.

## Why this exists

Vast amounts of enterprise IT are configuration of vendor platforms, not code. Engineers arriving from a pure software background reliably misjudge this work in the same direction: they treat the platform as an inconvenient runtime and build around it, and the resulting customization breaks at the next vendor upgrade.

Three properties make COTS genuinely different:

**The vendor's upgrade path is the binding constraint.** A customization that works today but blocks next year's mandatory upgrade has a cost that is invisible now and enormous later. The organization will be on this platform for a decade.

**Configuration doesn't live in git.** It lives in the platform, changed through a UI, with the platform's own change and transport mechanism. Version control, code review, and diffing all work differently or not at all — and pretending otherwise produces an unmanageable estate.

**The right answer is frequently "don't."** Adapting the process to the platform's standard behavior is usually cheaper over the platform's lifetime than customizing the platform to the process. Recommending that is often the highest-value thing an engineer does on these engagements, and it is not what anyone expects an engineer to say.

## When this applies

- Package or SaaS platform implementation
- Customizing a vendor product
- "Can this be configured or does it need code?"
- A platform upgrade threatened by existing customization
- Assessing whether a requirement is worth building

## When it doesn't

- Custom software you own end to end
- Integrating *with* a vendor platform from outside — that's `integration-adapter`
- The platform is only a data source

## Prerequisites

- `.fde/00-engagement.md` — COTS should be the recorded archetype
- `.fde/03-requirements.md` — you're assessing these against platform capability
- Vendor documentation, and access to a non-production instance

## Procedure

### 1. Learn the customization tiers before designing anything

Every major platform has tiers, roughly consistent across vendors despite different names:

| Tier | Nature | Upgrade risk |
|---|---|---|
| **Configuration** | Supported settings, fields, workflows, rules via the UI | Low — vendor preserves it |
| **Extension** | Vendor-sanctioned extension points, plugins, custom objects | Low to moderate — usually supported |
| **Customization** | Custom code in the platform's language, in vendor-defined places | Moderate — may need revalidation each upgrade |
| **Modification** | Changing vendor-supplied objects or core behavior | **High — frequently blocks upgrades entirely** |

Learn where these boundaries sit on *this* platform, early. It's the single most important thing to know, and the answer determines which requirements are cheap and which are ruinous.

**Modifications are usually the wrong answer regardless of how well they solve the problem.** They accumulate, and eventually the organization cannot upgrade — a state many large organizations are actually in, paying for extended support on a version they can't leave.

### 2. Ask whether the process can change instead

The question engineers don't ask, and the one that most often produces the best outcome.

Vendor platforms encode a process. Where the organization's process differs, there are two options: customize the platform, or adapt the process. The second is frequently cheaper over the platform's lifetime, and it's rarely evaluated because the requirement arrived as "make it do X."

Ask: *why* does the process work this way? Often it's a constraint of the previous system that nobody has revisited, being faithfully reproduced at considerable expense into a platform that doesn't need it.

Raise this carefully. It's a business-process question wearing a technical costume, and it belongs to the sponsor — but nobody else in the room is positioned to notice it. Frame it as an option with a cost comparison, not as a challenge to how they work.

### 3. Establish where configuration lives and how it moves

Fundamental, and unlike code work:

- Where does configuration live — a database in the instance, exportable metadata, files?
- How does it move between environments — transport requests, change sets, a metadata API, manual re-entry?
- Can it be diffed? Version-controlled? Reviewed before it lands?
- Can changes be **rolled back**, or only re-entered?
- Who can make changes in production, and is that gated?

Answer these before making changes. An estate where nobody knows what was changed, by whom, or how to reproduce it in another environment is a real and common failure — and once you're in it, it takes months to climb out.

Where the platform supports metadata export, **get it into version control**, even if imperfectly. A diffable record of configuration is worth substantial effort.

### 4. Assess each requirement against the tiers

For each requirement, establish which tier satisfies it and what that costs — including at every future upgrade. Feed it into `feasibility-probe`, whose deceptive-cost checklist already flags COTS customization for exactly this reason.

The critical question for anything above configuration: **does this survive the vendor's next upgrade?** Where the answer is no, or unknown, the true cost includes redoing it every upgrade, forever. That's a very different number from the build estimate, and it's the number that should be presented.

Check the vendor's roadmap too. Building something the vendor is shipping natively in two releases is a common and avoidable waste — and vendors will usually tell you if asked directly.

### 5. Test against a real upgrade where you can

Most vendors provide preview or early-access releases. Where available, testing customizations against the next version is the only way to know whether they survive — and it converts a future crisis into current work.

Where it isn't available, record every customization above the configuration tier as an **upgrade-risk item** in the handover. The team upgrading in two years needs a list of what to revalidate, and they will not be able to reconstruct it.

### 6. Follow the vendor's own lifecycle

These platforms have their own conventions for environments, change transport, testing, and release. They usually differ from the organization's software process and frequently from what you're used to.

Use theirs. Fighting the platform's model produces an estate that neither the vendor's tooling nor the organization's process can manage properly. `change-control-navigation` applies here too — COTS changes often have their own approval path.

### 7. Record configuration decisions as ADRs

Configuration decisions have the same longevity as architectural ones and are *less* discoverable — there's no code to read, and the UI shows the current state with no history or rationale.

Why a field was added, why a workflow branches, why a validation rule exists: none of it is visible in the platform. An ADR is frequently the only durable record, and on these engagements it's disproportionately valuable.

## Output

Write to `.fde/05d-cots-assessment.md`, with decisions as ADRs:

```markdown
# COTS assessment — <platform>

**Engagement:** <name> · **Platform:** <name + version> · **Date:** <YYYY-MM-DD>
**Vendor upgrade cadence:** 2 major/year, N-1 supported
**Next upgrade:** <date> — **customizations must survive it**

## Customization tiers on this platform
| Tier | Mechanism here | Upgrade-safe |
|---|---|---|
| Configuration | Admin UI, field/workflow setup | yes — vendor preserved |
| Extension | Custom objects, sanctioned hooks | yes |
| Customization | Platform-language scripts in defined slots | revalidate each upgrade |
| Modification | Editing vendor objects | **prohibited — blocks upgrades** |

## Requirements assessed
| Req | Tier needed | Upgrade risk | Recommendation |
|---|---|---|---|
| R1 approval routing | configuration | none | Build — standard |
| R2 custom pricing calc | customization | revalidate each upgrade | Build; log as upgrade-risk |
| R3 bespoke invoice layout | **modification** | **blocks upgrades** | **Don't.** Vendor ships this natively in <version>, <date>. Recommend waiting. |
| R4 legacy approval chain | modification | blocks upgrades | **Recommend process change** — the chain exists because the old system couldn't do parallel approval. This platform can. |

## Configuration management
**Lives in:** instance metadata · **Moves via:** change sets
**Version controlled:** partial — metadata export to `config/` weekly `[new, introduced by FDE]`
**Diffable:** yes, post-export · **Rollback:** re-import previous export, ~20 min, rehearsed <date>
**Prod change gated by:** <role>

## Upgrade-risk register
| # | Customization | Tier | Revalidate at upgrade | Owner |
|---|---|---|---|---|
| 1 | Pricing calc script | customization | yes — test on preview release | <name> |

## Process-change recommendations
<Where adapting the process beats customizing the platform, with a cost comparison.>
```

## Common traps

**Treating the platform as an inconvenient runtime.** Customizing around it is how organizations end up unable to upgrade.

**Not learning the tiers first.** Determines which requirements are cheap and which are ruinous.

**Never asking whether the process could change.** Often the cheapest answer, and nobody else will raise it.

**Faithfully reproducing a previous system's constraints.** Expensive reimplementation of a limitation that no longer exists.

**Configuration with no version control or record.** An unmanageable estate, and months to recover from.

**Not checking the vendor roadmap.** Building what ships natively in two releases.

**Costing a customization at build price.** The real cost includes every future upgrade.

**Fighting the platform's lifecycle.** Produces an estate neither the vendor's tools nor the organization's process can manage.

**Not recording why.** The UI shows current state with no history. An ADR is often the only record that will exist.
