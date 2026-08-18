# Engagement charter — env-bootstrap cold-start (ripgrep)

**Engagement:** env-bootstrap cold-start / ripgrep
**Author:** FDE
**Date:** 2026-08-17
**Status:** draft
**Source revision:** BurntSushi/ripgrep@3fce3b5
**Confidence:** Validation spike, not a client engagement. Ask and sponsor are the portfolio test in VALIDATION.md, not a product owner.

## Workspace
- **Location:** `eval/workspaces/ripgrep/` in the FDE-Claude repository (not `.fde/` inside the throwaway clone)
- **Committed to VCS:** yes, with the validation record — the clone at `/tmp/fde-coldstart/ripgrep` is disposable
- **Decided by:** FDE, 2026-08-17
- **Packs needed:** core

## The ask
**As stated:** Run `env-bootstrap` as written against a real repository through compile, test, and run. Record defects. Fix methods, not one-off patterns.
**Requested by:** portfolio validation
**Sponsor:** portfolio validation

## The real problem
`VALIDATION.md` listed `env-bootstrap` as steps 1–3 only — no build had been run to completion. The skill's durable value is the workaround table after a real green (or honestly blocked) loop.

## Definition of done
- Procedure followed as written, including the pin-file grep
- `01-environment.md` records what works, what doesn't, and every workaround
- Any method defect is fixed in the skill / `stack-detection.md`, not papered over in the clone
- `VALIDATION.md` Run 10 written

## Archetype
**Spike / PoC** — timeboxed execution of one skill against an unfamiliar checkout.

## Constraints
| Constraint | Detail | Source |
|---|---|---|
| Deadline | this session | validation |
| Environment / access limits | public GitHub clone; no secrets; do not change the user's default rustup toolchain | machine |
| Repo hygiene | do not add `rust-toolchain.toml` or `CLAUDE.md` to the upstream clone | skill: do not invent a pin file |

## Stakeholders
| Name | Role | Interest | Consulted or informed |
|---|---|---|---|
| — | — | no product owner | n/a |

## History
Run 9 used boltons because Plausible had no `mix`. Ripgrep chosen because Rust + Cargo.lock + a CI pin above the machine's `rustc 1.90.0`.

## Open questions
| # | Question | Who can answer | Blocking? |
|---|---|---|---|
| — | none for this spike | | |

## Assumptions
- CI `ci.yml` is the build workflow `[confirmed: triage rank 7, only PR workflow]`
- `rust-version = "1.96"` is the floor, not a request for nightly `[confirmed: Cargo.toml [workspace.package]; README Building]`

## Planned sequence
1. `env-bootstrap` — the skill under test
2. Record in `VALIDATION.md`

## Log
| Date | Change |
|---|---|
| 2026-08-17 | Charter created for the cold-start |
