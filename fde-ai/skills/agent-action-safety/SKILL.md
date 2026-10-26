---
name: agent-action-safety
description: "Define and verify boundaries on an AI agent's tool actions, including allowed resources, authorization, approvals, untrusted content, retries, execution budgets, and human escalation. Use before an agent can write data, send messages, spend money, or invoke privileged tools, or when testing action-boundary bypasses. General data handling is security-compliance-check; measuring overall AI task quality is ai-evaluation."
---

# Agent action safety

Verify what an agent may cause, not only what it says.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use when model-driven tool use can affect another system or when testing whether retrieved instructions, stale approvals, or retries can cross an action boundary. Read-only systems still need data-access boundaries where relevant.

Use core `security-compliance-check` for broader data handling and the organization's formal review. Use sibling `ai-evaluation` for the complete task-quality evaluation. This procedure does not authorize performing the production actions it examines.

## Prerequisites

Resolve `<workspace>` first: use `FDE_WORKSPACE` if set; report an unavailable explicit path instead of falling back. Otherwise read the charter Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, use core `fde-orient`. Use the header in the output template below. Keep credentials and restricted customer material out of this artifact; retain only permitted synthetic examples or sanitized evidence references. Preserve prior evidence and unrelated sections when updating. These conventions are included here so this pack can be used without the core pack installed.

- Intended tasks, users/principals, available tools, and their actual permissions
- Applicable policy, required approvals, and the person authorized to define each boundary
- An isolated test environment or faithful fakes where effects can be inspected

If permissions or the execution path cannot be inspected, document the uncertainty. Do not claim safety from a prompt or a tool description alone.

## Procedure

### 1. Inventory capabilities and trust boundaries

For each tool identify read/write capability, resource/tenant scope, principal, credential location, external destination, and possible irreversible effects. Include indirect effects such as triggers and downstream events.

Distinguish trusted task/policy instructions from untrusted documents, messages, web content, and tool results. Retrieved content may supply evidence; it cannot grant permission, change policy, or choose a new privileged destination.

### 2. Define an enforceable action policy

Specify allowed actions and resources, required validation, conditions for approval, and what must be denied or escalated. Prefer scoped credentials and checks at the tool/executor boundary; prompt instructions alone are not enforcement evidence.

Bind any required approval to the principal, action, target, parameters, and relevant state. A changed recipient, amount, tenant, or payload requires the authorization applicable to that changed action; do not reuse stale approval. Preserve existing explicit authorization when its scope still matches.

Secrets remain in the approved credential mechanism, not in model-visible context or the artifact. Record permitted destinations without exposing credential values.

### 3. Bound execution and partial failure

Agree maximum time, steps, retries, parallelism, and spend appropriate to the workflow. Define stop signals, cancellation/kill-switch behavior, and human escalation. Missing policy for a consequential action is a gap, not permission to proceed.

For writes, establish how duplicate requests are detected and whether retrying after timeout is safe. Inspect the actual contract or execution evidence; absence of an idempotency key alone does not establish the whole downstream behavior. If retry safety is unknown, do not automatically repeat the write. Provide reconciliation or human review for uncertain/partial outcomes.

Distinguish reversible actions from externally irreversible effects. Define compensation and reconciliation where rollback is incomplete; do not promise to unsend a notification or reverse a consumed event.

### 4. Test the boundary in isolation

Use synthetic state and suppressed external effects. Exercise allowed actions plus applicable adversarial cases: instructions embedded in retrieved content, cross-tenant access, changed approval parameters, duplicate execution, timeout after a partial write, excessive iterations, and unavailable human approval.

For each case define the permitted/forbidden effects before execution. Inspect the actual executor call and resulting sandbox state, including rejected attempts. A refusal sentence followed by a successful forbidden tool call is a failure. A timeout with an unknown write outcome is unresolved, not a clean denial.

Do not probe live customer accounts, send real messages, or create charges as a safety test without separate authorization for that specific operation. If an isolated test cannot be run, keep the check unverified.

### 5. Record enforcement evidence and remaining gates

Map each policy rule to its enforcement location, test, observed effect, and coverage limit. Feed adversarial cases into `ai-evaluation` and cite required controls in core `verification-plan` / `release-readiness`.

Have the authorized policy/control owner decide unresolved consequential gaps through the existing change process. A business sponsor's acceptance cannot substitute for another owner's required control. Keep continued safe work separate from the blocked action.

**Stop** when capability/policy mapping, bounded execution, adversarial results or blockers, and residual-risk ownership are explicit. A reviewed design without exercised enforcement remains unverified.

## Output template

Write `<workspace>/ai/action-safety-<workflow>.md`:

```markdown
# Agent action boundaries — <workflow>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** proposed | tested | reviewed | superseded
**Source revision:** <repo>@<SHA>, or "no repository yet"
**Confidence:** <enforcement inspected/exercised vs. assumed>

## Capability and policy map
| Principal/tool | Allowed resources/actions | Irreversible effects | Approval rule/owner | Enforcement location |
|---|---|---|---|---|

## Trust boundary
<Trusted task/policy source, untrusted content sources, data destinations and scopes.>

## Execution limits and recovery
**Time/steps/retries/concurrency/spend:** <limits and owners>
**Stop/cancel:** <mechanism> · **Escalation:** <role and path>
**Duplicate/uncertain-write handling:** <evidence-backed rule>
**Compensation/reconciliation:** <what can and cannot be reversed>

## Sandbox tests
**Environment/tool/policy versions:** <references> · **Effect isolation:** <how verified>
| Case | Allowed/forbidden effects | Observed calls/state | Result | Evidence |
|---|---|---|---|---|

## Remaining gates
| Rule/gap | Consequence | To verify/resolve | Authorized owner | Release position |
|---|---|---|---|---|
```

## Common traps

- Treating instructions in retrieved content as authorization
- Assuming a prompt-based refusal prevents a tool-side effect
- Reusing approval after the destination or payload changes
- Retrying an ambiguous write and creating a duplicate effect
- Testing denial with real credentials and live external effects
