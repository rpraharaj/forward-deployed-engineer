<div align="center">

# FDE Skills

**Claude Code skills for engineers who get dropped into someone else's codebase and have to deliver.**

From a vague ask to something running in production — on a stack you didn't choose, in a system nobody documented, with Claude Code as your only tool.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-50-blue)
![Packs](https://img.shields.io/badge/packs-7-blue)
![Cold-start tested](https://img.shields.io/badge/cold--start%20tested-5%20stacks-brightgreen)
![Historical Claude trigger](https://img.shields.io/badge/historical%20Claude%20trigger-42%2F43-lightgrey)

[Quick start](#quick-start) · [The skills](#whats-in-the-box) · [Why it's tested](#validated-not-vibed) · [Contributing](#contributing)

</div>

---

## The problem

You start Monday at a bank, an insurer, a telco. They put you on a fifteen-year-old billing system. The team that built it left. There's no documentation, the wiki is from 2019, and someone wants an estimate by Thursday.

**Your bottleneck is never writing code.** Claude can already write the service. What it can't do — and what nobody has written down — is the *procedure* for building an accurate mental model of an unfamiliar system fast enough that a team who didn't ask for you starts trusting your judgment.

That's what this is. 50 skills encoding what an experienced forward deployed engineer actually does, and the artifacts that make the work survive their departure.

---

## Quick start

```bash
git clone https://github.com/rpraharaj/forward-deployed-engineer.git
claude plugin marketplace add ./forward-deployed-engineer
claude plugin install fde-core@fde-skills
```

Then just describe your situation. No need to name a skill:

> *"I've been dropped into a payments service I've never seen and they want multi-currency refunds by Q3."*

`fde-orient` opens the engagement, classifies it, and tells you what to run next.

**Install `fde-core` always. Add the pack that matches the work:**

```bash
claude plugin install fde-data@fde-skills        # ETL, warehouse, schema change
claude plugin install fde-migration@fde-skills   # replatform, EOL upgrade, cutover, decommission
claude plugin install fde-platform@fde-skills    # integration, contracts, SAP/Salesforce/ServiceNow
claude plugin install fde-operate@fde-skills     # pipelines, post-deploy watch, observability
claude plugin install fde-product@fde-skills     # permitted customer lessons for a shared product
claude plugin install fde-ai@fde-skills          # AI workflow evaluation and agent action boundaries
```

For local development without installing, start a session with `claude --plugin-dir ./forward-deployed-engineer/fde-core`; repeat `--plugin-dir` for each optional pack. The marketplace path above is local to your clone; refresh its catalog with `claude plugin marketplace update fde-skills` when pulling changes. See the [Claude plugin reference](https://code.claude.com/docs/en/plugins/cli-reference).

The split isn't cosmetic. Skill descriptions load into context **every session** whether they fire or not. Install what the engagement needs: core has 34 skills; the six optional packs add 16.

---

## What's in the box

<table>
<tr><td width="50%" valign="top">

**LAND** — arrive and orient
`fde-orient` · `access-and-onboarding`
`context-strategy` · `env-bootstrap`
`repo-recon` · `ownership-map`
`knowledge-interview`

**FRAME** — work out what's actually being asked
`workflow-discovery` · `use-case-selection`
`outcome-measurement`
`requirements-to-spec` · `feasibility-probe`
`estimation` · `delivery-plan`

**UNDERSTAND** — only where the change lands
`trace-the-flow` · `blast-radius`
`git-archaeology` · `data-archaeology`

**DESIGN**
`solution-design` · `contract-design`
`nfr-baseline`

</td><td width="50%" valign="top">

**BUILD**
`safe-change` · `characterization-tests`
`refactor-seams` · `integration-adapter`
`dependency-upgrade` · `db-change-management`
`data-pipeline-work` · `cots-configuration`

**VERIFY**
`verification-plan` · `test-data-strategy`
`nfr-validation` · `security-compliance-check`
`ci-forensics`

**SHIP**
`release-readiness` · `deploy-runbook`
`cutover-plan` · `change-control-navigation`
`post-deploy-watch` · `decommission-plan`

**SUSTAIN**
`incident-triage` · `observability-gap`
`handover-pack` · `enablement-handoff`
`adoption-plan`

**PRODUCT & AI** — optional engagement-specific procedures
`field-to-product` · `ai-evaluation`
`agent-action-safety`

**ACROSS EVERYTHING**
`stakeholder-brief` · `escalation-and-renegotiation`

</td></tr>
</table>

**Seven new procedures are experimental:** workflow discovery, use-case selection, business outcomes, end-user adoption, field-to-product feedback, AI evaluation, and agent action safety. All seven passed their initial synthetic scenario checks; three optional skills also passed isolated retests after a convention dependency was fixed. [Results and limitations](VALIDATION.md#run-16--seven-synthetic-procedure-trials) are recorded; these trials do not establish field effectiveness.

📖 **[USAGE.md](USAGE.md)** — first-day walkthrough, full reference, workflows by engagement type

---

## Three ideas hold it together

**Artifacts, not conversations.** Every skill writes a file to a `.fde/` workspace. Work that lives only in a chat transcript evaporates — and as an FDE, you always leave.

**Evidence or a confidence tag.** Every claim carries a `file.java:88` citation or one of `[confirmed]` / `[inferred]` / `[unverified]`. This is the difference between being trusted in week two and being quietly routed around after being confidently wrong once.

**Skills compose.** Each reads what the previous ones wrote. `feasibility-probe` reads the system map and the spec instead of re-deriving them.

📖 **[DESIGN.md](DESIGN.md)** — the lifecycle model, 12 engagement archetypes, and why the portfolio is shaped this way

---

## Validated, not vibed

Most skill collections ship on the author's confidence. This one was pointed at real, unfamiliar codebases to find out where it was wrong. **It was wrong ten times.**

Six cold-start runs, each against a deliberately different stack — and each found a class of assumption the previous fix did not prevent:

| Run | Subject | What broke |
|---|---|---|
| **1** | Rust workspace (`dbt-core`) | Entry-point search found **5** of **61**. Hardcoded Java/JS patterns. → *Don't assume the **language**.* |
| **2** | .NET monolith (`nopCommerce`) | Framework search found **0** scheduled tasks; the app has **39** behind its own interface. → *Don't assume the codebase uses its **framework's vocabulary**.* |
| **3** | XML-configured Java (`Apache OFBiz`) | Every route search returned **0**. The system declares **3,113** routes in XML. → *Don't assume the entry points are **in the code at all**.* |
| **4** | Elixir/Phoenix (`plausible/analytics`) | Stack detected; "generic" greps returned **0**. The app has **216** Phoenix routes and **24** Oban workers. → *Don't assume a **generic grep is stack-neutral**.* |
| **5** | COBOL / CICS / JCL (`CardDemo`) | No manifest, **0** XML. Procedure reported no entry points. The app has **25** CICS transactions, **55** JCL members, **62** copybooks. → *Don't assume the repository is a **packaged software project**.* |
| **6** | Generated OpenAPI client (`kubernetes-client/python`) | 1,916 `.py` files, real `setup.py`. **91%** say do not edit. Canonical spec is another repo. → *Don't assume the files in the repository are the **source of truth**.* |

Run 3 tested a prediction written down after run 2. It was correct — **and the fix still couldn't have been written without running the test.** That's the argument for this whole section.

Every fix is a *method*, never a pattern. Adding `IScheduleTask` to a .NET list would have fixed one repo; teaching the skill how to *find* a codebase's own abstraction fixed the class.

**Also measured:**
- **Triggering** — 54 queries against all 43 descriptions: **42/43** first choice on Claude (run 4). After later description edits: **43/43** plus **10/10** regression probes on Grok (run 8). Claude rematch **blocked** (run 13) — CLI remaps to OpenRouter and OAuth is revoked; not a score. **Zero** false fires on near-miss queries like *"help me write a cover letter."*
- **Baseline comparison** — same task with and without the skill. The baseline was good, and it claimed the codebase shipped one binary. It declares **nine**.
- **`env-bootstrap`** — first full build/test/run, on `ripgrep`. The dedicated pin-file grep returned **nothing**; the pin was `rust-version = "1.96"` in `Cargo.toml` and `rust: 1.96.0` in CI. Compile on the machine's `rustc 1.90.0` failed as cargo promised. 1.96.0: **1218** tests passed.

📖 **[VALIDATION.md](VALIDATION.md)** — every run, every defect, and an explicit list of what still isn't tested

The model scores above are historical and refer to the earlier 43-skill catalog. The October 2026 audit found malformed runtime metadata and permissive evaluator parsing; both are repaired, with native plugin validation and offline regressions recorded in [run 14](VALIDATION.md#run-14--local-audit-and-evaluator-regressions). The seven additions have a separate validation record; do not apply the old scores to the 50-skill catalog.

> **What this doesn't claim.** The skills don't make Claude smarter about your codebase. They add provenance, declared limits, and better accuracy on the steps the procedure forces. That's a narrower claim than most skill repos make, and it's the one the evidence supports.

---

## Contributing

**Contributions are genuinely wanted, and the most valuable one isn't code.**

### 🔬 Run a cold-start test (start here)

Every round of testing found something reasoning alone had missed. Five languages plus a generated-client tree are covered. Many aren't.

Point `repo-recon` at a real codebase in a stack we haven't tried — **Salesforce/Apex, low-code, embedded C, anything where there is no repository** — and tell us where it produced a wrong answer. A one-paragraph issue saying *"it found 4 entry points, there are 200, here's why"* is worth more than a new skill.

Use the [cold-start report template](.github/ISSUE_TEMPLATE/cold-start-report.md). Six classes so far. Low-code with no repo is still open.

### 🧭 Tell us when a procedure didn't fit

Used a skill on a real engagement and the steps were wrong for your situation? That's the highest-signal feedback available. Four skills have documented repository-based procedure trials, at least partially, and seven others have synthetic artifact trials; 39 of 50 have no recorded procedure trial. These are not a substitute for live engagement validation. Open an issue.

### ✍️ Write or improve a skill

The house style is in [DESIGN.md §8](DESIGN.md). Two rules matter most:

1. **No stack specifics in a `SKILL.md` body.** Maven, npm, and pytest belong in `references/`, loaded on detection. Three of our ten defects were violations of this.
2. **Explain *why*, don't issue rules.** A skill that says "always do X" gets followed mechanically. One that explains what goes wrong without X gets applied with judgment.

### 📦 Propose a new pack

Industry verticals (`fde-fintech`, `fde-healthcare`), regional compliance regimes, or platform-specific packs are all sensible extensions.

📖 **[CONTRIBUTING.md](CONTRIBUTING.md)** — full guide, PR checklist, how to run the trigger evals

---

## Prior art and thanks

Standing on the shoulders of Michael Feathers (*Working Effectively with Legacy Code* — the seam-finding and characterization-test patterns), Martin Fowler (strangler fig, branch by abstraction), and the ADR practice popularized by Michael Nygard.

Built with [Claude Code](https://claude.com/claude-code).

---

## License

[MIT](LICENSE) — use it, fork it, take it into your client work, sell consulting built on it. No attribution required, though a star is appreciated if it saved you a week.
