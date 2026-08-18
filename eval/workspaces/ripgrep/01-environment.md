# Environment — ripgrep

**Engagement:** env-bootstrap cold-start / ripgrep
**Author:** FDE
**Date:** 2026-08-17
**Status:** working
**Source revision:** BurntSushi/ripgrep@3fce3b5
**Confidence:** Local macOS aarch64 only. `cargo +1.96.0 test --workspace --features pcre2` green. Did not run the `unstable-index` job, `ci/test-complete`, or any `cross` target.

## What works
- [x] Dependencies resolve
- [x] Compiles (`cargo +1.96.0 build --workspace` and `--features pcre2`)
- [x] Unit tests
- [x] Integration tests (`tests/tests.rs` in the workspace suite)
- [x] Runs locally (`./target/debug/rg --version`, search smoke)

## Quickstart

```bash
git clone https://github.com/BurntSushi/ripgrep
cd ripgrep
# 1. toolchain — no rust-toolchain.toml in this repo. Default rustc 1.90.0 is below MSRV.
rustup toolchain install 1.96.0 --profile minimal   # do not rustup default unless you mean to
# 2. dependencies — Cargo.lock present; use cargo, do not rewrite the lockfile
# 3. services — none
# 4. build (CI, sans --verbose and sans cross)
cargo +1.96.0 build --workspace
cargo +1.96.0 build --workspace --features pcre2
# 5. test (CI pcre2 job, sans --verbose)
cargo +1.96.0 test --workspace --features pcre2
# 6. run
./target/debug/rg --version
./target/debug/rg 'pattern' path
```

## Toolchain
| Tool | Required | Pinned in | Notes |
|---|---|---|---|
| rustc / cargo | **1.96** floor | `Cargo.toml` `[workspace.package] rust-version = "1.96"` `[confirmed: Cargo.toml:54-55]`; README Building says 1.96.0 | Layer-1 pin-file grep: **empty**. No `rust-toolchain.toml`. |
| rustc (CI pinned job) | 1.96.0 | `.github/workflows/ci.yml` matrix `build: pinned` / `rust: 1.96.0` | Ubuntu. |
| rustc (CI this OS) | nightly | `ci.yml` `build: macos` / `rust: nightly` | Layers disagree. 1.96.0 compiled and tested green here; nightly is not required for this SHA. |
| cargo / lockfile | Cargo | `Cargo.lock` present | 12 `Cargo.toml` — workspace. |
| Installed (PATH) | rustc 1.90.0 (1159e78c4 2025-09-14) | rustup `stable` default | Stale stable. Left unchanged. |
| Installed (used) | rustc 1.96.0 (ac68faa20 2026-05-25) | `rustup toolchain install 1.96.0` | Invoked as `cargo +1.96.0`. |

## Services required
| Service | How to start | Needed for |
|---|---|---|
| none | — | no `docker-compose`, no CI service containers |

## Configuration
| What | Source for local | Notes |
|---|---|---|
| Runtime config | CLI flags / `.ignore` / gitignore | CLI search tool; no `.env` |
| Secrets | none | |

## Test baseline
- **Command:** `cargo +1.96.0 test --workspace --features pcre2`
- **Passing:** 1218 · **Failed:** 0 · **Ignored:** 3 · **Runtime:** 24.47s
- **Known failures:** none on this SHA
- **Not run:** `cargo test --workspace --features unstable-index` (CI's other local-ish job); `ci/test-complete` (zsh completions); `cross` targets
- **`--lib` only (earlier):** 738 passed, 1 ignored, 11.45s — subset, superseded by the workspace command above

## Workarounds discovered
| Problem | Symptom | Fix | Why |
|---|---|---|---|
| Layer-1 pin grep silent | `git ls-files \| grep -iE '…toolchain\|global\.json'` returned **nothing** | Read `[workspace.package] rust-version` and CI `rust:` | The pin is a manifest field + CI matrix, not a pin *file* |
| Default rustc below MSRV | `error: rustc 1.90.0 is not supported` — `ripgrep@15.2.0 requires rustc 1.96` (and eight `grep*` crates) | `rustup toolchain install 1.96.0`; `cargo +1.96.0 …` | rustup `stable` on this machine had not been updated; do not invent `rust-toolchain.toml` |
| Layers disagree | macos CI uses nightly; Cargo.toml / pinned job / README say 1.96 | Used 1.96.0 (the floor). Build and tests passed. | Nightly is CI's "latest", not the required compiler |
| `--verbose` | CI prefixes every cargo invocation with `--verbose` | Omitted locally | Noise, not behavior |
| rustup side effect | `rustup toolchain install` also ran `self-update` | None needed; default toolchain still 1.90.0 | Recorded so the next person is not surprised |

## Still blocked
| What | Why | Needs | Tracked in |
|---|---|---|---|
| — | — | — | — |

## Gaps worth fixing
- This repository's README already states MSRV 1.96.0. The gap is in **our** pin survey, not in ripgrep's docs. Fixed in `stack-detection.md` (three-layer survey) and `env-bootstrap` step 2.
- Did not add `CLAUDE.md` or a pin file to the throwaway clone.
