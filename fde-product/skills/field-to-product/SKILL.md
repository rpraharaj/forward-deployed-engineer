---
name: field-to-product
description: "Turn customer deployment evidence into a sanitized, reproducible product-gap proposal for a shared product team. Use when workarounds recur across deployments or a vendor FDE needs to feed field lessons into the product. A local handover belongs to handover-pack; routine bugs, sponsor status updates, and customer-specific feature delivery do not automatically need a product proposal."
---

# Field to product

Give a product team evidence it can use without exporting the customer's private context.

**Maturity:** experimental — an initial synthetic procedure trial is recorded; live engagement validation is still needed.

## When this applies / when it doesn't

Use for vendor/product-company FDE work when deployment evidence may justify a shared capability, reusable pattern, or documentation improvement. One customer's issue can be a useful signal, but recurrence must be evidenced rather than assumed.

Use core `handover-pack` for the receiving customer team and `stakeholder-brief` for a sponsor update. Stabilize an active incident with core `incident-triage` before preparing product feedback. Routine local fixes need their ordinary delivery path.

## Prerequisites

Resolve `<workspace>` first: use `FDE_WORKSPACE` if set; report an unavailable explicit path instead of falling back. Otherwise read the charter Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, use core `fde-orient`. Use the header in the output template below. Keep credentials and restricted customer material out of this artifact; retain only permitted synthetic examples or sanitized evidence references. Preserve prior evidence and unrelated sections when updating. These conventions are included here so this pack can be used without the core pack installed.

- A concrete observed limitation or workaround and its customer impact
- Product/version/configuration context and available evidence
- The permitted audience and restrictions on sharing, copying, or reusing customer assets

Unknown permission is a restriction to resolve. A contract, source code, dataset, log, or internal architecture diagram is not reusable merely because the FDE can access it.

## Procedure

### 1. Classify the field signal

Describe the user task, expected behavior, observed limitation, and workaround. Check whether an existing capability, supported configuration, documented extension, or training would resolve it. Separate a defect, documentation gap, product capability gap, and customer-specific requirement.

Record the product version and whether the behavior was reproduced. Cite code or observations; do not present a remembered conversation as confirmation.

### 2. Establish impact and recurrence

Record affected tasks, frequency, operating cost, risk, and maintenance burden using permitted aggregate evidence. Keep a single-customer observation distinct from independently observed recurrence. Do not invent the number of other customers who would benefit.

Describe the common constraint across occurrences and what remains customer-specific. Avoid combining unlike problems just because their workarounds look similar.

### 3. Build a shareable reproduction

Use synthetic inputs and the smallest permitted setup that demonstrates the limitation. State versions, configuration, expected result, actual result, and reproduction limits. If it cannot be reproduced outside a restricted environment, provide an approved redacted observation and label that limitation.

Check confidentiality, customer ownership, licensing, and sharing restrictions before moving material into a shared artifact. Keep restricted originals in their approved location. Sanitization alone does not establish permission to reuse code or data.

### 4. Frame the product decision

Explain the user problem, why the workaround is expensive, existing alternatives, the smallest useful shared capability, and compatibility/operational constraints. Include improving documentation or configuration as real options.

Distinguish a proposed reusable pattern from a production-supported product commitment. Name an appropriate product/engineering decision owner; if unknown, record the routing gap. Do not promise roadmap dates or represent the proposal as accepted.

### 5. Close the loop within the authorized audience

Prepare the proposal and any permitted reusable example. Sharing or publishing follows the user's authorization and the audience restrictions already established; this skill does not grant permission to expose a customer's material.

Record submitted, accepted, declined, or pending only when evidenced, with the receiving owner and next review. Link customer-facing follow-up to core `stakeholder-brief` if needed. Product implementation is separate work grounded through core `requirements-to-spec` and `solution-design`.

**Stop** when the signal, impact, reproducible or restricted evidence, sharing boundary, product decision, and owner/next action are recorded. Feedback prepared is not a product improvement shipped.

## Output template

Write `<workspace>/product-feedback/<topic>.md`:

```markdown
# Product feedback — <problem>

**Engagement:** <approved alias>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft | submitted | accepted | declined | superseded
**Source revision:** <product/repo>@<SHA>, or "no repository yet"
**Confidence:** <reproduced vs. reported; recurrence limits>

## Audience and reuse boundary
**Permitted audience:** <roles/team> · **Permission evidence:** <approved reference>
**Restricted originals:** <location only> · **Excluded material:** <what cannot move>

## Signal
**User task:** <task> · **Classification:** <defect/docs/config/capability/customer-specific>
**Expected/actual:** <behavior> · **Version/configuration:** <context>

## Impact and recurrence
| Observation | Evidence | Impact/maintenance cost | Shared constraint | Limits |
|---|---|---|---|---|

## Reproduction
<Synthetic setup, exact steps, expected/actual result; or permitted observation and limits.>

## Decision requested
**Proposal:** <small shared improvement> · **Alternatives:** <including existing capability>
**Compatibility/operations:** <constraints> · **Decision owner:** <role or unknown>

## Follow-up
| Date | Submitted/decided by | Evidence | Next action/owner/review date |
|---|---|---|---|
```

## Common traps

- Copying client code into a reusable example without permission
- Calling one observation a market-wide requirement
- Sending a feature wish without a reproducible limitation or impact evidence
- Creating a shared abstraction for constraints unique to one customer
- Promising a roadmap outcome before the product team has decided
