# Context strategy

**Engagement:** Synthetic portability trial
**Author:** FDE
**Date:** 2026-10-27
**Status:** draft
**Source revision:** parcel-desk@2c484c3
**Confidence:** Scale is confirmed from `git ls-files`; the CSV-export working set is a bounded judgment from a complete read of the nine tracked files.

## Scale

- **Files:** 9 tracked files · **Band:** <500 `[confirmed: command "git ls-files | wc -l" -> 9]`
- **Scope:** Whole repository; installed skill sources under ignored `.agents/skills/` were read only as instructions and are not part of the product map.
- **Approach:** Read freely. The product has 24 lines across authored Python and test files `[confirmed: command "wc -l parcel_desk/*.py tests/*.py" -> 24]`.
- **Constraints:** No feature implementation, source-file edits, software installation, delegation, contacts, or external services; project `AGENTS.md` remains authoritative.

## Working set — next CSV export slice

- `pyproject.toml:1-7` — Python floor, empty dependency list, installed CLI declaration.
- `parcel_desk/__main__.py:1-12` — argument parsing and current presentation boundary; likely home for a bounded export option.
- `parcel_desk/store.py:1-6` — SQLite persistence boundary and tuple-shaped pending query.
- `tests/test_store.py:1-6` — current store test and fixture idiom.
- `README.md:1-6` — user-facing run/test commands and explicit statement that CSV export is absent.
- `AGENTS.md` — team policy plus durable repository commands and landmines; preserve `TEAM_SENTINEL`.

## Working guide

`AGENTS.md`; updated with confirmed commands, layout, persistence behavior, and CSV-export limits while preserving all existing instructions.

## Useful commands

- Run/help: `python3 -m parcel_desk --help`
- Test: `python3 -m unittest discover -s tests -v`
- Reconfirm tracked scale: `git ls-files | wc -l`
- Locate the persistence surface: `rg -n 'sqlite3|CREATE TABLE|SELECT ' parcel_desk tests`

## Next step

Shape one independently testable CSV-export slice: choose stdout versus a destination file and define header, column, quoting, and deterministic ordering behavior; then add failing CLI-level tests before changing `parcel_desk/__main__.py` or `parcel_desk/store.py`.
