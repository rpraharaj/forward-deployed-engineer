---
name: integration-adapter
description: Build a client against a system you do not control and cannot fully see - contract discovery from observed traffic and existing callers, defensive parsing, timeout and retry and circuit-breaking posture, and a fake for testing. Use when consuming a legacy, undocumented, mainframe, SOAP, flat-file, or externally-owned interface, when the documentation disagrees with reality, or when integrating with a partner system. Assume the documentation is wrong and the interface will misbehave, because both are usually true.
---

# Integration adapter

Talking to something you can't change.

## Why this exists

Enterprise integration is mostly against systems that are undocumented, documented incorrectly, owned by someone else, or all three. A mainframe interface described by a Word document from 2014. A partner SOAP endpoint whose WSDL doesn't match what it returns. A flat file whose format is defined by the code that writes it.

Two assumptions make this work, and both feel pessimistic until you've been burned:

**The documentation is wrong.** Not maliciously — it described the system accurately once. Observed behavior beats documentation every time, and where they disagree, the documentation is the thing that's out of date.

**The interface will misbehave.** It will time out, return malformed responses, return HTTP 200 with an error in the body, be down for maintenance without notice, and change without telling you. An adapter that assumes good behavior fails in production in ways that are hard to diagnose because the failure is somewhere you can't see.

## When this applies

- Consuming a legacy, mainframe, SOAP, flat-file, or externally-owned interface
- Documentation disagrees with reality
- Partner or vendor system integration
- The system on the other side can't be changed

## When it doesn't

- Both sides are yours and changeable — design the contract properly with `contract-design`
- A well-maintained internal API with an accurate spec
- You need to understand an existing integration rather than build one — that's `trace-the-flow`

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: use `FDE_WORKSPACE` if set (report an unavailable explicit path rather than falling back), otherwise the charter's recorded Location (look in `.fde/` and `../*-fde/`), then an existing `.fde/` or `../<repo>-fde/`. If none exists, run core `fde-orient`; do not create a second workspace. All artifact paths below use that location. Follow core workspace conventions for headers; preserve existing sections when appending.

- `<workspace>/02-system-map.md` — where this integration sits
- `<workspace>/03b-nfrs.md` — what data may cross the boundary
- Any existing callers of the same system, which are your best documentation

## Procedure

### 1. Find the existing callers first

Before reading any specification, find code in the organization that already talks to this system. It encodes years of accumulated knowledge about the interface's actual behavior — every workaround in it is a bug someone hit.

```bash
# Search for the hostname, service name, or a distinctive field
grep -rn "<hostname>\|<ServiceName>\|<distinctive-field>" --include="*.*" . | head -20
```

Read them specifically for the **workarounds**: retries around a particular call, a field parsed defensively, a sleep, a comment explaining something strange. Each one is a documented failure mode, and reproducing them is cheaper than rediscovering them.

`git-archaeology` on those workarounds usually tells you exactly what incident produced them.

### 2. Observe reality, then compare it to the documentation

Where you can call the system — a test environment, a sandbox, or a recorded sample — capture actual traffic and compare it to whatever spec exists.

You're looking for the divergences that will bite:

- Fields present in reality, absent from the spec
- Fields documented as required that are sometimes missing
- Types that differ — numbers as strings, dates in unexpected formats, booleans as `"Y"`/`"N"`
- Error responses whose shape differs completely from success responses
- **HTTP 200 with an error in the body**, which is extremely common in enterprise SOAP and legacy REST
- Character encoding, which is where mainframe integration usually goes wrong

Record what you observed and when, with samples. That record is the real contract, and it's more valuable than the spec to whoever maintains this next.

### 3. Isolate everything behind one adapter

The whole point of the pattern. **All contact with the foreign system goes through one component**, exposing an interface shaped for *your* domain, not theirs.

That boundary is what lets you:
- Change the integration without touching business logic
- Substitute a fake for testing
- Put all the defensive handling in one place
- Absorb their changes in one file rather than across the codebase

Do **not** let their data structures leak past the adapter. If their `CUST_REC_TYPE_CD` reaches your domain layer, you've coupled your system to theirs and every one of their changes becomes a change in your business logic.

### 4. Parse defensively

Assume every response is malformed until proven otherwise.

- Treat every field as optional regardless of what the spec says, and fail explicitly when a genuinely required one is missing
- Validate types rather than trusting them
- Check for error indicators *inside* successful responses — the 200-with-error case
- Handle unknown enum values without crashing
- Never let a parse failure surface as an unhandled exception carrying the raw payload — that's how sensitive data reaches your logs

**Log enough to diagnose, redacted.** When this breaks at 3am the person debugging needs the request and response, and they must not contain card numbers or personal data. Decide the redaction up front; see `security-compliance-check`.

### 5. Set the resilience posture explicitly

Every parameter is a decision, and the defaults are almost always wrong:

- **Timeout** — always set one. An unset timeout is the single most common cause of an integration taking down the calling system, because a slow dependency exhausts your connection pool while a fast failure never would.
- **Retry** — only for genuinely transient failures, and **only if the operation is idempotent.** Retrying a non-idempotent payment call is a duplicate charge. If they offer an idempotency key, use it; if they don't, retry only reads.
- **Backoff** — exponential with jitter. Fixed-interval retries from many instances synchronize and hammer a recovering system.
- **Circuit breaker** — stop calling a system that's clearly down, so you fail fast instead of queueing.
- **Fallback** — is there a degraded mode? `nfr-baseline` should have specified it.

Slow is worse than down, and it's the case people don't test. `nfr-validation` covers testing it.

### 6. Build a fake, not a mock

Build a fake implementation of the adapter's interface that behaves like the real system — including its bad behavior. It should be able to return malformed responses, time out, and produce the 200-with-error case.

A fake beats a mock here for the same reason as in `characterization-tests`: mocks assert interactions and couple tests to the current implementation, while a fake supplies behavior and lets you exercise the failure paths that matter.

Record real responses as fixtures — redacted — so the fake returns shapes you actually observed rather than shapes you imagined.

### 7. Write down what you learned

The observed contract is the most valuable artifact here. Where it disagrees with their documentation, record both and say which you built against.

This is what makes the integration maintainable after you leave, and it's the thing that reliably doesn't exist for the integrations you inherited.

## Output

Write to `<workspace>/traces/<external-system>.md`:

```markdown
# Integration — <system>

**Engagement:** <name> · **Author:** FDE · **Date:** <YYYY-MM-DD>
**Their docs:** <ref, date> · **Observed:** <environment>, <dates>
**Confidence:** <observed vs. documented-only>
**Status:** draft
**Source revision:** <repo>@<short SHA>, or "no repository yet"

## Interface
**Protocol:** SOAP 1.1 over HTTPS · **Auth:** mutual TLS, cert expires <date> ⚠️
**Owner:** <team / vendor> · **Contact:** <how> · **SLA:** <if any>

## Observed vs documented
| Aspect | Documented | Observed | Built against |
|---|---|---|---|
| `amount` | decimal | **string, 2dp, comma separator in some locales** | observed |
| `status` | 3 values | **5 values** — 2 undocumented | observed |
| Error | HTTP 500 | **HTTP 200, `<fault>` in body** | observed |
| Missing customer | 404 | **200 with empty result set** | observed |

## Failure modes seen
| Mode | Frequency | Handling |
|---|---|---|
| Timeout > 30s | ~1/1000 | 10s timeout, circuit breaker |
| Malformed XML | rare | Parse failure → explicit error, payload logged redacted |
| Maintenance window | Sundays 02:00–04:00, **unannounced** | Circuit breaker; batch reschedule |

## Resilience posture
| Parameter | Value | Why |
|---|---|---|
| Timeout | 10s | p99 observed 3.2s |
| Retry | 2×, reads only | **No idempotency key offered — writes not retried** |
| Backoff | exponential + jitter | |
| Circuit breaker | 5 failures / 30s → open 60s | |
| Fallback | cached rate, max 24h stale | Per `03b-nfrs.md` N5 |

## Adapter
**Interface:** `FxRateProvider` — our domain, not theirs
**Fake:** `FakeFxRateProvider`, 14 recorded fixtures incl. 4 failure cases
**Their types do not escape:** `[confirmed: FxAdapter:88 maps to domain]`

## Watch items
- Client cert expires <date> — **renewal owner: <name>**
- Undocumented status values may grow; unknown values map to `UNKNOWN` and alert
```

## Common traps

**Trusting the documentation.** It was accurate once. Observed behavior wins.

**Letting their types into your domain.** Every change of theirs becomes a change in your business logic.

**No timeout.** The most common way an integration takes down the calling system.

**Retrying non-idempotent calls.** A duplicate charge is not a transient failure.

**Fixed-interval retry.** Instances synchronize and hammer a recovering system.

**Only handling HTTP-level errors.** 200-with-error-in-body is extremely common in enterprise interfaces.

**Mocking instead of faking.** You never exercise the failure paths, which are the ones that matter.

**Logging the raw payload.** That's how card numbers reach your logs. Redact by design.

**Not recording the observed contract.** The single most valuable artifact, and the one that never exists for integrations you inherit.
