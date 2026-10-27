# Environment — Parcel Desk

**Engagement:** Synthetic portability trial
**Author:** FDE
**Date:** 2026-10-27
**Status:** draft
**Source revision:** handover@375f3c1
**Confidence:** Module help and the complete local unittest suite were verified on Python 3.12.5; dependency installation, packaging/build, normal CLI execution, real-file database behavior, integration, release, and production were not exercised.

## What works

- [x] Module help
- [x] Unit tests
- [ ] Dependencies resolve — not applicable to the verified path; the manifest declares no dependencies
- [ ] Compiles/packages — not exercised; no build-system configuration is declared
- [ ] Integration tests — none identified
- [ ] Runs locally against a database — deliberately not exercised by this handover

## Quickstart

From the repository root:

```bash
# 1. Confirm the interpreter meets the declared floor.
python3 --version

# 2. Inspect the CLI without opening or creating a database.
python3 -m parcel_desk --help

# 3. Run the local test suite (uses an in-memory SQLite database).
python3 -m unittest discover -s tests -v
```

No dependency installation or service startup is required for these verified commands.

## Evidence and command source

- No CI configuration was found, so there is no CI command to treat as ground truth.
- The quickstart commands come from `README.md`; the Python floor and empty dependency list come from `pyproject.toml`.
- The repository has one root `pyproject.toml` and no sub-manifests, lockfile, dedicated Python pin, wrapper, container definition, or internal registry configuration.
- Only module help and local tests were authorized and exercised.

## Toolchain

| Tool | Required | Pinned in | Notes |
|---|---|---|---|
| Python | `>=3.11` | `pyproject.toml` | Verified with Python 3.12.5; no exact version pin exists |
| unittest | Python standard library | N/A | Repository-documented test runner |
| SQLite | Python standard library module | N/A | Test uses `:memory:`; no external database service |

`pytest 8.4.2` is installed on this machine but was not used and is not a project requirement.

## Services required

| Service | How to start | Needed for |
|---|---|---|
| None for verified scope | N/A | Module help and unit tests |

## Configuration

| What | Source for local | Notes |
|---|---|---|
| Database path | CLI `--db`; defaults to `parcels.db` | Relative to the current working directory; normal execution can create the database/table |
| Credentials/secrets | None identified | No network account is required per README |
| Proxy | No proxy environment variable names were present | No network operation was attempted |

## Test baseline

- **Passing:** 1 · **Pre-existing failures:** 0 · **Runtime:** 0.004s reported by unittest; 0.06s wall time
- **Command:** `python3 -m unittest discover -s tests -v`
- **Coverage limit:** only the empty in-memory queue is tested; file-backed databases, populated queues, errors, and CLI output are not covered.

## Workarounds discovered

| Problem | Symptom | Fix | Why |
|---|---|---|---|
| No CI or exact interpreter pin | No executable CI baseline or auto-selected Python version | Use Python 3.11+ as declared in `pyproject.toml` and run the README commands | This is the strongest repository-local evidence available |
| Help command displays `__main__.py` | Usage begins `usage: __main__.py` | Treat as cosmetic; invoke through `python3 -m parcel_desk` | The CLI is exercised as a module, not an installed console script |

## Still blocked or unverified

| What | Why | Needs | Tracked in |
|---|---|---|---|
| Package build/install | No `[build-system]` configuration and installation was prohibited | Receiving team decision on supported packaging workflow | `.fde/09-handover.md` |
| Normal CLI/file database behavior | Handover permits only module help and local tests | An approved disposable path and broader verification scope | `.fde/09-handover.md` |
| Release and production | No release or production access exists; operation was out of scope | Named owner, access, and release process | `.fde/09-handover.md` |
| Access register | `.fde/00b-access.md` is absent | Receiving team to establish required grants if scope expands | `.fde/09-handover.md` |

## Gaps worth fixing

- Add a CI workflow or another executable check definition so the supported Python versions and test command are continuously verified.
- Decide whether installable packaging is supported; if it is, declare and verify a build backend.
- Add tests for populated queues, file-backed behavior, CLI output/errors, and the requested CSV behavior before implementing it.
- Add an exact local Python pin only if the receiving team wants one; do not infer one from this machine.
