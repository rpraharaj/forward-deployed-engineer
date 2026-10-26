---
name: trace-the-flow
description: Follow one concrete business operation end to end through every layer and process boundary - entry point, orchestration, persistence, messaging, downstream calls, and the error and retry paths - producing a sequence narrative with a citation at every hop. Use when you need to know how something actually works before changing it, when asked "what happens when a customer does X", when debugging behavior you cannot explain from reading one file, or when a change lands on a request path you have not walked. Traces one operation deeply rather than mapping the whole system - run repo-recon first for breadth.
---

# Trace the flow

Walking one operation from end to end.

## Why this exists

`repo-recon` tells you where things are. It does not tell you what actually happens, and in a layered enterprise system those are very different questions. The call path for "customer places an order" typically crosses eight files, two process boundaries, a transaction, a message queue, and three error handlers — none of which is visible from any single file.

The specific danger this skill addresses is **plausible reconstruction**. Reading a controller and a service, it's easy to assemble a mental model that is coherent, confident, and wrong — because the actual dispatch goes through a framework-configured interceptor, or an event listener registered in XML, or a strategy selected by a config value. That model then becomes the basis for a change, and the change breaks something invisible.

A trace with a citation at every hop is the antidote. Where you can't establish a hop, the trace says so rather than bridging the gap with a reasonable guess.

## When this applies

- Before changing anything on a request path you haven't walked
- "What happens when a customer does X?"
- Behavior you can't explain from reading one file
- Debugging where the symptom and the cause are in different components
- Understanding an integration before modifying it

## When it doesn't

- You need breadth, not depth — run `repo-recon`
- The system is small enough to read outright
- You need the data model rather than the control flow — that's `data-archaeology` *(fde-data)*; if unavailable, record the data-model gap rather than claiming a complete analysis.
- You need to know *why* the code is shaped this way — that's `git-archaeology`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/02-system-map.md` — you need to know the entry points before following one
- Ideally `<workspace>/01-environment.md` — being able to *run* the flow turns `[inferred]` hops into `[confirmed]` ones cheaply

## Procedure

### 1. Pick exactly one operation, named in business terms

Not "the OrderController" — **"a customer places an order with a saved card."**

Two reasons. A business-named trace is findable later by someone who doesn't know the class names, and it forces you to pick a *concrete* path rather than a general one. "Order placement" branches; "order placement with a saved card, in EUR, for an existing customer" does not.

Where variants matter, trace the main one and note the branch points. Tracing every variant at once produces a document nobody can follow.

### 2. Find the true entry point

From the system map. Be careful here: the apparent entry point is often not the first thing that runs. Filters, middleware, interceptors, and authentication layers execute before the handler, and they frequently do things that matter — tenant resolution, transaction demarcation, request mutation.

Check what's configured to run before the handler, not just the handler.

### 3. Follow each hop, citing as you go

At every step record: **what is called, where it's defined, what it does, and what it passes on.**

The discipline that makes this useful is refusing to skip. When you can't find where control goes next, you have hit indirection — read `references/following-indirection.md`, which covers dependency injection, dynamic dispatch, event buses, reflection, config-driven wiring, aspect-oriented interception, and code generation. Those mechanisms are why a call path disappears, and each has a way of being resolved.

If after that you still can't establish the next hop, **write the gap into the trace**:

> `OrderService:88` publishes `OrderPlaced`. Consumers not established `[unverified]` — no subscription found in this repo; likely in another service. Resolve by searching the org's repos for the event name, or asking the platform team.

A trace with a labelled gap is useful. A trace that bridges the gap with a plausible guess is dangerous, because it reads identically to the parts you verified.

### 4. Mark every boundary crossing

Boundaries are where behavior gets surprising and where changes break things. Flag each one explicitly:

| Boundary | Why it matters |
|---|---|
| **Process / network** | Can fail, time out, retry, or partially succeed |
| **Transaction** | Where it starts, commits, rolls back — and what's *outside* it |
| **Thread / async** | Ordering is no longer guaranteed; context may not propagate |
| **Message queue** | Delivery may be at-least-once; consumers may be idempotent, or may not be |
| **Team ownership** | Changes here need coordination, not just code |

The transaction boundary deserves particular attention. Work that happens outside the transaction — an email, an event publish, a cache write — will not roll back, and that asymmetry is the source of a large share of production data inconsistencies.

### 5. Follow the unhappy paths

Most traces only follow the success case, which is the least interesting one. For each hop ask: what happens if this fails?

- Is the exception caught, and where?
- Is it retried? How many times, with what backoff, and is the operation idempotent?
- Is there a timeout, and what is it? An unset timeout is a finding.
- Is there a circuit breaker or fallback?
- What does the caller see?
- Is anything left in an inconsistent state?

Retry against a non-idempotent operation is a bug waiting for a slow downstream. It is common, it is invisible in the success path, and finding one is often the most valuable output of a trace.

### 6. Verify by running it, where you can

If you can execute the flow, do. Add logging or a breakpoint and confirm the path you reconstructed is the path taken. This is the cheapest possible upgrade from `[inferred]` to `[confirmed]`, and reconstructions are wrong more often than they feel.

Where you can't run it, say so in the Confidence line.

### 7. Stop at the boundary of your question

A trace can expand forever — every downstream call is another trace. Stop when you've covered the operation you named, and record downstream systems as endpoints rather than following into them.

If a downstream turns out to be where the interesting behavior is, that's a *second* trace with its own document.

## Output template

Write to `<workspace>/traces/<business-operation>.md`:

```markdown
# Trace — <operation in business terms>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** <how much is confirmed by running it vs. read>
**Verified by running:** yes / no — <how>

## Operation
<The concrete scenario, in business terms. State the variant traced and the ones not traced.>

## Sequence

| # | Where | What happens | Boundary | Confidence |
|---|---|---|---|---|
| 1 | `AuthFilter:34` | Resolves tenant from JWT, sets thread-local | — | confirmed |
| 2 | `OrderController:44` | Validates payload, maps to command | — | confirmed |
| 3 | `OrderService:88` | **Opens transaction** | transaction start | confirmed |
| 4 | `InventoryClient:22` | HTTP POST to inventory-service, 2s timeout | **network** | confirmed |
| 5 | `OrderRepository:140` | Inserts order + lines | — | confirmed |
| 6 | `OrderService:132` | **Commits** | transaction end | confirmed |
| 7 | `EventPublisher:19` | Publishes `OrderPlaced` — **outside the transaction** | queue | confirmed |
| 8 | ? | Consumers unknown | — | **unverified** |

## Boundaries
| Boundary | Where | Implication |
|---|---|---|
| Transaction | opens `OrderService:88`, commits `:132` | Event publish at `:19` is outside it — will not roll back |

## Error and retry behavior
| Hop | On failure | Retry | Idempotent? | Caller sees |
|---|---|---|---|---|
| 4 | `InventoryException` | 3×, 100ms fixed | **No** `[confirmed: no idempotency key sent]` | 503 |

## Findings
<Things worth someone's attention. This section is often the real output.>

- Retry at hop 4 is not idempotent — a slow downstream could double-reserve inventory `[confirmed]`
- Event publish at hop 7 is outside the transaction — a crash between commit and publish loses the event `[confirmed]`

## Gaps
| # | What's unknown | Why it matters | To resolve |
|---|---|---|---|
| 1 | Consumers of `OrderPlaced` | Can't assess blast radius of a schema change | Search org repos, or ask platform team |

## Not traced
<Variants and downstream systems deliberately excluded, so a reader knows the limits.>
```

## Common traps

**Bridging a gap with a plausible guess.** The failure this skill exists to prevent. An unverified hop must be labelled, because it reads identically to a verified one.

**Missing what runs before the handler.** Filters, middleware, and interceptors do real work and are invisible in the handler.

**Only tracing the success path.** The error paths are where the surprises and the findings are.

**Not marking the transaction boundary.** Work outside the transaction doesn't roll back, and that asymmetry causes a large share of data inconsistencies.

**Ignoring timeouts and idempotency.** An unset timeout and a non-idempotent retry are both common and both serious.

**Tracing "order placement" instead of a concrete scenario.** The general case branches; the document becomes unreadable.

**Following every downstream.** Each is its own trace. Record it as an endpoint and stop.

**Naming the trace after a class.** `traces/OrderController.md` is unfindable by the person who needs it. Name the business operation.
