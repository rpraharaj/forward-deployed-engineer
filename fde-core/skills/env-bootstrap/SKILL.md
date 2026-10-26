---
name: env-bootstrap
description: Get a working build, test, and run loop in an unfamiliar repository on a locked-down machine - read the CI config as ground truth for how the software is actually built, check toolchain versions against the repo's pins, configure internal registries and proxies, start required services, and record every workaround discovered so the next person does not rediscover them. Use on the first day in a repo, when a build fails and you do not know why, when tests will not run locally, when someone says "it works on my machine", or when onboarding documentation is missing or stale. Produces the environment doc the rest of the engagement depends on.
---

# Environment bootstrap

Getting to a green build in someone else's repository.

## Why this exists

You cannot map, change, or verify a system you cannot run. Bootstrap is therefore the first hard gate of an engagement, and in enterprise environments it routinely eats two or three days — not because it's difficult, but because the knowledge is distributed: a version pin in one file, a registry credential in someone's shell profile, a service dependency nobody documented, and a workaround that exists only in a senior engineer's muscle memory.

The second reason this skill exists is durability. Every FDE who bootstraps a repo discovers the same six workarounds and writes down none of them. `01-environment.md` is how that stops.

## When this applies

- First day in a repository
- Build or tests fail locally and the cause isn't obvious
- "It works on my machine"
- Onboarding docs are missing, stale, or wrong

## When it doesn't

- The build already works and you can run the tests
- You only need to read code, not run it — `repo-recon` doesn't require a working build
- The failure is in CI rather than locally — that's `ci-forensics` *(fde-operate)*

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

Read `00-engagement.md`. Check `00b-access.md` too — a missing registry credential is an access problem wearing a build problem's clothes, and diagnosing it as the latter wastes a day.

## Procedure

### 1. Read the CI config before anything else

The highest-value step, and the one most people skip in favour of guessing at a build command.

CI configuration is **the only executable statement of how this software is actually built** that has to work every day. A README records what was true when someone last cared; CI is verified continuously.

Find the real build workflow using the triage in `../_shared/stack-detection.md` — mature repositories accumulate twenty automation workflows around one that builds. From it, extract:

- The exact build and test invocation, with flags and profiles
- Toolchain versions, which are usually pinned here and nowhere else
- Service containers the tests need
- Environment variables and secret **names**
- Any setup step that runs before the build

Copy the commands verbatim rather than paraphrasing them. The flags matter — a profile or a `-P` argument is frequently the difference between a build that works and one that doesn't.

### 2. Detect the stack and its pins

Follow `../_shared/stack-detection.md`. Two things specifically:

**Sub-manifest count.** One root manifest and a hundred below it is a workspace, and building a single module may not be a supported operation. Establish this before trying.

**Version pins.** Run the three-layer survey in `../_shared/stack-detection.md` (dedicated pin file → manifest field, including the workspace/root hoist → CI toolchain install). Compare each against what's actually installed.

An empty dedicated-file grep is **not** "unpinned." That command is layer 1 only. The version is often a field in the manifest you already opened, or a matrix key in the workflow from step 1.

Version mismatch is the single most common bootstrap failure, and the answer is nearly always already written down.

### 3. Prefer the repository's own tooling

Use the repository's own wrapper and the lockfile's package manager — names and pins live in `../_shared/stack-detection.md`. On a locked-down machine the global tool is frequently the wrong major version.

**Match the package manager to the lockfile.** Using the wrong one rewrites the lockfile and produces an enormous, unreviewable diff — a memorable way to introduce yourself.

### 4. Registries and proxies

If dependency resolution fails or hangs, this is usually why. See `../_shared/enterprise-constraints.md`.

Check for internal registry configuration in the files `../_shared/stack-detection.md` lists for this stack. Two failure modes: you lack credentials for the internal registry (an access problem — record it in `00b-access.md`), or the package genuinely isn't mirrored (a request with a lead time).

Never resolve a TLS error by disabling verification. It gets committed, and it's a finding in any subsequent audit.

### 5. Start what the build needs

`docker-compose.yml` and the CI config's service containers tell you what must be running — databases, brokers, caches, stubbed downstreams.

If Docker isn't available, find out what the team does instead: a shared dev database, an in-memory substitute, a profile that stubs the dependency. Ask rather than inventing an approach.

### 6. Config and secrets

Establish where configuration comes from for a local run, and where secrets come from. **Record locations, never values** — see `../_shared/workspace-conventions.md`.

An `.env.example` or a `application-local.yml` is the intended path. Where none exists, that's a gap worth fixing on the way out — see step 9.

### 7. Build, test, run — recording as you go

Work up the ladder, and **keep a log while you go, not afterwards**:

1. Dependencies resolve
2. It compiles
3. Unit tests pass
4. Integration tests pass
5. It starts
6. It responds to something

Write down every deviation from the documented path the moment you hit it. By the time you're finished you will have forgotten two of them, and those two are exactly what the next person needs.

Record the **baseline honestly**: which tests pass, which already fail, and how long the suite takes. Pre-existing failures are normal in enterprise repositories, and knowing about them now saves an hour later proving your change didn't cause them. `safe-change` reads this.

### 8. Stop at "good enough for the task"

You don't always need the full stack. If the work is a unit-testable change in one module, compiling and running that module's tests is sufficient — spending a day getting end-to-end integration tests running against six containers is over-investment.

State explicitly what you got working and what you didn't, so a later reader knows the limits of what's been verified.

### 9. Leave it better

If the bootstrap took a day and the fix was three lines in a README, contribute the three lines. It's cheap, it's visible, and it's the kind of thing that makes a team glad you're there. Where the gap is bigger — a missing `.env.example`, a broken setup script — raise it rather than silently working around it.

Copy the working build/test/run commands into `CLAUDE.md`. That is what stops the next session rediscovering the flags. A CI-only failure after a local green build is `ci-forensics` *(fde-operate)*.

## Output template

Write to `<workspace>/01-environment.md`:

```markdown
# Environment — <repo>

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** working | partial | blocked
**Source revision:** <repo>@<short SHA>
**Confidence:** <what you got running, what you didn't>

## What works
- [x] Dependencies resolve
- [x] Compiles
- [x] Unit tests
- [ ] Integration tests — blocked, see below
- [x] Runs locally

## Quickstart
<Copy-pasteable, in order. Assume the reader has nothing.>

```bash
# 1. toolchain
# 2. dependencies
# 3. services
# 4. build
# 5. test
# 6. run
```

## Toolchain
| Tool | Required | Pinned in | Notes |
|---|---|---|---|

## Services required
| Service | How to start | Needed for |
|---|---|---|

## Configuration
| What | Source for local | Notes |
|---|---|---|
| DB connection | `application-local.yml` | |
| API credentials | Vault `secret/<path>` — **location only** | |

## Test baseline
- **Passing:** <n> · **Pre-existing failures:** <n> · **Runtime:** <duration>
- **Known failures:** <which, and whether they're expected>

## Workarounds discovered
| Problem | Symptom | Fix | Why |
|---|---|---|---|
| Wrong toolchain | Compiler rejects the crate (`rust-version` / `engines` / equivalent) | Install the version the manifest or CI named; do not invent a pin file | Global install was below the floor |

<This table is the most valuable part of this document. Be generous with it.>

## Still blocked
| What | Why | Needs | Tracked in |
|---|---|---|---|

## Gaps worth fixing
<Missing docs, absent .env.example, broken setup script. Offer to fix rather than working around silently.>
```

## Common traps

**Guessing the build command instead of reading CI.** CI is the only statement of the build that's verified daily.

**Fighting a version mismatch you could have read.** Check all three pin layers before debugging the error.

**Treating a missing `.nvmrc` / `rust-toolchain.toml` as unpinned.** Layer 1 returning nothing is the same silent-zero as searching the wrong extension. Read the manifest field and the CI setup action.

**Wrong package manager for the lockfile.** Rewrites it, produces a huge diff, and is immediately visible.

**Disabling TLS verification to get past a proxy error.** It gets committed, and it's an audit finding.

**Not recording the workarounds.** The whole durable value of this skill. Write them down as you hit them — you'll forget by the end.

**Not recording pre-existing test failures.** Then spending an hour proving they aren't yours.

**Over-investing.** Getting six containers up for a change that needs one module's unit tests is a day you don't have.

**Silently working around a missing `.env.example`.** Fixing it is cheap, visible, and the sort of thing that makes a team glad you arrived.
