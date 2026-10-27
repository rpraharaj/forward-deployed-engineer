# Project working guide

TEAM_SENTINEL: retain this ownership note.

Use Python standard library tools. Existing engagement workspace is .fde/. Do not change source files during analysis.

## Repository working notes

- Runtime: Python 3.11+; package and console-script metadata are in `pyproject.toml`. There are no third-party runtime dependencies or lockfiles.
- Run/help: `python3 -m parcel_desk --help`. Installed console entry point: `parcel-desk` -> `parcel_desk.__main__:main`.
- Test: `python3 -m unittest discover -s tests -v`.
- Layout: `parcel_desk/__main__.py` parses CLI arguments and prints results; `parcel_desk/store.py` owns SQLite access; `tests/test_store.py` contains the current unit test.
- Persistence: `pending(path)` opens the caller-selected SQLite file, creates the `parcels` table if absent, then returns pending labels as one-element tuples. The CLI default is the working-directory-relative `parcels.db`.
- CSV-export landmines: no query ordering is specified; the read path has the side effect of creating schema; presentation is currently coupled to tuple-shaped store results; only the empty in-memory queue is tested.
- Engagement map and scoped CSV-export follow-up: `.fde/02-system-map.md`. Read `.fde/00c-context.md` and `.fde/02-system-map.md` explicitly at the start of the next session.
