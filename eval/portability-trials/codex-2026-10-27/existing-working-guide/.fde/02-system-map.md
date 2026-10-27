# System map — Parcel Desk

**Engagement:** Synthetic portability trial
**Author:** FDE
**Date:** 2026-10-27
**Status:** draft
**Source revision:** parcel-desk@2c484c3
**Confidence:** Complete static coverage of all tracked product and test files plus successful help/test execution; packaging installation, installed console invocation, non-empty database output, and CI behavior were not exercised.

## Scope

This map covers the whole nine-file repository at `2c484c3`, including its CLI, SQLite access, package metadata, test, and project instructions. Ignored installed skills under `.agents/skills/` are tooling instructions, not application code. CSV export is mapped as the next change only; it is not designed or implemented here.

## At a glance

- **Purpose:** List labels for parcels whose status is `pending` from a caller-selected local SQLite database `[confirmed: README.md:3-6; parcel_desk/__main__.py:4-9; parcel_desk/store.py:3-6]`.
- **Size:** 9 tracked files and 24 lines across package/test Python `[confirmed: commands "git ls-files | wc -l" -> 9 and "wc -l parcel_desk/*.py tests/*.py" -> 24]`.
- **Stack:** Python >=3.11, `argparse`, `sqlite3`, and `unittest`; no declared third-party dependencies or lockfile `[confirmed: pyproject.toml:1-7; parcel_desk/__main__.py:1; parcel_desk/store.py:1; tests/test_store.py:1]`.
- **Deployment shape:** Local CLI; no service, network account, scheduler, event consumer, container, or external integration is declared `[confirmed: README.md:3-6 and complete tracked-file review]`.
- **Activity:** 2 commits in the last six months; latest commit dated 2026-10-27 `[confirmed: git history commands returned 2 and 2026-10-27]`.
- **Health:** `python3 -m parcel_desk --help` succeeds on Python 3.12.5; `python3 -m unittest discover -s tests -v` passes 1 test in 0.001s. No CI configuration exists in the tracked tree, so merge gating is unverified.

## Commands

| Goal | Command | Observed result |
|---|---|---|
| Inspect CLI | `python3 -m parcel_desk --help` | Success; exposes `--db DB` |
| Run tests | `python3 -m unittest discover -s tests -v` | 1 test passed |
| Installed CLI | `parcel-desk` | Declared, not exercised because the project was not installed `[confirmed: pyproject.toml:6-7]` |
| Install/build | None required for module execution | Standard-library-only project with no build-system table `[confirmed: README.md:3-5; pyproject.toml:1-7]` |

## Entry points

| Type | Entry | Handler | Notes |
|---|---|---|---|
| Module CLI | `python3 -m parcel_desk` | `parcel_desk.__main__:main` | `__main__` guard calls `main()` `[confirmed: parcel_desk/__main__.py:4-12]` |
| Installed CLI | `parcel-desk` | `parcel_desk.__main__:main` | Declared by project metadata; installation was outside scope `[confirmed: pyproject.toml:6-7]` |

No generated-source marker, declarative route surface, HTTP handler, scheduled job, event handler, or serverless handler appears in the complete tracked tree `[confirmed: complete tracked-file review; generated-header and entry-point searches returned zero]`.

## Module map

| Module | Responsibility | Depends on | Notes |
|---|---|---|---|
| `parcel_desk.__main__` | Parse `--db`, fetch pending rows, print each row | stdlib `argparse`; `parcel_desk.store.pending` | Owns current presentation behavior `[confirmed: parcel_desk/__main__.py:1-9]` |
| `parcel_desk.store` | Open SQLite, ensure schema, query pending labels | stdlib `sqlite3` | Entire persistence boundary `[confirmed: parcel_desk/store.py:1-6]` |
| `tests.test_store` | Verify an empty in-memory store returns `[]` | stdlib `unittest`; `pending` | No CLI/output or non-empty-row coverage `[confirmed: tests/test_store.py:1-6]` |

Dependency direction is CLI -> store -> SQLite; the test calls the store directly. There are no other authored modules `[confirmed: imports in parcel_desk/__main__.py:1-2, parcel_desk/store.py:1, tests/test_store.py:1-2]`.

## Data

| Store | What lives there | Accessed via | Shared with |
|---|---|---|---|
| SQLite file from `--db`; default `parcels.db` relative to the process working directory | `parcels(id INTEGER PRIMARY KEY, label TEXT, status TEXT)` | `sqlite3.connect(path)` inside `pending(path)` | No sharing or concurrent-use contract is documented `[confirmed: parcel_desk/__main__.py:6; parcel_desk/store.py:3-6]` |

The read operation is also schema initialization: `pending()` executes `CREATE TABLE IF NOT EXISTS` before selecting labels with status exactly `pending` `[confirmed: parcel_desk/store.py:3-6]`. It returns `fetchall()` unchanged, so consumers receive one-element tuples such as `(label,)`, not scalar strings `[confirmed: parcel_desk/store.py:6]`.

## Integrations and dependencies

| System | Direction | Protocol | Where configured | Owner |
|---|---|---|---|---|
| Local SQLite database | Read/write from process | Python DB-API / local file | CLI `--db`; default in `parcel_desk/__main__.py:6` | This repository |

Runtime dependencies are Python >=3.11 and standard-library `argparse`/`sqlite3`; tests additionally use standard-library `unittest`. `dependencies = []`, and there is no lockfile, container, CI config, or network client `[confirmed: pyproject.toml:4-5 and complete tracked-file review]`.

## Test topology

- **Location:** `tests/test_store.py` · **Kinds:** store unit test using SQLite `:memory:` · **Count:** 1 test · **Runtime:** 0.001s observed · **Gates merge:** `[unverified: no CI configuration is tracked]`.
- **Coverage of CSV-export area:** None. The existing test covers only the empty persistence result; it does not cover non-empty rows, deterministic ordering, argument parsing, stdout, CSV headers/quoting, destination errors, or database failures `[confirmed: tests/test_store.py:4-6]`.

## Config and environments

| Environment | Config source | Notes |
|---|---|---|
| Local CLI | `--db` argument | Defaults to `parcels.db`; no environment-variable access exists `[confirmed: parcel_desk/__main__.py:5-7 and complete Python-source review]` |
| Python runtime | `pyproject.toml` | Minimum 3.11; recon ran on 3.12.5 `[confirmed: pyproject.toml:4; command "python3 --version" -> 3.12.5]` |

## Churn hotspots

The two-commit synthetic history provides no meaningful relative churn: every initial project file has one content commit, and the second commit only changed `.gitignore` `[confirmed: command "git log --oneline --stat --all"]`.

## Limits and landmines

| What | Where | Why it matters for CSV export | Confidence |
|---|---|---|---|
| No deterministic row order | `parcel_desk/store.py:6` | The query has no `ORDER BY`; exported row order must not be assumed. | confirmed |
| Read creates schema | `parcel_desk/store.py:4-6` | Exporting a missing database silently creates it instead of behaving as a pure read. | confirmed |
| Store leaks row shape | `parcel_desk/store.py:6` | `fetchall()` returns one-element tuples, while CSV needs an explicit column model. | confirmed |
| Presentation is direct tuple printing | `parcel_desk/__main__.py:8-9` | Current human output is Python tuple syntax; adding CSV should preserve or deliberately replace it behind an explicit mode. | confirmed |
| Weak data constraints | `parcel_desk/store.py:5` | `label` and `status` are nullable/unconstrained; CSV behavior for nulls and unexpected statuses needs a decision. | confirmed |
| Relative default database path | `parcel_desk/__main__.py:6` | Output depends on launch directory and a default run can create `parcels.db`. | confirmed |
| Minimal test seam | `tests/test_store.py:4-6` | Only the empty queue is pinned; regressions in non-empty and CLI behavior would currently pass. | confirmed |
| No error policy | `parcel_desk/__main__.py:4-9` | Database/open/write failures are not caught or translated into stable exit behavior. | confirmed |

## The five questions

1. **Where does a request enter?** Through `main()` via either `python3 -m parcel_desk` or the declared `parcel-desk` script `[confirmed: pyproject.toml:6-7; parcel_desk/__main__.py:4-12]`.
2. **Where does its data live?** In the SQLite path passed as `--db`, defaulting to working-directory-relative `parcels.db`; access is isolated to `pending()` `[confirmed: parcel_desk/__main__.py:6-8; parcel_desk/store.py:3-6]`.
3. **What else does it talk to?** Nothing external is declared; only Python standard library and local SQLite are present `[confirmed: pyproject.toml:4-5 and complete tracked-file review]`.
4. **Where would CSV export land?** The smallest likely slice is CLI behavior and tests around `parcel_desk/__main__.py`, with a narrowly defined store change only if deterministic ordering or an explicit row model is required `[inferred: current dependency and presentation boundaries]`.
5. **What is risky to touch?** `pending()` combines initialization, querying, and return-shape semantics; changing it can alter database creation, current CLI tuple output, and the sole test at once `[confirmed: parcel_desk/store.py:3-6; parcel_desk/__main__.py:8-9; tests/test_store.py:5-6]`.

## Next scoped step

Before implementation, specify one CLI-level CSV slice: whether CSV goes to stdout or a named file, the exact header/columns, quoting/newline rules using the standard-library `csv` module, ordering, empty-result behavior, and failure/exit behavior. Then add failing tests using temporary SQLite data and captured CLI output. Keep the first implementation within `parcel_desk/__main__.py`, `parcel_desk/store.py` only if ordering/row shape must change, and focused tests; do not add a dependency.

## Gaps

- Installed `parcel-desk` execution is unverified because installation was explicitly out of scope; module execution proves the same handler is runnable.
- Non-empty and malformed database behavior is unverified because no fixture or test covers it.
- CSV product semantics are intentionally unspecified; the next scoped step must decide them before code changes.
- CI/merge gating is unverified because no CI configuration is tracked.
