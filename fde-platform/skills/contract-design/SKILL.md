---
name: contract-design
description: Design an API, event, or schema contract with compatibility as the primary concern - versioning strategy, backward compatibility, migration path for existing consumers, and failure semantics - plus a consumer impact list. Use when creating or changing anything that crosses a team boundary, when adding a field to a published response or event, when consumers exist outside your repository, or when someone asks how to version an API. Once consumers exist you do not control, the contract stops being a design problem and becomes a coordination problem.
---

# Contract design

Designing something other people depend on.

## Why this exists

An internal interface can be changed by editing every caller. A published contract cannot, and the moment consumers exist outside your repository the constraints change completely: you no longer control when they upgrade, whether they upgrade, or in some cases who they are.

The characteristic mistake is designing a contract as though it were an internal interface — shaped for the current implementation, with no versioning story — and discovering the constraint when the first breaking change is needed. By then the options are all expensive.

An FDE hits this specifically because you often can't see the consumers. `blast-radius` ring 4 is the hardest ring to establish from inside one repository, and contracts are exactly where an unknown consumer hurts.

## When this applies

- Creating or changing an API, event, message, or shared schema
- Adding a field to a published response or event payload
- Consumers exist outside your repository
- "How should we version this?"
- Anything crossing a team boundary

## When it doesn't

- Internal interfaces with all callers in one repository — refactor freely
- A prototype nobody consumes yet
- The contract exists and isn't changing — that's `blast-radius`

## Prerequisites

- Locate the workspace: `FDE_WORKSPACE`, else the charter Location, else `.fde/`, else `../<repo>-fde/`
- `.fde/06-blast-radius-*.md` — ring 3 and ring 4 especially. **You need the consumer list before designing.** If ring 4 was not checked, design as if consumers are uncontrollable.
- `.fde/03b-nfrs.md` — data classification determines what may cross the boundary
- `.fde/02b-ownership.md` — who must be coordinated with

## Procedure

### 1. Establish who consumes it, and how much control you have

This determines everything downstream, and the categories behave very differently:

| Consumer type | Control | Implication |
|---|---|---|
| Same team, same repo | Full | Change freely; this isn't really a contract |
| Other team, same org | Coordinated | Breaking changes possible with notice and effort |
| External partner | Contractual | Breaking changes need commercial agreement |
| Mobile or embedded client | **None** | Old versions live forever. Design for indefinite compatibility. |
| Unknown | **None, and you can't ask** | Treat as the most constrained case |

The mobile case is the one engineers under-weight. You cannot deploy a fix to an app on someone's phone; a two-year-old client version will still be calling. "Backward compatible until the next release" and "backward compatible indefinitely" are different designs.

Where consumers are **unknown** — common, and the honest state after a blast-radius ring 4 you couldn't complete — design as though they're uncontrollable. That's the cost of not knowing, and it's cheaper than the alternative.

### 2. Choose what changes are allowed to be

Decide, before designing, which categories of change you're committing to support. Broadly consistent across formats:

**Usually safe:**
- Adding an optional field
- Adding a new endpoint, message type, or enum member *(see below)*
- Relaxing a validation constraint

**Usually breaking:**
- Removing or renaming anything
- Making an optional field required
- Changing a type or its semantics
- Tightening validation
- Changing the meaning of an existing value

**Adding an enum value deserves its own thought.** It is safe only if consumers are built to tolerate unknown values, and many are not — a strict parser or an exhaustive switch will reject or crash. Whether this is safe is a property of your *consumers*, not of your schema, so it can only be answered by knowing them.

The same applies to added fields: additive is safe unless a consumer uses strict schema validation, parses positionally, or round-trips the payload. Check rather than assume — this is the most common way an "obviously safe" change breaks something.

### 3. Pick a versioning strategy and state the lifecycle

Options, each with a real cost:

| Strategy | Cost |
|---|---|
| **No versioning, additive only** | Simple; you can never remove anything |
| **URI or namespace version** (`/v2/`) | Explicit and visible; doubles surface area while both live |
| **Header or content negotiation** | Cleaner URLs; harder to see what's in use |
| **Schema evolution** (Avro, Protobuf) | Strong tooling; requires discipline about field numbering and defaults |
| **Event type versioning** | New event type alongside the old; consumers migrate independently |

Whichever you choose, define the **lifecycle** explicitly, because this is what people skip: how long does a version live, what triggers deprecation, how much notice do consumers get, and what happens to a consumer that doesn't migrate?

A version with no defined end lives forever. Most organizations have three "current" API versions because nobody ever said when v1 stops.

### 4. Design the failure semantics

Half of a contract, and routinely undocumented — leaving each consumer to guess, differently.

- What errors can this return, and what does each mean?
- Which are retryable, and which will never succeed?
- Is the operation idempotent? If a consumer retries after a timeout, what happens? **This is the single most important question in the contract**, and the least often answered.
- What's the timeout expectation on both sides?
- What happens on partial success?

An idempotency key mechanism, defined up front, prevents a whole category of duplicate-processing incidents. Retrofitting one later is far harder because consumers have already built retry logic against its absence.

### 5. Be deliberate about what you expose

A contract is a commitment. Everything in it is something you must keep supporting.

- Don't leak internal structure — an entity serialized straight from the domain model couples consumers to your internals, and every refactor becomes a breaking change
- Don't expose fields consumers don't need. Each is a future constraint.
- Don't expose sensitive data because it was convenient — every consumer inherits that data and its retention obligations. See `security-compliance-check`.
- Do include what consumers will obviously need next, if it's cheap. Adding it later is easy; the coordination isn't.

### 6. Write the migration path before you need it

For any change requiring consumers to act: what do they do, by when, what happens if they don't, and how do you know who has migrated?

That last one matters and is usually impossible retrospectively. **Build version observability in from the start** — log the version each consumer uses, so "can we retire v1?" is a query rather than a guess. Without it, retiring a version becomes a consumer-discovery project — the same problem `decommission-plan` exists for if `fde-migration` is installed.

### 7. Document it where consumers will look

A contract only documented in code isn't a contract. Machine-readable where the ecosystem supports it — OpenAPI, `.proto`, JSON Schema, Avro — because that gives consumers generated clients and gives you contract testing.

Record the decision in an ADR via `solution-design`. The versioning strategy in particular is a decision future engineers need the reasoning for.

## Output

ADR at `.fde/adr/NNNN-contract-<name>.md`, plus the machine-readable schema in the repo:

```markdown
# ADR-NNNN — <contract> versioning and compatibility

**Status:** proposed · **Deciders:** <who> · **Date:** <YYYY-MM-DD>

## Decision
<One sentence.>

## Consumers
| Consumer | Type | Control | Can we coordinate? |
|---|---|---|---|
| `billing-web` | internal | coordinated | yes |
| Partner X extract | external | contractual | 90 days' notice per agreement |
| Mobile app | **uncontrollable** | none | **no — v1.x will call indefinitely** |
| Unknown | — | none | **assume uncontrollable** |

## Compatibility commitment
- Additive optional fields only, within a major version
- Unknown fields MUST be ignored by consumers — **stated in the contract docs**
- Unknown enum values MUST be tolerated — `UNKNOWN` fallback defined
- Breaking changes require a new major version + 12 months' overlap

## Versioning
**Strategy:** URI major version · **Lifecycle:** 12 months' overlap minimum, deprecation
announced at new-version launch · **Retirement gate:** < 0.1% traffic for 30 days

## Failure semantics
| Condition | Response | Retryable | Idempotent |
|---|---|---|---|
| Validation failure | 400 + field list | no | n/a |
| Downstream unavailable | 503 + `Retry-After` | yes | yes — `Idempotency-Key` required |
| Duplicate idempotency key | 200, original result | n/a | yes |

## Version observability
`consumer_id` + `api_version` logged per request → retirement is a query, not a guess.

## Migration path
<What consumers do, by when, what happens if they don't.>
```

## Common traps

**Designing it like an internal interface.** You don't control when consumers upgrade, or whether.

**Assuming additive is safe.** Strict validators, positional parsers, and round-trippers all break. A property of consumers, not of your schema.

**Adding an enum value without checking consumer tolerance.** Exhaustive switches crash.

**No defined version lifecycle.** Three "current" versions forever, because nobody said when v1 ends.

**Undocumented failure semantics.** Every consumer guesses differently, and their retry logic becomes your problem.

**No idempotency story.** Retrofitting one after consumers have built retries around its absence is far harder.

**Serializing the domain model.** Every internal refactor becomes a breaking change.

**No version observability.** "Can we retire v1?" becomes a consumer-discovery project.

**Forgetting mobile.** Old versions live forever, and you cannot deploy a fix to them.
