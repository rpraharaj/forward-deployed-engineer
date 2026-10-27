# Handover — Synthetic portability trial

**Engagement:** Synthetic portability trial
**Author:** FDE
**Date:** 2026-10-27
**Receiving:** Internal operations engineering team (no individual named) · **Walked through:** not yet; no meeting authorized
**Source revision:** handover@375f3c1
**Status:** draft
**Confidence:** Repository-local module help and unit tests are confirmed; ownership, adoption, packaging, expanded runtime behavior, release, and production remain unverified or out of scope.

## What was done

The repository's local Python metadata, documentation, source, and tests were inspected without changing application source or installing anything. Module help and the documented unittest command were verified on Python 3.12.5, producing a green 1-test baseline. A portable repository guide and detailed environment record now capture the repeatable path and its limitations. No CSV implementation, dependency installation, service operation, external contact, release activity, or production activity occurred.

## Current state

| Item | Status | Notes |
|---|---|---|
| Module help | Verified | `python3 -m parcel_desk --help` succeeds |
| Local unit tests | Verified | 1/1 passes; in-memory empty-queue case only |
| CSV export | **Not built** | Requested in README; explicitly outside handover scope |
| Package build/install | Unverified | No build-system section; installation prohibited |
| Release/production operation | **Unavailable** | No access exists and operation was out of scope |
| Ownership/adoption | Unresolved | Receiving role named, but no individual, process owner, or adoption evidence |

## Open risks — read this section

| # | Risk | Impact if it lands | What would resolve it | Owner |
|---|---|---|---|---|
| 1 | Runtime coverage consists of one empty in-memory database test | Regressions in populated, file-backed, error, and CLI-output paths may go undetected | Add focused tests before changing behavior | **unowned** |
| 2 | CSV export is requested but has no recorded acceptance criteria or owner | Implementation may encode the wrong columns, ordering, escaping, or destination behavior | Name a decision owner and record testable CSV requirements | **unowned** |
| 3 | No CI configuration or exact local Python pin exists | Supported commands can drift and Python-version failures may appear late | Establish CI across the intended Python versions; optionally add a team-approved local pin | Internal operations engineering team |
| 4 | Installable packaging is ambiguous because `pyproject.toml` has no build-system section | The declared `parcel-desk` console script may not have a supported installation path | Decide whether packaging is required, then declare and test the build backend | **unowned** |
| 5 | Default CLI execution targets relative `parcels.db` and the query path creates schema | A smoke test from the wrong directory can create or mutate an unintended local database | Use an explicitly approved disposable `--db` path and add runtime tests | **unowned** |
| 6 | No individual maintainer, process owner, walkthrough, or adoption plan is identified | Questions, prioritization, and operational uptake may stall after handover | Assign named technical and process owners and conduct a hands-on walkthrough | Internal operations engineering team |
| 7 | No access register, release path, or production access exists | The team cannot demonstrate deployability or operate the project beyond local checks | Establish only the necessary access and release evidence when that work is authorized | **unowned** |

## Known issues not fixed

| What | Why not | Where |
|---|---|---|
| CSV export is absent | Implementation explicitly excluded from this engagement | `README.md` and future requirements artifact |
| Installed console-script path is unverified | No installation or dependency changes authorized; build backend absent | `pyproject.toml` |
| Test suite covers only an empty queue | Adding tests/application work was outside environment-and-handover scope | `tests/test_store.py` |

## Fragile areas

| Where | Why | What to do instead |
|---|---|---|
| Default database path | It is relative to the caller's current directory | Pass an explicit approved disposable path during future local verification |
| `pending()` read path | It also creates the table if absent, so a read has a write side effect | Characterize existing behavior before refactoring or adding CSV export |
| Packaging metadata | Project/script metadata exists without a declared build backend | Decide and verify the supported installation model before documenting install commands |

## Things only I currently know

- The clean verified path needs no third-party dependencies: Python 3.11+ and its standard library are enough.
- The local verification interpreter was Python 3.12.5; this is evidence, not a new project pin.
- `pytest 8.4.2` is present on this machine but is incidental and should not become an undocumented requirement.
- The help path is safe from database creation; normal CLI execution was deliberately not attempted.
- No proxy variable names were present during inspection, and no network operation was attempted.
- The `/var/...` workspace path in the charter and the checkout's `/private/var/...` path resolve to the same local workspace on this machine.

## Where everything is

| What | Where |
|---|---|
| Engagement scope | `.fde/00-engagement.md` |
| Working guide | `.fde/repo-guide.md` |
| Environment setup and verification | `.fde/01-environment.md` |
| Continuation handover | `.fde/09-handover.md` |
| Deploy/rollback runbook | Not present; no release or production scope |
| Decisions/ADRs | None present |
| System map | None present; narrow engagement did not run repository reconnaissance |
| Enablement evidence | None present; walkthrough not authorized |

## Skill and shared-reference provenance

Installed skill files used:

- `.agents/skills/env-bootstrap/SKILL.md`
- `.agents/skills/handover-pack/SKILL.md`

Shared-reference files used:

- `.agents/skills/_shared/workspace-conventions.md`
- `.agents/skills/_shared/stack-detection.md`
- `.agents/skills/_shared/enterprise-constraints.md`
- `.agents/skills/_shared/agent-context.md`

No other skill or shared-reference file was used.

## Access that will be revoked

No engagement-specific grants were identified or used. No release or production access exists. If scope expands, create an access register before requesting credentials and record locations only, never values.

## Superseded

None identified. The only pre-existing workspace artifact is the current engagement brief.

## Next steps

1. Assign a named technical maintainer and process/adoption owner; update this handover with decision rights and a realistic contact path.
2. Have the receiver reproduce the two commands in `.fde/repo-guide.md` and record the walkthrough result; none was authorized during this engagement.
3. Define CSV acceptance criteria before implementation, including schema, ordering, escaping, output destination, failure behavior, and compatibility expectations.
4. Add characterization tests for populated queues, file-backed SQLite, CLI output, and errors before changing `pending()` or adding export behavior.
5. Decide whether installable packaging is required. If so, select a build backend, add CI for supported Python versions, and verify build/install in an isolated environment.
6. Before any release or production work, establish the release process, required access, operational ownership, rollback expectations, and production-safe verification plan.
7. Reassess adoption after ownership is assigned: identify intended users, current workflow, support path, fallback, and a measurable successful-use signal.

## What I'd do differently

With broader authorization, I would first obtain a named receiver and watch them execute the guide, because the current handover is documentation-tested only by its author. I would also shape the CSV request into acceptance criteria and characterize the database side effects before implementation; doing those in the opposite order risks locking in accidental behavior.

## Contact

No post-engagement individual contact or availability window is authorized. The internal operations engineering team must assign the ongoing contact.
