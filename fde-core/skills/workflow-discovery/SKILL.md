---
name: workflow-discovery
description: "Map how people actually carry out a business process by walking real cases, handoffs, waits, exceptions, and workarounds. Use when the current process is disputed or undocumented, users rely on email or spreadsheets, or the problem needs understanding before requirements are chosen. Following a code execution path is trace-the-flow; specifying an already-selected change is requirements-to-spec."
---

# Workflow discovery

Find the work before designing the change.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use for an unclear current business process, disagreement about where delay occurs, or a workflow whose official diagram differs from everyday work.

For a clear ticket, use `requirements-to-spec`. For control flow inside software, use `trace-the-flow`. For a specific expert question, use `knowledge-interview`. Do not make discovery a gate on a small, already-understood change.

## Prerequisites

Resolve `<workspace>` using `../_shared/workspace-conventions.md`; use its header, privacy, and confidence conventions. Preserve earlier observations when updating an artifact.

- `00-engagement.md`, if available, to bound the process and purpose
- Access to a process participant or approved, sanitized examples of completed cases
- Existing process documents, if any, treated as claims to check

If direct observation is unavailable, build a provisional map from available evidence and label what needs checking. Do not fabricate interviews or observed timings.

## Procedure

### 1. Bound one process

Name its trigger, end condition, actors, and unit of work: for example, one supplier invoice from arrival to payment approval. Record excluded variants and the person who owns the process. A map of the whole department is too broad.

### 2. Walk cases with the people doing the work

Trace an ordinary completed case, then an exception or rework case where available. Ask the participant to explain what happened at each step and show only artifacts permitted by data policy. Record role, input, action, tool, output, recipient, and evidence.

Observe manual copying, offline decisions, duplicate entry, unofficial spreadsheets, and handoffs between teams. Use `knowledge-interview` for missing explanations; its output is optional, not a prerequisite for observing a case.

Do not copy customer records, screenshots containing personal data, or credentials into the workspace. Reference approved locations and synthesize examples.

### 3. Separate elapsed time from active work

For each step distinguish active handling time, waiting time, queue age, and rework. Capture the observation window, sample size, and source. A two-day approval wait is not two person-days of labor.

For estimates from participants, record the source and mark them inferred. Do not turn one observed case into a population average. Where time cannot be measured, record the gap and a feasible measurement method.

### 4. Explain exceptions and decision rights

Find who can approve, reject, override, or return work, what evidence they require, and what happens when a participant is unavailable. Preserve mandatory controls when identifying delay; a control is not removable merely because it is slow.

Separate the observed process, its documented intent, and suggested improvements. A workaround may protect a real constraint. Confirm its purpose before recommending removal.

### 5. Read the map back and identify opportunities

Ask the process owner and representative participants to correct the map when available. Record agreement, disagreement, and unanswered questions with confidence tags. Prepare questions or a draft summary; contacting people requires the user's authorization.

List opportunities with the step affected, pain evidence, constraints, and unknowns. Multiple competing opportunities go to `use-case-selection`; a chosen change goes to `requirements-to-spec`. Discovery does not authorize implementation.

**Stop** when the bounded process, an ordinary path, available exceptions, decision points, timing evidence or gaps, and opportunities are recorded. Do not keep interviewing to make every box look certain.

## Output template

Write `<workspace>/discovery/workflow-<name>.md`:

```markdown
# Workflow — <process>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | reviewed | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <observed vs. reported; coverage limits>

## Boundary
**Trigger:** <event> · **End:** <observable result> · **Unit:** <one case>
**Owner:** <role> · **Excluded:** <variants>

## Cases examined
| Case alias | Ordinary/exception | Evidence location | Window | Limits |
|---|---|---|---|---|

## Actual steps
| Step | Role | Input/action/output | Tool | Next recipient | Evidence/confidence |
|---|---|---|---|---|---|

## Time and rework
| Step | Active time | Wait | Rework | Sample/window/source | Confidence |
|---|---|---|---|---|---|

## Decisions and exceptions
| Condition | Decider | Required evidence/control | What actually happens | Unknown |
|---|---|---|---|---|

## Documented vs. observed
| Claim | Observation | Consequence | Who can resolve |
|---|---|---|---|

## Opportunities
| Step | Pain evidence | Possible improvement | Constraint | To investigate |
|---|---|---|---|---|

## Review and gaps
| Participant role | Correction/agreement | Date | Remaining question/owner |
|---|---|---|---|
```

## Common traps

- Mapping software screens while missing the human decisions between them
- Multiplying queue time by salary and calling it labor savings
- Treating the official diagram or one interview as observed reality
- Removing an approval without establishing why it exists
- Picking a technology while the actual bottleneck is still unknown
