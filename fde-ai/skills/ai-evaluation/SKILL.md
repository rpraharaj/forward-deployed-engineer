---
name: ai-evaluation
description: "Evaluate a delivered AI workflow or agent against representative task cases, grounded expectations, quality and safety thresholds, latency, and cost, with versioned regression evidence. Use when model-driven behavior needs acceptance evidence or a model/prompt/retrieval/tool change needs comparison. Ordinary software test planning is verification-plan; evaluating which FDE skill should trigger is outside this skill."
---

# AI evaluation

Test the delivered workflow under conditions that make its failures visible.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use for model-backed task quality, version comparisons, or regression checks after changes to prompts, models, retrieval, or tools. Evaluate the complete task boundary that matters to the user.

Use core `verification-plan` for ordinary acceptance coverage and core `nfr-validation` for infrastructure/load measurements. This skill does not score the FDE portfolio's skill-selection descriptions. Action permissions are defined by sibling `agent-action-safety`, whose cases can join this evaluation.

## Prerequisites

Resolve `<workspace>` first: use `FDE_WORKSPACE` if set; report an unavailable explicit path instead of falling back. Otherwise read the charter Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, use core `fde-orient`. Use the header in the output template below. Keep credentials and restricted customer material out of this artifact; retain only permitted synthetic examples or sanitized evidence references. Preserve prior evidence and unrelated sections when updating. These conventions are included here so this pack can be used without the core pack installed.

- An intended user task, acceptance criteria, and accountable quality/risk owner
- A runnable system or an explicit plan for blocked measurements
- Permitted task examples and an evaluation environment with isolated effects

Use existing runners and approved local models/services where available. No external provider or downloaded framework is required by this procedure. If execution is unavailable, produce the evaluation plan and mark all results unmeasured.

## Procedure

### 1. Define the task and release decisions

State the input population, expected end result, unacceptable failures, and thresholds with their owners. Include ordinary, difficult, ambiguous, insufficient-information, and forbidden-action cases as applicable. A high aggregate score cannot cancel a mandatory safety failure.

Separate user-task quality, factual grounding, required abstention/escalation, latency, and cost. Technical infrastructure measurements can be cited from core `nfr-validation` rather than duplicated.

### 2. Assemble a versioned case set

Use approved synthetic or sanitized cases, with provenance, expected outcomes/rubrics, important subgroups, and known sampling limits. Keep development examples separate from a held-out acceptance set. Do not tune on the acceptance cases and report the result as an independent measurement.

For retrieval, record source versions, permissions, freshness, missing-content cases, and whether failures occur before or after retrieval. Do not infer answer quality from retrieval similarity alone.

Keep personal data, credentials, private prompts, and raw sensitive traces in approved storage; artifacts contain references and redacted summaries.

### 3. Establish independent grading

Use deterministic checks where the outcome is checkable. For judgments, define an explicit rubric and obtain expert-labelled examples where available. Check any model grader against human-reviewed examples and record disagreements and limitations. The evaluated model's assertion that it succeeded is not ground truth.

For agents, inspect permitted environment state and tool effects as well as the response. Grade a failed or timed-out execution as a failure/error with evidence; do not silently exclude it or count it as abstention. Never recompute expected values from the candidate's answer.

### 4. Run a bounded, comparable experiment

Record case-set version, system revision, model identity/configuration, prompt/retrieval/tool versions, environment, grader version, trial count, and execution budget. Preserve raw evidence only where approved, with redacted references in the artifact.

Use repeated trials where variability matters, with the count and aggregation fixed before seeing results. Compare baseline and candidate under equivalent cases and conditions. Report failures by subgroup, not only an average; label small samples and uncertainty.

Run write-capable tools only against isolated state or faithful fakes with external effects suppressed. A test request is not permission to send messages, spend funds, or change production records. Reuse existing authorization and approved usage/spend/time limits; resolve missing authorization or budgets before paid or external execution, and define stop conditions.

### 5. Explain failures and gate changes

Separate source-data, retrieval, reasoning, tool/execution, grader, and workflow failures using the available evidence. Link actual defects to ordinary delivery work; keep the held-out set independent while adding representative regression cases.

State whether each required threshold is met, unmet, or unmeasured. Cite the result from core `verification-plan` and `release-readiness`; this evaluation supplies evidence, not permission to launch or waive a required control. Link business benefit separately to core `outcome-measurement`.

**Stop** when case coverage/limits, grading, configurations/budgets, results or execution blockers, and the threshold decision are recorded. A plan without executed trials remains a plan.

## Output template

Write `<workspace>/ai/evaluation-<workflow>.md`:

```markdown
# AI evaluation — <workflow>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** planned | executed | reviewed | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <case coverage, grading confidence, execution limits>

## Task and gates
| Task/population | Expected outcome | Quality/safety threshold | Owner |
|---|---|---|---|

## Cases and graders
**Case-set version/location:** <approved reference> · **Development/held-out split:** <method>
**Rubric/grader version:** <reference> · **Human calibration:** <sample and disagreements>
**Coverage and exclusions:** <ordinary, difficult, unknown, restricted; sampling limits>

## Run configuration
| System/model/config | Prompt/retrieval/tools | Environment/effect isolation | Trials/budget | Evidence |
|---|---|---|---|---|

## Baseline vs. candidate
| Metric/subgroup | Threshold | Baseline | Candidate | Sample/variability | Verdict |
|---|---|---|---|---|---|

## Failure analysis
| Case/trial | Observed outcome/effect | Failure class | Evidence | Next action |
|---|---|---|---|---|

## Decision and gaps
<Met/unmet/unmeasured gates, blockers, risk owner, and links to verification/release artifacts.>
```

## Common traps

- Grading an agent's claim instead of checking the resulting state
- Letting a model grader validate itself without independent examples
- Hiding critical-case failures in a favorable average
- Comparing runs with changed source data or execution conditions
- Running real write tools in an evaluation environment with live credentials

Optional background on task/trial/outcome terminology: [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents). Use an approved local copy when offline; the procedure does not require web access.
