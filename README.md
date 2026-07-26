# FDE Skills

Claude Code skills for a **forward deployed engineer** — someone dropped into unfamiliar organizations and expected to deliver, from a vague ask through to something running in production, on a stack they didn't choose, in a codebase nobody documented.

**43 skills across five installable packs.**

```bash
claude plugin install ./fde-core        # always — 30 skills, every engagement
claude plugin install ./fde-data        # analytics, ETL, warehouse, schema change
claude plugin install ./fde-migration   # replatform, upgrade, cutover, decommission
claude plugin install ./fde-platform    # integration, contracts, COTS (SAP/Salesforce/ServiceNow)
claude plugin install ./fde-operate     # pipelines, post-deploy watch, observability
```

Install core plus whichever pack matches the engagement. You invoke skills by describing your situation in plain language — say *"I've been dropped into a payments system I've never seen"* and the right one fires.

---

## Start here

| Document | What it's for |
|---|---|
| **[USAGE.md](USAGE.md)** | How to use them. First-day walkthrough, skill reference, workflows by engagement type. **Read this one.** |
| [DESIGN.md](DESIGN.md) | Why the portfolio is shaped this way — the lifecycle model, design principles, engagement archetypes |
| [VALIDATION.md](VALIDATION.md) | What was tested and what wasn't. Five test runs, defects found, honest coverage gaps. |

---

## The idea in three lines

**Artifacts, not conversations.** Every skill writes a file to a `.fde/` workspace. Work that lives only in a chat transcript evaporates when you leave — and you always leave.

**Evidence or a confidence tag.** Every claim carries a `file.java:88` citation or one of `[confirmed]` / `[inferred]` / `[unverified]`. This is the difference between being trusted in week two and being quietly routed around after being confidently wrong once.

**Skills compose.** Each reads what the previous ones wrote. `feasibility-probe` reads the system map and the spec instead of re-deriving them.

---

## What the skills actually add

Claude already knows how to write a service. Tested against a baseline on a real unfamiliar repository, the measurable contribution was **provenance** (citations and confidence tags where the baseline had none), **declared limits** (an explicit gaps section, so omission doesn't read as absence), and modestly better accuracy on the enumeration steps the procedures force — the baseline claimed the codebase shipped one binary where it declares nine.

That's a narrower claim than "the skills make it work," and it's the honest one. See [VALIDATION.md](VALIDATION.md).

---

## Stack-agnostic by construction

No `SKILL.md` body names Maven, npm, or pytest. Skills detect the stack, then load a matching reference — entry points across nine ecosystems, test harnesses, indirection mechanisms.

This was not free. Cold-start testing against a Rust workspace and a .NET monolith found six and three defects respectively, most of them language assumptions leaking into skill bodies that the design explicitly forbade. Stating a principle in a design document does not enforce it.

---

## Status

| | |
|---|---|
| Skills | 43 across 5 packs |
| Triggering | 42/43 correct, 0 false fires on near-miss queries |
| Procedures exercised | 4 of 43, across 2 stacks |
| Baseline comparison | 1 task, 1 repo |

The honest gap is that most skills' *procedures* remain untested — they're engagement-shaped and need stakeholders, an environment, and a release decision that a cloned repository can't provide. [VALIDATION.md](VALIDATION.md) states this precisely.
