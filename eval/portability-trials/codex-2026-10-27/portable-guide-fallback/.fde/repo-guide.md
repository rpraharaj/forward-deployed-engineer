# Repository guide — Parcel Desk

**Engagement:** Synthetic portability trial
**Author:** FDE
**Date:** 2026-10-27
**Status:** draft
**Source revision:** handover@375f3c1
**Confidence:** Commands below were verified locally at the stated revision; package installation, normal CLI execution, and production/release paths were not exercised.

Read this file explicitly when starting work; automatic loading is host-specific.

## Scope and layout

- `parcel_desk/__main__.py` — CLI entry point; accepts `--db`.
- `parcel_desk/store.py` — SQLite-backed pending-parcel query.
- `tests/test_store.py` — one standard-library unittest using an in-memory database.
- `pyproject.toml` — project metadata and Python floor; no dependencies or build-system section.
- `.fde/` — engagement artifacts, intentionally committed for this synthetic fixture.

## Verified commands

Run from the repository root with Python 3.11 or newer.

```bash
python3 -m parcel_desk --help
python3 -m unittest discover -s tests -v
```

Verified on 2026-10-27 with Python 3.12.5: module help succeeded; 1/1 tests passed in 0.004s (0.06s wall time).

## Conventions and constraints

- The application and tests use only the Python standard library; no dependency installation is required for the verified commands.
- Use the documented unittest command. `pytest` happens to be installed locally but is neither declared nor required by the repository.
- Keep Python compatibility at 3.11+ unless the project requirement changes.
- Stay within local/module-level operation until release and production access and ownership are established.

## Landmines and limits

- Do not run the CLI without `--help` merely as a smoke test: its default database is the relative path `parcels.db`, and the query path creates the `parcels` table if absent.
- CSV export is requested but not implemented; it was explicitly outside this handover's implementation scope.
- No CI configuration, lockfile, dedicated Python-version pin, service definition, or existing project instruction file was found.
- Packaging/build, installation, real-file SQLite behavior, integration behavior, release, and production were not verified.

## Durable records

- Environment and command evidence: `.fde/01-environment.md`
- Continuation state, risks, and next steps: `.fde/09-handover.md`
- Engagement scope and constraints: `.fde/00-engagement.md`
