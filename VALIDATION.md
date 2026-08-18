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

## Run 6 — Apache OFBiz, testing a stated prediction

**Date:** 2026-07-26 · **Subject:** `apache/ofbiz-framework`, 6,384 files
**Why this subject:** run 5 ended with an explicit prediction — that a *"mainframe-adjacent, COBOL, or heavily XML-configured legacy Java system would likely surface a third class of assumption, very plausibly around config-driven wiring."* OFBiz is an ERP framework whose entities, services, and routes are all XML-declared. This run existed to test that prediction rather than to confirm the portfolio works.

### The prediction was correct, and the defect is the worst found so far

| | Java-annotation search | Reality |
|---|---|---|
| HTTP routes | **0** | **3,113** `<request-map>` across 18 `controller.xml` |
| Services | — | **3,479** `<service name=>` |
| Entities | — | **843** `<entity entity-name=>` |

Every JVM entry-point pattern in the reference returned near-zero on a system with thousands of entry points. The map it would have produced — "5 mains, 4 controllers" — is not merely incomplete; it describes a different system.

**Neither previous fix caught it.** The run-1 fix (detect the language) passed: this *is* Java. The run-2 fix (find the house abstraction) failed too, because OFBiz services are XML declarations pointing at static methods, not Java interfaces with implementors. This is a genuinely distinct third class.

### The three classes, as a progression

| Run | Lesson |
|---|---|
| 1 — Rust | Don't assume the **language** |
| 2 — .NET | Don't assume the codebase uses its **framework's vocabulary** |
| 3 — OFBiz | Don't assume the entry points are **in the code at all** |

Each is one level more fundamental than the last, and each was invisible until a repository that violated it was tried. That progression is the strongest argument in this document for testing against real systems rather than reasoning about them.

### The fix

Again a method rather than a pattern, added as the **first** check in `entry-points-by-stack.md`, ahead of every language section:

1. **Detection heuristic** — compare config-file volume to source volume. Here: 1,035 XML against 1,169 Java, near parity, an unmissable signal once you look.
2. **Generic declaration discovery** — grep for repeated `<element name=>` patterns and rank by frequency.
3. **Find the loader** — the code that reads the config is the bridge to the executable surface.
4. **Database-held configuration** — the hardest variant, where neither code nor repository contains the behavior. Recorded as an access requirement rather than guessed at.

`repo-recon`'s body now names both pre-checks explicitly, before any language pattern runs.

**Verified on re-test**, using only the generic technique with no OFBiz knowledge: flagged config-driven from file counts, surfaced `<service>` (3,479), `<request-map>` (3,250), and `<screen>` (1,749) as the entry points, and identified `ConfigXMLReader.java` and `RequestHandler.java` as the loaders.

### Passes worth recording

Several earlier fixes were exercised and held:

- **Shallow-clone guard** — clone was `--depth 500`; `git rev-parse --is-shallow-repository` returned true, so churn analysis is correctly suppressed rather than reported from a truncated history
- **CI triage** — picked `gradle.yml` (7 build commands) out of 5 workflows
- **Sub-manifest count** — 5 `build.gradle` files against a depth-2 survey finding 2
- **Centralized build config** (a run-2 .NET fix) generalized to Gradle's `buildSrc`
- **`env-bootstrap` steps 1–3** ran clean: real build workflow, `gradlew` wrapper, Gradle 8.14.5 pin, Java source/target compatibility. **First procedural test of a skill other than `repo-recon`.**

---

## Run 7 — Plausible Analytics (Elixir/Phoenix)

**Date:** 2026-08-17 · **Subject:** `plausible/analytics` @ `d777fb9`, shallow clone `--depth 400`, 2,030 files
**Why this subject:** CONTRIBUTING asked for Elixir. The stack is in `stack-detection.md` (`mix.exs`) and **had no section** in `entry-points-by-stack.md`. This run tested the post-review claim that "generic" greps in the SKILL.md body are stack-neutral.

### Detection worked. The playbook after it did not.

| Check | As written, before this run | Reality |
|---|---|---|
| Language mix | 616 `.ex` + 615 `.exs` — Elixir | correct |
| One-shot survey | `mix.exs` found | correct |
| Sub-manifest count | **`package.json: 4` only** (`mix.exs` not in the loop) | 1 `mix.exs` + 4 `package.json` |
| Entry points (no Elixir section → stack-independent sweep) | Dockerfile `CMD ["run"]`, CI `run:` lines | **216** Phoenix routes in `lib/plausible_web/router.ex`, OTP app `Plausible.Application`, **24** Oban workers, 12 Mix tasks |
| Boundaries `^(import \|using \|from )` on `*.ex` | **0** | 630 `alias`, 610 `use`, 290 `import` — all indented |
| Tests, assertion grep on `*.ex` / `*.exs` | **0** / **2** | **309** `*_test.exs` files; 301 contain `test "` |
| Config `process.env` / `os.getenv` | 5 Node vars in JS | `config/*.exs` + `Application.get_env` in **45** files, `System.get_env` in 7 |
| Persistence `CREATE TABLE\|Schema(` | 56 hits in `structure.sql` | same dump, plus 56 Ecto `schema "` modules and 236 Postgres migrations the grep did not name |

The map the procedure would have produced: a Node-flavoured asset repo with a Docker entrypoint and almost no tests. That is a different product from a Phoenix app that ingests analytics into ClickHouse and Postgres.

**Shallow-clone guard held.** `git rev-parse --is-shallow-repository` is true; churn numbers from 400 commits are `[unverified]`. Router.ex still topped the truncated list, which matches a live product, but the skill correctly forbids treating that as a 12-month hotspot.

**CI triage was lucky, not correct.** `elixir.yml` ranked first because it also contains `npm` and `make`. The rank regex did not include `mix `. A workflow that only ran `mix test` would have scored 0.

### The fourth class

| Run | Lesson |
|---|---|
| 1 — Rust | Don't assume the **language** |
| 2 — .NET | Don't assume the codebase uses its **framework's vocabulary** |
| 3 — OFBiz | Don't assume the entry points are **in the code at all** |
| 4 — Elixir | Don't assume a **"generic" grep is stack-neutral** |

Run 1–3 are about searching the wrong place. This one is about searching the right tree with the wrong alphabet. Detecting Elixir and then grepping `^import ` / `def test_` / `process.env` is the same silent-zero failure as run 1's `*.java`, one layer up.

Adding Phoenix `get/post/live` to a list would have fixed Plausible. The fix that generalizes:

1. **If `entry-points-by-stack.md` has no section for the detected stack, do not fall through to the stack-independent sweep.** That sweep is a supplement. Use the "no language section" method: declared start in the manifest → filename conventions (`router.*`, `workers/`) → framework named in the lockfile.
2. **Module-reference and test discovery are per-stack forms**, allowing leading whitespace. Filename conventions (`*_test.*`) come before assertion syntax.
3. **Detection tables must list every stack they claim to detect.** `mix.exs` was in the one-shot survey and missing from the sub-manifest loop and the lockfile list.

### Verification of fixes

Re-ran the updated commands on the same checkout, no Plausible-specific knowledge beyond "this is Elixir":

| Fix | Before | After |
|---|---|---|
| Sub-manifest loop includes `mix.exs` | `package.json: 4` | `mix.exs: 1`, `package.json: 4`, `Makefile: 1` |
| CI triage includes `mix ` | elixir.yml won via npm/make | elixir.yml **33** (mix + npm + make) |
| Elixir playbook | no section | `mod: Plausible.Application`, router.ex, 216 routes, 24 Oban workers, 12 Mix tasks, 56 Ecto schemas |
| Test filenames | 0 / 2 | 430 paths matching `*_test.*` / `*_spec.*` |
| Module refs with whitespace | 0 | 630 alias / 610 use / 290 import |

### What this does not establish

Single product, one framework (Phoenix), shallow history, no human who owns the codebase read the map. The fourth class is as well supported as the first three were after one repo each — which is to say it is a real defect and not a benchmark.

---

## Run 8 — trigger discrimination after description edits

**Date:** 2026-08-17 · **Method:** the CONTRIBUTING protocol (name+description only; reply with at most two skill names or `NONE`). 64 queries: 43 positives (one per skill), 6 negatives, 5 historic collision probes, 10 regressions for the description edits in this cycle.

**Judge:** `grok --single`, not `claude -p`. Claude CLI on this machine remaps every `--model` alias to an unavailable third-party id. This is therefore **not** a like-for-like rematch of runs 3–4. It answers whether the current descriptions still discriminate for a different model that only sees the frontmatter.

Queries and scorer live in [`eval/trigger-queries.json`](eval/trigger-queries.json) and [`eval/run-trigger-eval.py`](eval/run-trigger-eval.py) so the next run is not reconstructed from memory. Raw replies: [`eval/trigger-results.json`](eval/trigger-results.json).

### Result

| Measure | Run 4 (`claude -p`, 43 skills) | This run (`grok --single`) |
|---|---|---|
| Positives ranked first | 42 / 43 | **43 / 43** |
| Negatives correctly silent | 6 / 6 | **6 / 6** |
| Collision probes | 5 / 5 | **5 / 5** |
| Description-edit regressions | — | **10 / 10** |

The description edits held on the things they were written to protect:

| Query | Intended | First pick |
|---|---|---|
| "can we add multi-currency by end of Q3? I haven't looked at their code yet" | `feasibility-probe` | `feasibility-probe` |
| "I've been dropped into a payments service… don't know where to start" | `fde-orient` | `fde-orient` (`repo-recon` second) |
| "help me understand this repo" | `repo-recon` | `repo-recon` |
| "I need a reviewer for this PR" | `ownership-map` | `ownership-map` |
| "implement R1, feasibility already done" | `safe-change` | `safe-change` |
| "I can't get into the VPN" | `access-and-onboarding` | `access-and-onboarding` |
| "login endpoint returns 401" | not `access-and-onboarding` | `incident-triage` (not access) |
| "give the sponsor a status update, nothing has slipped" | `stakeholder-brief` | `stakeholder-brief` |
| "the plan is no longer achievable" / "tell the sponsor the reporting piece isn't happening" | `escalation-and-renegotiation` | `escalation-and-renegotiation` |
| "what breaks if we add a field to the published refund response" | `blast-radius` | `blast-radius` |

Negatives (CSV, SQL join, React re-render, cover letter, Kafka explainer, rename a variable) all returned `NONE`.

Description context cost after the edits: **~24 KB / ~6.1k tokens** across 43, **~17.5 KB / ~4.4k tokens** for `fde-core` alone. Unchanged in kind from run 4.

### What this does not establish

It does not replace the Claude first-choice number. A different judge can hide a Claude-only steal. Re-run with `claude -p` when that CLI can reach an Anthropic model. It also does not test whether the skill improves the work once selected.

---

## Run 9 — characterization-tests on boltons (`ordinalize`)

**Date:** 2026-08-17 · **Subject:** `mahmoud/boltons` @ `580a9c2`, 112 files, Python / pytest
**Why this subject:** the skill had never been run against a real repository. Elixir/Plausible could not be used — no `mix` on the machine, and `harness-by-stack.md` had no Elixir section. Python was the runtime we could actually execute, which is a prerequisite the skill itself states.

### Procedure followed as written

1. Harness detection (`grep` of manifests) found pytest in `pyproject.toml`. Neighbouring tests mix `assert` and `unittest.TestCase`.
2. `ordinalize` in `boltons/strutils.py` had **doctest examples and no unit tests**. Pytest does not collect those doctests (no `--doctest-modules` in CI config).
3. Seam: public in-memory function. No fakes needed.
4. Observed current behavior, including cases that look wrong, then pinned them:

| Input | Current output | Looks like |
|---|---|---|
| `None` | `'None'` | a bug |
| `1.5` | `'1.5th'` | a bug |
| `-1` | `'-1st'` | surprising |
| `-11` | `'-11th'` | teen rule still applies to the digits |
| `0` | `'0th'` | odd but consistent |

5. Characterization suite: **19 passed** against unmodified code.
6. Mutation check: inverted the teen test (`numstr[-2] == '1'` → `!=`). **9 tests failed** (11/12/13/21/22/23/101/111/-1). Reverted.
7. Reachability: `raise` at the first line of the body. The `None` test failed with that error. Reverted.

Production source left clean. Tests lived only in the throwaway clone.

### What the skill changed vs an unprompted test

Without the skill, the natural tests are `ordinalize(1) == '1st'` and the happy English table. They would not have pinned `None` → `'None'` or `1.5` → `'1.5th'`. Those are exactly the cases a later "cleanup" would change, and exactly what the skill exists to freeze.

The mutation check is the other load-bearing step. A suite that only asserted `ordinalize(1) == '1st'` would have stayed green under the teen-rule inversion.

### Defects found and fixed

| # | Severity | Defect | Fix |
|---|---|---|---|
| 1 | Moderate | "Already well covered" can fire on doctests that CI never runs | Trap + when-it-doesn't: doctests are not a suite unless collected |
| 2 | Moderate | Existing test `test_asciify` asserts `len(b) == len(b)` — a tautology | Trap: read the assertion, not the name (same rule as `verification-plan`) |
| 3 | Minor | `harness-by-stack.md` had no Elixir row | Added ExUnit / `*_test.exs` / prefer fakes over Mox |

### What this does not establish

Single function, one language, no review by the library author. It does not test characterization at an HTTP or DB seam, and it does not test the "introduce a seam first" path.

---

## Run 10 — env-bootstrap on ripgrep

**Date:** 2026-08-17 · **Subject:** `BurntSushi/ripgrep` @ `3fce3b5`, shallow clone, 237 files, Rust / Cargo workspace
**Why this subject:** `VALIDATION.md` still listed env-bootstrap as steps 1–3 with no completed build. Ripgrep has a lockfile, a workspace (12 `Cargo.toml`), and a compiler floor *above* the machine's installed `rustc`. Artifacts: [`eval/workspaces/ripgrep/`](eval/workspaces/ripgrep/).

### Procedure followed as written

1. **CI first.** Only PR workflow: `ci.yml`. Rank: `ci.yml` 7, `release.yml` 6. Extracted verbatim (local-ish, no `cross`):

   `cargo build --verbose --workspace`  
   `cargo build --verbose --workspace --features pcre2`  
   `cargo test --verbose --workspace --features unstable-index`  
   `cargo test --verbose --workspace --features pcre2`

   Toolchain from the same file: matrix `pinned` / `rust: 1.96.0`; **macos job uses `nightly`**.

2. **Stack.** 110 `.rs`, 12 `Cargo.toml`, `Cargo.lock` present. No compose, no Makefile, no `.env`.

3. **Pin-file grep (skill verbatim, before the fix).**

   ```text
   git ls-files | grep -iE "^\.(nvmrc|…|java-version)$|toolchain|global\.json"
   ```

   **Returned nothing.**

4. **Pins the grep missed.** `Cargo.toml` `[workspace.package] rust-version = "1.96"` / `edition = "2024"`. README Building: 1.96.0 or newer. CI as above.

5. **Installed vs pinned.** `rustc 1.90.0` (rustup `stable`, default, left unchanged). `cargo build --workspace` downloaded crates, then:

   ```text
   error: rustc 1.90.0 is not supported by the following packages:
     ripgrep@15.2.0 requires rustc 1.96
     grep@0.4.1 requires rustc 1.96
     … (eight grep* crates)
   ```

6. **Workaround, not a pin file.** `rustup toolchain install 1.96.0 --profile minimal`. Invoked `cargo +1.96.0`. Did **not** add `rust-toolchain.toml` to the clone.

7. **Ladder.** Dependencies resolved (already, on 1.90). Compile 10.93s. `--features pcre2` 4.08s. `rg --version` → `ripgrep 15.2.0 (rev 3fce3b5bb0)`, PCRE2 10.45 after the feature build. Search smoke: `fn main` at `crates/core/main.rs:44`. Workspace tests with pcre2: **1218 passed, 0 failed, 3 ignored, 24.47s**.

### What the skill changed vs an unprompted bootstrap

Without the skill: `cargo build` on PATH rustc, fight the error, maybe `rustup update`. With the skill's **step 1**, the 1.96 pin is already in `ci.yml` before any compile. The failure was **step 2's copy-paste command**, which can contradict step 1 and the prose ("compiler release in the build manifest").

### Defects found and fixed

| # | Severity | Defect | Fix |
|---|---|---|---|
| 1 | **Moderate** | Dedicated pin-file grep returning empty reads as "unpinned." The pin was `rust-version` in `[workspace.package]` and `rust: 1.96.0` in CI. Same silent-zero as runs 1–7, applied to toolchain pins. | Three-layer survey in `stack-detection.md`: pin file → manifest field (including workspace/root hoist) → CI toolchain install. `env-bootstrap` step 2 points there and says empty layer 1 is not unpinned. `ci-forensics` points at the same survey. |
| 2 | Minor | When layers disagree (macos CI nightly vs MSRV 1.96 vs local 1.90), no guidance. | Record all three. CI job for this OS = what the PR will run. Manifest field = floor. Do **not** invent a pin file. |
| 3 | Minor | `env-bootstrap` still hardcoded `.fde/` for the prerequisite and output. This run's workspace is `eval/workspaces/ripgrep/`. | Resolve via `workspace-conventions.md`; write `<workspace>/01-environment.md`. |

Not a fifth assumption class. It is the silent-zero family again: absence of the *conventional artifact* (`rust-toolchain.toml`) treated as absence of the *fact* (the compiler floor). Adding `rust-version` to the env-bootstrap grep would have fixed ripgrep and nothing else.

### Verification of the method

On this checkout, after the rewrite, the survey produces:

| Layer | Result |
|---|---|
| 1. Dedicated file | empty — no `rust-toolchain.toml` |
| 2. Manifest field | `rust-version = "1.96"`, `edition = "2024"` in `[workspace.package]` |
| 3. CI install | `rust: 1.96.0` (pinned job); `rust: nightly` (macos) |

That is enough to install 1.96.0 *before* debugging the compiler error. The 1.90 build was run only to confirm the gate is load-bearing.

### What this does not establish

One CLI crate, public crates.io, no internal registry, no service containers, no secrets. It does not test the enterprise path (Artifactory credentials, `settings.xml`, a compose stack). `unstable-index`, zsh completion, and `cross` were not run.

---

## Run 11 — CardDemo (COBOL / CICS / JCL)

**Date:** 2026-08-17 · **Subject:** `aws-samples/aws-mainframe-modernization-carddemo` @ `59cc6c2`, 329 files, full clone (not shallow)
**Why this subject:** CONTRIBUTING predicted a fifth class on mainframe/copybooks. Four prior recon stacks all had a package manifest. Artifacts: [`eval/workspaces/carddemo/`](eval/workspaces/carddemo/).

### Detection found a language mix. Everything after it assumed a packaged project.

| Check | As written, before this run | Reality |
|---|---|---|
| One-shot survey | **empty** — no pom / mix / Cargo / package.json | correct, and treated as "no stack" |
| Language mix (no case-fold) | 47 jcl + 8 JCL, 41 cpy + 21 CPY, 39 cbl + 5 CBL | **55** JCL, **62** copybooks, **44** COBOL |
| Config-driven heuristic (XML/YAML/JSON rival source) | **0** XML/YAML/JSON → not config-driven | Application is CSD + JCL + BMS + copybooks |
| No-language-section "declared start" | look in mix.exs / `[[bin]]` / `func main` | no manifest; **25** `DEFINE TRANSACTION`, **44** `PROGRAM-ID`, **128** `EXEC PGM=` |
| Filename conventions | `router.*`, `handlers/` | `app/csd/`, `app/jcl/`, `app/bms/`, `app/cpy/` |
| Stack-independent sweep | Dockerfile / cron YAML / k8s CronJob / CI `run:` | **0**. Scheduler is `app/scheduler/CardDemo.ca7` + `.controlm` (XML inside a non-`.xml` name, **15** `<JOB>`) |
| Persistence `CREATE TABLE` on `*.sql` / `*.cbl` | **0** | 8 VSAM `DEFINE FILE`, 78 copybook `01` levels, 3 `CREATE TABLE` in `*.ddl`, IMS `*.dbd` |
| Tests | 0 | 0 — actually true |
| CI | none | none — actually true |

The map the procedure would have produced: an unclassified tree with no entry points, no data store, and no schedule. That is a different product from a CICS credit-card system with 25 transactions, 55 batch members, and a VSAM file set.

### The fifth class

| Run | Lesson |
|---|---|
| 1 — Rust | Don't assume the **language** |
| 2 — .NET | Don't assume the codebase uses its **framework's vocabulary** |
| 3 — OFBiz | Don't assume the entry points are **in the code at all** |
| 4 — Elixir | Don't assume a **"generic" grep is stack-neutral** |
| 5 — COBOL | Don't assume the repository is a **packaged software project** |

Runs 1–4 all still had a `Cargo.toml`, `.sln`, `build.gradle`, or `mix.exs`. This one has none. The spine of stack-detection (manifest → lockfile → CI → `main()`) has nothing to attach to. The OFBiz heuristic almost applies — declarations live outside the procedure division — but it only fires on XML/YAML/JSON volume. CardDemo's declaration languages are JCL, CSD, BMS, and copybooks.

Adding `PROGRAM-ID` and `DEFINE TRANSACTION` to a list would have fixed CardDemo. The fix that generalizes:

1. **An empty one-shot survey is not a failed detection.** The case-folded language mix *is* the stack. "No package manager, no CI" is a finding.
2. **Declaration-driven means non-source artifacts rival the compiled language**, not "has a lot of XML." Count repeating keywords in *those* extensions (`DEFINE `, `EXEC PGM=`, `PROGRAM-ID`, `01 `).
3. **No manifest → skip `func main`.** Dominant extensions and their repeating tokens are the declared start.
4. **Scheduler exports are not only cron YAML.** Look in `scheduler/` for CA7, Control-M, Autosys.

### Verification of fixes

Re-ran the updated commands on the same checkout, no CardDemo-specific knowledge beyond "the top extensions are cpy/jcl/cbl/bms":

| Fix | Before | After |
|---|---|---|
| Case-folded mix | split cbl/CBL, cpy/CPY, jcl/JCL | 62 / 55 / 44 / 21 |
| Repeating tokens in dominant extensions | 0 entry points | 25 TRANSACTION, 26 PROGRAM, 8 FILE, 21 MAPSET; 44 PROGRAM-ID |
| `EXEC PGM=` | 0 batch | 62 IDCAMS, plus `CBTRN02C` / `CBACT04C` / `CBSTM03A` |
| Schema find includes `.ddl` / `.csd` / `.dbd` | 0 | 6 ddl, 4 csd, 4 dbd |
| `scheduler/` | 0 | CA7 + Control-M (15 jobs) |

### What this does not establish

329 files (under the skill's "just read it" threshold), a public AWS demo, no execution on a real region. It does not test generated-source or a low-code platform with *no* repository — those are still open fifth-class cousins. It does not test whether a COBOL section overfits the next mainframe shop's house JCL.

---

## Run 12 — kubernetes-client/python (generated OpenAPI client)

**Date:** 2026-08-17 · **Subject:** `kubernetes-client/python` @ `9c3456a`, 7,365 files (band 5k–50k), Python / setup.py / tox / openapi-generator
**Why this subject:** Run 11 left generated-source as an open cousin of class 5. This repo *looks* like a normal packaged Python library. Artifacts: [`eval/workspaces/k8s-python/`](eval/workspaces/k8s-python/). `context-strategy` ran first (prerequisite above 5,000 files).

### As written, the procedure maps a compiler output

| Check | As written | Reality |
|---|---|---|
| Stack | Python, `setup.py`, `requirements.txt` | correct |
| Shape | library (`packages=` in setup.py, no HTTP framework) | correct |
| Language mix | 1,916 py + 1,821 txt + 1,815 html + 1,690 md | most of the tree is generated docs + generated client |
| Entry points | `kubernetes/__init__.py` + 140 `if __name__` (examples) | those are real; **1,677** generated API/model files are not where you change the product |
| "Are the files authored?" | **no such check** | `.openapi-generator/FILES` × 2, swagger.json, "Do not edit the class manually" |
| Landmine grep `DO NOT` (case-sensitive) | **11** hits | **1,678** files with "Do not edit the class manually" |
| Tests | 72 test-dir paths, 625 `_test` | inflated by `doc/html` (94) and generated aio stubs (67). Authored tests are a few dozen |
| CI triage (`pytest`/`make` only) | `test.yaml` **0**; e2e-master **1** | real PR gate is `test.yaml` (`tox -e py`). After adding `tox ` / `python `, it ranks |

A map of `kubernetes.client.*Api` is a map of openapi-generator output. The handwritten system is `kubernetes/base`, `utils`, `informer`, and `scripts/update-client.sh`. The **canonical OpenAPI spec is the Kubernetes main repo**, not this tree.

CardDemo's method (non-source extensions rival source) does **not** fire. The dominant compiled-language extension *is* `.py`. The files look like source.

### The sixth class

| Run | Lesson |
|---|---|
| 1 — Rust | Don't assume the **language** |
| 2 — .NET | Don't assume the codebase uses its **framework's vocabulary** |
| 3 — OFBiz | Don't assume the entry points are **in the code at all** |
| 4 — Elixir | Don't assume a **"generic" grep is stack-neutral** |
| 5 — COBOL | Don't assume the repository is a **packaged software project** |
| 6 — generated client | Don't assume the files in the repository are the **source of truth** |

Class 5: no package; declarations *are* the authored application. Class 6: there *is* a package; the files you grep are a build product. Adding `.openapi-generator/` to a list would have fixed this repo. The fix that generalizes:

1. **Header density and generator metadata before mapping modules.** Count `generated by` / `do not edit` against the language-mix total. If most files match, split authored / generated / generated-docs.
2. **The working set is the authored remainder + the spec + the generate script.** Do not implement in generated files.
3. **Case-fold the landmine grep.** `DO NOT` misses "Do not edit." A four-digit generated-header count is a generation finding, not a todo list.
4. **Exclude generated paths from churn.** Regeneration is not business change.
5. **CI rank includes `tox ` and `python `.** A workflow that never says `pytest` was invisible.

### Verification of the method

On this checkout, after the rewrite:

| Check | Result |
|---|---|
| Generator metadata | `.openapi-generator/FILES` (1,677 × 2), `swagger.json` |
| Header density | **1,749 / 1,916** `.py` (~91%) |
| Authored library (not in FILES, not examples) | **176** files |
| CI rank | `e2e-master` 7, `e2e-release` 5, **`test.yaml` 3** (was 0) |

### What this does not establish

No `tox` run, no cluster. Low-code with *no* repository is still untested. This is one generator (openapi-generator); buf/protoc/SQLC trees may need the same density check against `.proto` / SQL, which the method names but did not execute.

---

## Run 13 — Claude trigger rematch (blocked)

**Date:** 2026-08-17 · **Method:** same 64-query suite as run 8. Judge was supposed to be `claude -p` so the number is comparable to run 4 (42/43 on Claude before the description edits).

**Result: no queries scored.** Auth and routing on this machine cannot reach an Anthropic model. Probe log: [`eval/claude-rematch-probe.json`](eval/claude-rematch-probe.json).

| Attempt | What happened |
|---|---|
| `claude -p` (default / `sonnet` / `opus` / `fable`) | Claude Code 2.1.174 is installed. `ANTHROPIC_BASE_URL` points at OpenRouter. Aliases remap to third-party ids (`inclusionai/ling-3.0-flash:free`, `zai-org/GLM-5.2-FP8`). Those ids return "may not exist or you may not have access." Same class of failure as run 8's judge note. |
| Unset the OpenRouter env and use Claude OAuth | `401 OAuth access token has been revoked.` |
| OpenRouter `chat/completions` with `anthropic/claude-sonnet-4.5` | Catalog lists 32 Claude ids. The env key returns `401 User not found`. |

This is **not** a rematch and it is **not** a trigger regression. Run 8 (`grok --single`: 43/43 + 10/10) still stands. Substituting Grok or a random OpenRouter chat model would have hidden exactly the Claude-only steal this run exists to find.

The runner now accepts the rematch as one command once a working Anthropic path exists:

```bash
python3 eval/run-trigger-eval.py --judge claude --out eval/trigger-results-claude.json
```

That uses `claude -p --bare` (no skills, no tools; description list only) and writes a separate file so run 8's Grok results are not overwritten.

**What you have to do on the machine:** restore Claude Code login (OAuth) *or* point `ANTHROPIC_*` at Anthropic rather than a dead OpenRouter remap. Then re-run the command above. Do not treat a third-party free model as Claude.

---

## Still untested

Honest coverage statement after thirteen runs.

**Well covered:**
- **Triggering** — Claude: 42/43 first-choice (run 4, pre-edit). After description edits, Grok: 43/43 + 10/10 regressions (run 8). Claude rematch **blocked** on this machine (run 13): OpenRouter remap + revoked OAuth + dead OpenRouter key. Not a score.
- **`repo-recon` and `stack-detection`** — five languages plus a generated-client tree (Rust, .NET, XML-configured Java, Elixir/Phoenix, COBOL/CICS/JCL, OpenAPI-generated Python)
- **Baseline comparison** — one task, one repo, one run. A data point, not a benchmark.

**Partially covered:**
- **`blast-radius`** — ring 1 and the grep-insufficiency caveat only. Rings 3–6 untested.
- **`env-bootstrap`** — one public Rust workspace through compile, test, and run. Pin-survey defect found and fixed. Internal registries, required services, and a blocked/partial outcome untested.
- **`characterization-tests`** — one Python function (`ordinalize`), in-memory seam, mutation + reachability checked. HTTP/DB seams and "introduce a seam" untested.

**Not covered — 36 of 43 skills.** Most are engagement-shaped: they need requirements, stakeholders, an environment, and a release decision that a cloned repository cannot provide.

**Remaining known gaps:**

- **No human check of a produced artifact.** The real test for a system map is whether someone who knows the codebase reads it and finds no material error. That needs a reader who knows the system, and it is the single most valuable test still outstanding.
- **One baseline comparison.** Enough to establish the skill changes the outcome; not enough to characterize by how much, or on which kinds of task.
- **Six classes found (runs 1–4, 7, 11, 12).** Remaining cousin: low-code platforms where there is no repository at all.

That last point is the honest summary of this document: every round of testing found something reasoning alone had missed, including defects the previous run did not make preventable.
