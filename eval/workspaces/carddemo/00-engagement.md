# Engagement charter — fifth-class hunt (CardDemo)

**Engagement:** fifth-class hunt / CardDemo
**Author:** FDE
**Date:** 2026-08-17
**Status:** draft
**Source revision:** aws-samples/aws-mainframe-modernization-carddemo@59cc6c2
**Confidence:** Validation spike. No z/OS region, so nothing here was executed.

## Workspace
- **Location:** `eval/workspaces/carddemo/` in the FDE-Claude repository
- **Committed to VCS:** yes, with the validation record — clone at `/tmp/fde-coldstart/carddemo` is disposable
- **Decided by:** FDE, 2026-08-17
- **Packs needed:** core

## The ask
**As stated:** Point `repo-recon` at a stack the skills were not written against — COBOL / copybooks / JCL — and see what breaks.
**Requested by:** portfolio validation
**Sponsor:** portfolio validation

## The real problem
Four previous cold-starts each found a new assumption class. CONTRIBUTING predicted a fifth on mainframe/copybooks, generated source, or low-code.

## Definition of done
- Procedure followed as written
- As-written map compared to what is actually there
- Method fix, not a COBOL-only grep list
- `VALIDATION.md` Run 11

## Archetype
**Assessment only** — map, do not change.

## Constraints
| Constraint | Detail | Source |
|---|---|---|
| No mainframe | cannot compile or run CICS/JCL | this machine |
| Size | 329 files — under the skill's "~500, just read it" threshold; procedure still followed | `git ls-files` |

## Planned sequence
1. `repo-recon` as written
2. Compare, fix, record

## Log
| Date | Change |
|---|---|
| 2026-08-17 | Charter created |
