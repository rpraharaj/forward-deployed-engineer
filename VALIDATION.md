# Cold-start validation

Record of the test [DESIGN.md §12](DESIGN.md) specifies: point the spine at a genuinely unfamiliar repository, in a stack the skills weren't written against, and see what breaks.

---

## Run 1 — dbt-core

**Date:** 2026-07-26 · **Subject:** `dbt-labs/dbt-core` @ full clone, 3,124 files
**Why this subject:** unfamiliar, non-JVM, non-JS, polyglot, workspace-structured, and active (3,347 commits in six months). Chosen specifically to stress the stack-agnostic claim rather than confirm it.

### Result: 6 defects, 1 severe. All fixed.

The most useful finding came before any defect. Going in, the assumption was that dbt-core is a Python project. **It is now Rust** — 1,363 `.rs` files against 18 `.py`. Step 1 of `repo-recon` caught this in about thirty seconds, which is the "detect, don't assume" principle working exactly as intended. A skill that had hardcoded Python would have produced a confidently wrong map.

| # | Severity | Defect | Fix |
|---|---|---|---|
| 1 | **Severe** | `repo-recon` step 3 hardcoded Java/JS/Python entry-point patterns in the SKILL.md body. Found **5** entry points where the system has **61**. Would have produced a confident, wrong system map. | Patterns moved to `repo-recon/references/entry-points-by-stack.md`, loaded on detection. Nine stacks plus a stack-independent sweep. Body now carries a sanity check: *"if a 1,300-file codebase appears to have two entry points, you searched wrong."* |
| 2 | Moderate | `stack-detection.md` one-shot survey uses `-maxdepth 2`, finding **1** manifest where there are **124**. A workspace read as a single project. | Added an explicit sub-manifest count step. |
| 3 | Moderate | Churn analysis dominated by `Cargo.toml` (407) and `CHANGELOG.md` (229); real hotspots pushed below the fold. | Filter manifests, lockfiles, changelogs. Added `--no-renames` and a shallow-clone guard. |
| 4 | Moderate | Test topology counted files in `test/` directories, returning 216 snapshot **fixtures** as the top "test location" while 459 files with inline `#[test]` were invisible. | Count both conventions; explicit warning about fixture directories masquerading as tests. |
| 5 | Minor | No guidance for finding the build workflow among 20+ bot/automation workflows. | Added CI triage — rank workflows by build-command density. |
| 6 | Minor | `git log` emitted a rename-detection warning and stalled on large history. | `--no-renames`. |

### Verification of fixes

Re-run against the same repository after fixing:

| Fix | Before | After |
|---|---|---|
| Sub-manifest count | 1 | 124 Cargo.toml — workspace revealed |
| CI triage | no guidance | `release-v2.yml` surfaced, 21 build commands |
| Churn | `Cargo.toml` 407, `CHANGELOG.md` 229 | `nodes.rs` 191, `xdbc/lib.rs` 134, `resolver.rs` 127 |
| Test topology | 216 snapshot fixtures | 459 files with inline tests |

### What this says about the design

The stack-agnosticism principle ([DESIGN.md §3.3](DESIGN.md)) was stated correctly and **violated in implementation** — three of the six defects were language assumptions leaking into a SKILL.md body that the design explicitly says must stay universal. Stating a principle in a design document does not enforce it.

The lesson carried into Wave 2: **no language-specific pattern belongs in a SKILL.md body.** If a step needs one, it needs a reference file loaded on detection.

The evidence discipline held up better. Every defect above was found by comparing what a command *returned* against what the repository *actually contains* — which is only possible because the skills insist on running commands and citing output rather than reasoning about what a codebase probably looks like.

---

---

## Run 2 — nopCommerce

**Date:** 2026-07-26 · **Subject:** `nopSolutions/nopCommerce`, 6,674 files, 3,614 C#
**Why this subject:** .NET, layered enterprise application, plugin architecture, DI-heavy, server-rendered. Chosen to be maximally unlike run 1's Rust workspace. Also exercised `blast-radius` and the entry-point reference written *after* run 1.

### Run 1 fixes held

The fixes generalized rather than overfitting to Rust:

| Fix | Result on .NET |
|---|---|
| Sub-manifest count | 39 `.csproj` surfaced; depth-2 survey alone found only the `.sln` |
| CI triage | `dotnet.yml` correctly identified as the build workflow |
| Churn / test-topology | No stack assumptions triggered |

`blast-radius` also validated: ring 1 on `ICustomerService` returned 169 files — the count *is* the finding, exactly as the skill describes. Its grep-insufficiency caveat proved correct and checkable (3 implementors against 40 DI registration sites).

### 3 new defects, all fixed

| # | Severity | Defect | Fix |
|---|---|---|---|
| 1 | **Severe** | Searching framework-standard patterns returned **0** hits for `IHostedService`/`BackgroundService` in an application with **39** scheduled tasks behind its own `IScheduleTask`. Reads as "no scheduled work" — the same silent-wrong-answer failure as run 1, one level up. | New **"When the standard search returns zero"** section. Generic technique for discovering a codebase's *house abstraction*, plus a note on plugin-contributed entry points. |
| 2 | Moderate | Attribute-routing search found 117 files; the app has 138 controller classes. Convention-routed MVC controllers were invisible. | .NET section now compares both counts and reads the route table. |
| 3 | Minor | `TargetFramework` is centralized in `Directory.Build.props`, so a per-`.csproj` version grep returns nothing. | `stack-detection.md` now covers centralized build config across five ecosystems. |

### The generalizable lesson

Defect 1 is run 1's lesson at a higher altitude. Run 1: *don't assume the language.* Run 2: **don't assume the codebase uses its framework's vocabulary.** Mature enterprise systems wrap framework primitives in house abstractions, so the canonical search returns zero and the absence reads as fact.

The fix had to be a *method*, not a pattern. Adding `IScheduleTask` to a .NET list would have fixed nopCommerce and nothing else. Instead the reference now teaches how to find whatever the house abstraction is — and on re-test that generic technique surfaced `IScheduleTask` (19), `IConsumer` (25), and `IStartupTask` **with no nopCommerce-specific knowledge**.

The operating heuristic, now written into the reference: *if a search for a capability the system obviously must have returns zero, the search is wrong, not the system.*

---

## Run 3 — trigger discrimination across all 27 skills

**Date:** 2026-07-26 · **Method:** 38 realistic queries put to `claude -p` with all 27 name+description pairs, asking which skill it would invoke. Scored on whether the intended skill came **first**.

Skill descriptions are the sole triggering mechanism, and a skill that doesn't fire is worthless regardless of how well it's written. With 27 loaded at once the specific risk isn't weak triggering — it's *competition*, where two plausible skills split the decision. The eval was built to measure discrimination rather than single-skill trigger rate.

### Result

| Measure | Score |
|---|---|
| Positives — intended skill ranked first | **26 / 27** |
| Negatives — correctly silent | **6 / 6** |
| Collision probes — sensible primary + secondary | **5 / 5** |

**No false fires at all.** Six near-miss queries (a CSV parsing function, a SQL question, a React re-render bug, a cover letter, a Kafka explainer, a variable rename) returned `NONE`. Over-triggering was the risk worth checking most, and the descriptions are appropriately bounded.

The deliberately ambiguous probes resolved well, each picking the right primary and a defensible secondary:

| Probe | Resolved to |
|---|---|
| "how long is the refund work going to take" | `estimation`, `feasibility-probe` |
| "are we ready to ship this" | `release-readiness`, `verification-plan` |
| "engagement is wrapping up next month" | `handover-pack`, `enablement-handoff` |
| "I don't know this codebase and need to change something in it" | `repo-recon`, `safe-change` |
| "need to tell them the plan has slipped" | `escalation-and-renegotiation`, `stakeholder-brief` |

### One defect, found and fixed

`fde-orient` beat `feasibility-probe` on *"can we add multi-currency by end of Q3? I haven't looked at their code yet"* — a sizing question, not an engagement-opening one.

Cause was a single line in its description: **"Run this before any other FDE skill."** Written to prevent under-triggering, it made `fde-orient` win any query carrying a hint of unfamiliarity — turning the entry-point skill into a catch-all.

Replaced with an explicit scope boundary naming the skills it should defer to. Re-tested: `feasibility-probe` now wins its own query, and `fde-orient`, `repo-recon`, and `access-and-onboarding` all still win theirs. No regression.

The remaining non-first is `stakeholder-brief` losing to `escalation-and-renegotiation` on *"tell the sponsor the reporting piece isn't happening"* — which is arguably the correct call, since communicating a scope reduction is renegotiation. Left as-is.

### Incidental finding: context cost

The 27 descriptions total **~16 KB (~4k tokens) loaded every session**, whether or not any skill fires. That is the ongoing price of `fde-core`, and it is exactly the budget `context-strategy` exists to protect. It supports the pack-splitting decision in [DESIGN.md §9.1](DESIGN.md) — Wave 4's 16 skills should ship as optional packs rather than being folded into core.

### What this run does not establish

It tests *selection between skills*, not whether a skill improves the outcome once selected. That remains the untested question below.

---

## Run 4 — trigger discrimination at full scale (43 skills)

**Date:** 2026-07-26 · **Method:** run 3 repeated after Wave 4, with 16 new queries added. 54 queries against all 43 descriptions.

| Measure | 27 skills (run 3) | 43 skills (run 4) |
|---|---|---|
| Positives ranked first | 26 / 27 (96%) | **42 / 43 (98%)** |
| Negatives correctly silent | 6 / 6 | **6 / 6** |
| Collision probes resolved | 5 / 5 | **5 / 5** |

**Adding 16 skills caused no regression.** The single non-first is the same known-acceptable case from run 3 (`stakeholder-brief` losing to `escalation-and-renegotiation` on communicating a scope reduction, which is arguably correct).

This was the main risk of Wave 4 — that new skills would compete with established ones — and it did not materialize. Likely because the archetype-pack skills are narrow and domain-specific (`cots-configuration`, `cutover-plan`, `db-change-management`), so their descriptions don't overlap with the general-purpose core.

**Description context cost is now ~25 KB (~6k tokens)** across all 43. This is why the packs are optional: `fde-core` alone is ~17 KB, and an engagement installs only the pack it needs.

---

## Run 5 — baseline comparison

**Date:** 2026-07-26 · **Method:** the same system-mapping task given to `claude -p` in the dbt-core checkout, once with no skill and once following `repo-recon`. This is the check the skill-creator workflow calls for and the one that had been missing: does the skill change the outcome, or is it overhead?

### Result: yes, in two specific ways

| Property the skill claims to produce | Baseline | With skill |
|---|---|---|
| `file:line` citations | 0 | 2 |
| Confidence tags | 0 | 2 |
| Explicit gaps section | 0 | 2 |
| Length | 440 words | 810 words |

**The baseline was strong**, and that is worth stating plainly. Unprompted, it correctly identified the codebase as the Rust rewrite, named a real entry point (`crates/dbt-main/src/main_impl.rs`), and flagged a genuine fragility. Claude does not need this skill to understand a codebase.

**But it made a factual error the skill avoided.** The baseline concluded the workspace ships *"a single self-contained binary."* The with-skill run identified `dbt-sa-cli` as a separate binary. Checked directly: the workspace declares **9 `[[bin]]` targets across 43 crates containing `src/main.rs`**. The baseline was wrong; the skill was more correct.

Neither enumerated all nine, so this is an improvement rather than a fix — but it lands exactly where run 1's entry-point defect was, which suggests the procedural step ("enumerate per crate, sanity-check the count against the repo's size") is doing real work.

### What this establishes, and what it doesn't

The skill's contribution is **not** making Claude smarter about the codebase. It is:

1. **Provenance** — claims carry citations and confidence tags, so a reader can check them
2. **Declared limits** — an explicit gaps section, so omission doesn't read as absence
3. **Marginally better accuracy** on the enumeration steps the procedure forces

That matches what [DESIGN.md §1](DESIGN.md) claimed the portfolio was for. It is a narrower claim than "the skill makes it work," and it is the honest one.

Single task, single repo, single run. Not a benchmark — a first data point, and it points the right way.

---

## Still untested

Honest coverage statement after three runs:

- **Triggering:** all 27 skills tested and passing. This is now the best-covered dimension.
- **Procedure exercised:** `repo-recon`, `stack-detection`, `blast-radius` (ring 1 and the DI caveat), and the entry-points reference, across two stacks.
- **Not exercised:** the procedures of the other 24 skills. Most are engagement-shaped — they need requirements, stakeholders, an environment, and a release decision, none of which a clone provides. `env-bootstrap` and `characterization-tests` could be tested against a clone and haven't been.
- **Two stacks, both modern.** Rust and .NET. A mainframe-adjacent, COBOL, or heavily XML-configured legacy Java system would likely surface a third class of assumption — very plausibly around config-driven wiring, which is where enterprise systems hide the most behavior.
- **No comparative run.** The skill-creator workflow calls for running the same prompt with and without the skill to confirm the skill changes the outcome. Both runs tested whether the *procedure* is correct, not whether it beats the baseline.
- **No human check of a produced artifact.** The real test for a system map is whether someone who knows the codebase reads it and finds no material error. That needs a reader who knows the system.
