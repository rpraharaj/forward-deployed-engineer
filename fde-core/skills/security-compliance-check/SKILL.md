---
name: security-compliance-check
description: Review a change specifically for data handling before release - what sensitive data crosses this path, whether it is logged or cached, encryption in transit and at rest, secrets externalized, and whether the audit trail satisfies the stated obligation. Use as a pre-release gate on anything touching personal data, payment data, health data, money, authentication, or an audit trail, and whenever a change adds a new data field, a new external call, or a new storage location. Complements rather than replaces the organization's own security review, whose lead time you should already know.
---

# Security and compliance check

The pre-release pass on data handling.

## Why this exists

Security review in a large organization has a lead time — often weeks — and it happens at the end. That produces two bad outcomes: a change blocked days before release by something that could have been designed differently, or a change that passes because the reviewer had twenty minutes and no context.

This skill is the pass **you** do, early and with full context, so the formal review finds nothing surprising. It doesn't replace the organization's review. It makes it fast.

There's a narrower reason too. The most common data-handling defects are not sophisticated attacks — they're a field added to a log line, a payload cached somewhere new, a token in an error message. They're introduced casually, they pass code review because they look harmless, and they're found in an audit a year later.

## When this applies

- Pre-release, on anything touching personal, payment, or health data
- Anything touching money, authentication, authorization, or an audit trail
- A change adds a new data field, a new external call, or a new storage location
- Anything already inside a regulatory scope — SOX, PCI, HIPAA, GDPR

## When it doesn't

- Changes that touch no data and no external surface
- Internal tooling with no sensitive data
- This is not a penetration test or a threat model, and shouldn't be presented as one

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

- `<workspace>/03b-nfrs.md` — the data classification and audit obligations
- `<workspace>/06-blast-radius-*.md` — where data flows
- `<workspace>/06b-change-log.md` — what actually changed

Know the organization's own review process and its lead time before starting. See `change-control-navigation`.

**First action, not last:** start the organization's formal review as soon as you know the data classification. An available agent security-review command may assist but does not replace required review. The rest of this skill is so that review finds nothing surprising. Starting it at go-live is the failure the why-section describes.

## Procedure

### 1. Establish what data is actually in scope

List every field the change touches, and classify each: personal, financial, health, authentication, or none.

Be precise about derived and indirect data. An order ID isn't personal; an order ID plus a timestamp plus a postcode frequently is, because it identifies someone. A "currency" field is not sensitive alone, but if it reveals location it may be. Aggregates can re-identify.

Where the classification isn't yours to make — and it usually isn't — record what you believe and who must confirm.

### 2. Follow the data to everywhere it now goes

The core of the check. For each sensitive field, trace where the change causes it to travel:

- **Logs** — application, access, audit, error. Including exception messages and stack traces, which frequently carry the payload that caused them.
- **Metrics, traces, and support-ticket payloads** — the same leak class as logs, often missed.
- **Caches** — in-memory, Redis, CDN, browser. What's the TTL, and is it encrypted?
- **Messages and events** — a published event is a copy of the data in a system with different retention and different consumers
- **External calls** — including monitoring, analytics, and error-reporting services. Third-party error trackers ingesting a full request body is a very common and easily-missed leak.
- **Persistence** — new columns, new documents, new files
- **Backups and replicas** — inherited automatically, and inherit the retention obligations too

The event-publishing case deserves particular attention. Adding a field to an event payload silently copies it into every consumer's storage, under their retention rules, outside your control.

### 3. Check secrets handling

Use `../_shared/change-review.md` to inventory branch commits plus staged, unstaged, and untracked changes against the actual target branch. Run the organization's approved scanner locally with redacted output. If no scanner is available, inspect the changed files locally and report only path, line number, and finding type; never print matching values or raw hunks into chat. Record the scan's scope and limitations rather than claiming grep proves the absence of secrets.

Then the questions grep can't answer: are new secrets externalized to the vault or config rather than committed? Is anything logged at debug level that wouldn't be at info? Are test fixtures carrying real credentials? Has anything been committed and then removed — which does **not** remove it from history?

```bash
# A secret removed in a later commit is still in history
git log --format=%h -S '<non-secret field or key name>' -- '<changed-path>'
```

This prints commit IDs only. Do not search with the credential itself or display raw historical patches; inspect flagged commits locally using a redacting workflow.

If something sensitive is in history, say so immediately. It needs a rotation, not a deletion, and the rotation is the urgent part.

### 4. Check transit and rest

- New external calls over TLS, with certificate verification **on**? Look specifically for verification disabled as a proxy workaround — see `../_shared/enterprise-constraints.md`.
- New storage encrypted, or covered by existing platform encryption?
- New fields inheriting the existing encryption, or bypassing it?

Where the platform already handles this, say so and cite it. "Encrypted at rest by the platform's default disk encryption" is a legitimate answer, and knowing it saves everyone time.

### 5. Verify the audit trail against the stated obligation

Where `nfr-baseline` recorded one, check the change actually produces it: who did it, when, what changed from what to what, and is it retained for the required period.

Then check the audit trail is **tamper-evident** where that's required — an audit log the application can rewrite is not an audit log for most compliance regimes.

### 6. Check authorization, not just authentication

A frequently-missed distinction. The change may correctly require a logged-in user and still let that user access another tenant's data.

For any new endpoint, field, or query: who is allowed to see this, is that enforced, and where? Multi-tenant systems specifically — is the tenant filter applied at the data layer, or relied upon at the presentation layer where a crafted request bypasses it?

### 7. Write it up for the reviewer who has twenty minutes

Structure the output so a security reviewer can confirm rather than investigate. Lead with what changed about data handling, then the classification, then the specific answers.

A review pack that answers the standard questions before they're asked converts a three-week review into a short one, and that alone justifies the skill.

## Output

Append to `<workspace>/08-release-readiness.md`:

```markdown
## Security and compliance check

**Date:** <YYYY-MM-DD> · **Reviewer:** FDE (pre-check) · **Formal review:** <status, ref>

### Data in scope
| Field | Classification | New? | Confirmed by |
|---|---|---|---|
| `currency` | non-personal | yes | Security, 03-18 |
| `customer_id` | personal (indirect) | no — existing | — |

### Where it now flows
| Destination | Sensitive data? | Encrypted | Retention | Notes |
|---|---|---|---|---|
| `refunds` table | yes | platform at-rest ✅ | 7y per policy | |
| `refund.processed` event | **yes — new field** | in transit ✅ | consumer-controlled | 4 consumers inherit this |
| Application logs | no | — | 30d | Verified — no PII in new log lines |
| Error tracker | **unverified** | — | vendor-controlled | Does it capture request bodies? |

### Secrets
- Changed paths scanned with <tool, revision, date>; <findings and limitations>, values redacted
- History checked for <non-secret key names>; <coverage and unresolved findings>. A key-name search alone does not prove the absence of credentials.
- TLS verification enabled on the new FX call `[confirmed: FxClient:22]`

### Audit
- Actor, timestamp, before/after recorded `[confirmed: RefundAudit:44]`
- Retention 7y via existing policy ✅
- Tamper-evidence: append-only table `[inferred — no delete grant, not verified]`

### Authorization
- New endpoint requires `REFUND_WRITE` ✅
- Tenant filter applied at repository layer `[confirmed: RefundRepository:88]`

### Open items for formal review
| # | Question | Why it matters |
|---|---|---|
| 1 | Does the error tracker capture full request bodies? | Would leak payloads to a third party |
```

## Common traps

**Checking the code, not the data flow.** The leak is usually a destination, not a line.

**Forgetting error paths.** Exception messages and stack traces carry the payload that caused them.

**Forgetting third-party monitoring.** Error trackers ingesting request bodies is a very common leak.

**Missing event payloads.** Adding a field copies it into every consumer's storage under their retention rules.

**Deleting a committed secret instead of rotating it.** It's still in history. Rotation is the urgent part.

**Checking authentication and not authorization.** Logged in is not the same as allowed.

**Tenant filtering at the presentation layer.** A crafted request bypasses it.

**Treating this as a substitute for formal review.** It's preparation for it. Know the lead time and start it early.
