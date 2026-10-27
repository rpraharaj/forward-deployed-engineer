# Forward Deployed Engineer Skills & Playbooks

**50 agent skills across seven packs for forward deployed engineers delivering in unfamiliar organizations and systems.**

FDE Skills is an open-source toolkit for customer discovery, codebase onboarding, enterprise integration, production delivery, AI evaluation, adoption, and handover. Each skill defines a repeatable procedure and a durable artifact, with evidence and explicit limits.

The instructions use the [Agent Skills format](https://agentskills.io/specification). Use them with a coding agent that can read the skills and access the files and tools needed for the task. Codex has a local installation route; Claude Code is an optional plugin integration. Discovery, permissions, and automatic context loading differ—see the [integration guide](docs/integrations.md) and [recorded validation](VALIDATION.md).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-50-blue)
![Packs](https://img.shields.io/badge/packs-7-blue)

[Quick start](#quick-start) · [How to use](#how-to-use-the-skills) · [Skill packs](#fde-skill-packs) · [Troubleshooting](#troubleshooting) · [Testing](#testing-and-limitations)

## What is a forward deployed engineer?

A forward deployed engineer (FDE) works closely with customer or business teams to turn an operational problem into a usable production solution. The work can include discovery, technical scoping, software and data integration, deployment, adoption, and feeding field lessons into a shared product. Responsibilities vary by organization.

This toolkit supports that delivery work. It is also useful to customer-facing software engineers, technical consultants, and solutions engineers implementing systems. These are agent instructions and practical playbooks, not a course or certification.

## Quick start

Clone the library, then install core into the project where you will work. The installer needs Python 3.10+ and no third-party packages:

```bash
git clone https://github.com/rpraharaj/forward-deployed-engineer.git
python3 forward-deployed-engineer/scripts/install-skills.py \
  --dest /path/to/your-project/.agents/skills --packs fde-core
```

For Codex, open that project and invoke a skill in the conversation:

```text
$fde-orient I've inherited this payments service. Help me scope a currency-refund change before estimating it.
```

Or describe the situation and let the agent select an available skill. Automatic selection depends on the host and its configuration. `fde-orient` opens or resumes the engagement, identifies the work, and recommends the next installed skills.

Add packs when the work needs them. For example, install core and the AI pack into the same destination:

```bash
python3 forward-deployed-engineer/scripts/install-skills.py \
  --dest /path/to/your-project/.agents/skills --packs fde-core fde-ai
```

The installer copies complete skill folders and shared resources. It skips identical folders, preserves unrelated skills, and refuses conflicting files or links before installing anything. Copies are snapshots; see [updating an installation](docs/integrations.md#updating-an-installation) before refreshing changed skills. No global agent configuration or project instruction files are modified.

For Claude Code, use the [optional plugin installation](docs/integrations.md#claude-code-optional-plugin-integration). For other agents, consult their skill discovery rules or explicitly read the skill and its references from the checkout. Keeping the full resource layout matters; copying only `SKILL.md` breaks shared references.

## How to use the skills

1. **Open the working project.** Start the agent in the customer/application repository where you installed the skills. The library checkout supplies instructions; your working project supplies the system to investigate.
2. **Choose a starting point.** Use `fde-orient` for an unclear engagement, `repo-recon` for an unfamiliar codebase, or the [skill reference](USAGE.md#skill-reference) for a specific task. Describe the situation naturally, or explicitly select a skill. In Codex, type `$skill-name` in the conversation; this is not a shell command.
3. **Supply the goal and boundaries.** State what you need, what evidence and access are available, what actions are allowed, and what is out of scope. Point to existing notes. Agree the workspace location and whether its artifacts should be committed or ignored.
4. **Review the artifact.** Check source citations, assumptions, unverified claims, and owner questions. A draft plan or an unrun check must remain labelled that way.
5. **Continue or resume from the files.** Choose the next skill for the unresolved question. In a fresh session, explicitly read the charter, working guide, and relevant artifacts before continuing.

### Worked example: assess a refund change

Start with this prompt in Codex, after installing core:

```text
$fde-orient I'm assessing an unfamiliar billing service for multi-currency refunds.
The goal is a grounded scope and feasibility assessment before implementation.
Repository inspection and local notes are allowed; production access is unavailable.
Use .fde/ for the engagement. Ask about any missing scope or ownership facts.
```

Once the charter is written and its open questions are recorded, continue:

```text
$repo-recon Use .fde/00-engagement.md to map this service: entry points,
persistence, dependencies, test coverage, and risky areas for the refund change.
Record evidence and gaps. Do not implement the change.
```

Expected outputs under the agreed workspace:

```text
.fde/
├── 00-engagement.md   # goal, scope, access, owners, and next steps
├── 02-system-map.md   # repository findings and evidence limits
└── repo-guide.md      # only when no suitable existing working guide exists
```

Review the map before estimating: where does a refund enter, what stores its state, and which dependencies remain unverified? Clarify the required behavior with `requirements-to-spec`, then use `feasibility-probe` against that specification and the map. The findings depend on the actual repository; this example does not establish that currency conversion already exists or that a delivery date is feasible.

For an external workspace, manual invocation, session handoff, and the complete walkthrough, see the [detailed user guide](USAGE.md).

<a id="whats-in-the-box"></a>

## FDE skill packs

Install core for the general delivery lifecycle and add the packs relevant to the engagement. The pack folders are the canonical source; integrations use the same instructions.

| Pack | Skills | Supports |
|---|---:|---|
| [fde-core](fde-core/skills) | 34 | Orientation, discovery, requirements, comprehension, design, safe changes, verification, release, outcomes, adoption, and handover |
| [fde-data](fde-data/skills) | 3 | Data archaeology, pipelines, and database changes |
| [fde-migration](fde-migration/skills) | 4 | Dependency upgrades, refactoring seams, cutover, and decommissioning |
| [fde-platform](fde-platform/skills) | 3 | Enterprise integration, contracts, and vendor platforms |
| [fde-operate](fde-operate/skills) | 3 | CI diagnosis, observability, and post-deployment watch |
| [fde-product](fde-product/skills) | 1 | Turning permitted field evidence into a product decision request |
| [fde-ai](fde-ai/skills) | 2 | AI workflow evaluation and boundaries on agent actions |

Browse the [full skill catalog and engagement workflows](USAGE.md). A small, clear engineering task does not need every stage below.

| FDE responsibility | Representative skills | Example artifact |
|---|---|---|
| Understand the customer problem | `workflow-discovery`, `use-case-selection` | Workflow map and opportunity comparison |
| Learn an unfamiliar system | `context-strategy`, `repo-recon`, `trace-the-flow` | System map and working guide |
| Scope and design the work | `requirements-to-spec`, `feasibility-probe`, `solution-design` | Acceptance criteria, feasibility evidence, ADR |
| Implement and integrate safely | `safe-change`, `integration-adapter`, `db-change-management` | Change evidence and migration plan |
| Verify and release | `verification-plan`, `release-readiness`, `deploy-runbook` | Verification record and rollback procedure |
| Evaluate AI behavior | `ai-evaluation`, `agent-action-safety` | Task-quality gates and executor-effect evidence |
| Support sustained use | `adoption-plan`, `outcome-measurement`, `handover-pack` | Pilot, outcome readout, and continuation brief |

## Example FDE workflows

**An unfamiliar enterprise integration.** Start with “We need to connect this billing system to a new payments provider.” Orient the engagement, map the relevant flow, specify the contract, probe feasibility, and plan the change and release. Use `fde-platform` for integration and contract work. The result includes a grounded specification, evidence about the affected code, and a deploy/rollback runbook.

**An AI customer workflow.** Start with “Which support task should we automate, and what would count as a safe result?” Discover the current process, select a bounded use case, and establish an outcome baseline. Design and build the workflow, then evaluate task outcomes and any agent action boundaries before the release decision. Use `fde-ai`; a favorable average cannot waive a mandatory safety gate. Pilot adoption and measure business outcomes separately.

**A deployed tool that people rarely use.** Start with “The tool works technically, but users still do the task in a spreadsheet.” Investigate access and workflow friction with `adoption-plan`, define support and fallback, and measure successful tasks with an eligible-population denominator. `outcome-measurement` distinguishes observed handling-time changes from realized financial benefit.

The [usage guide](USAGE.md) covers 15 engagement archetypes and how the procedures compose.

## How the skills work

- **Artifacts survive the conversation.** Skills write to a resolved engagement workspace: `.fde/` by default, an explicit `FDE_WORKSPACE`, or another location recorded in the charter. They preserve prior evidence when updating it.
- **Claims carry evidence.** Cite source locations or command results and label `[confirmed]`, `[inferred]`, and `[unverified]`. An empty search is a coverage limit, not proof of absence.
- **Context is portable.** Preserve the team's existing working guide, such as `AGENTS.md`, `CLAUDE.md`, or another designated file. When none exists, use `<workspace>/repo-guide.md`. Record and read the guide explicitly; automatic loading is host-specific.
- **Tools are capabilities, not prerequisites to invent.** Use local files, Git, and a shell where the task needs them. Network integrations, subagents, and built-in review commands are optional. Skills do not grant new permissions or replace organizational controls.

Read the [portfolio design and artifact conventions](DESIGN.md) for the reasoning behind these choices.

<a id="validated-not-vibed"></a>

## Testing and limitations

The portfolio has been exercised against unfamiliar Rust, .NET, Java/XML, Elixir/Phoenix, and COBOL/CICS/JCL systems, plus a generated OpenAPI client. Those runs exposed assumptions about languages, frameworks, configuration, and where the source of truth lives. Coverage varies by skill; these were not trials of every procedure.

Seven newer procedures have initial synthetic artifact trials: workflow discovery, opportunity selection, outcomes, adoption, field-to-product feedback, AI evaluation, and agent action safety. All met their scenario checks; three optional skills were also retested without core files. They remain **experimental** pending live engagement validation. Baselines already handled most scenario decisions well.

Two [native Codex CLI trials](VALIDATION.md#run-17--agent-neutral-procedures-and-native-codex-trials) exercised four core procedures: preserving an existing working guide and creating a portable guide when none existed. A successful installation does not prove that all 50 skills behave identically in every host. Cursor and other hosts require their own runtime trials before claiming tested support.

Historical trigger results apply to the earlier 43-skill catalog and original evaluation method. They are retained in the [validation history](VALIDATION.md), not presented as a current score for the 50-skill catalog. Current checks cover catalog metadata, references, installer behavior, and evaluator regressions; runtime evidence is explicitly scoped.

## FAQ

**Is this tied to Claude Code?** No. The procedures and artifacts are agent-neutral. The Claude plugin marketplace is one optional packaging route; the local installer provides a separate route for Codex and other compatible skill directories.

**Which skills should an FDE start with?** Use `fde-orient` for an unclear engagement, `repo-recon` for an unfamiliar codebase, or a more specific skill when the task is already bounded. Core contains 34 skills; optional packs add specialized procedures.

**Does this require external accounts or MCP servers?** The library itself does not. A particular task may need authorized access to the system it investigates. Missing access or tools become explicit blockers; they are not silently assumed or installed.

**Can I use the playbooks without native skill support?** Read the relevant `SKILL.md` and its referenced files from the checkout and follow the procedure with available tools. This is manual use, not a claim of automatic discovery or equivalent behavior on an untested agent.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Skill is missing from the agent | Open the intended project, check its skill directory and installed pack, then restart the session or inspect the host's skill list. Use explicit invocation to distinguish discovery from automatic matching. |
| A shared reference is missing | Install complete folders and `_shared/`; copying only `SKILL.md` is insufficient. See the [integration guide](docs/integrations.md). |
| Installer reports a conflict | Preserve existing files. Follow the [update procedure](docs/integrations.md#updating-an-installation); do not delete the whole skill directory or unrelated team skills. |
| Notes are missing or written in an unexpected place | Check `FDE_WORKSPACE` and the charter's recorded Location. An explicitly configured but unavailable path is a blocker, not a reason to silently create another workspace. |
| The procedure needs unavailable evidence or access | Record what is blocked, its owner, and the next permitted step. A reduced-confidence investigation cannot waive a required control. |

See [detailed troubleshooting](USAGE.md#troubleshooting) for checks and recovery steps.

## Contributing

The most useful contribution is a concrete case where a procedure gave the wrong answer. Try an unfamiliar stack, review an artifact against a system you know, or test another agent's installation and workflow behavior. Report the inputs, version, actual outcome, and limits.

Use the [cold-start report template](.github/ISSUE_TEMPLATE/cold-start-report.md) and read the [contribution and validation guide](CONTRIBUTING.md). Keep skills focused, references discoverable, and every quality claim tied to recorded evidence.

## Prior art and license

The procedures draw on Michael Feathers' characterization testing and seams, Martin Fowler's migration patterns, and Michael Nygard's ADR practice.

[MIT](LICENSE). Use, adapt, and contribute the toolkit under the license terms.
