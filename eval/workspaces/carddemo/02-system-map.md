# System map — CardDemo

**Engagement:** fifth-class hunt / CardDemo
**Author:** FDE
**Date:** 2026-08-17
**Status:** draft
**Source revision:** aws-samples/aws-mainframe-modernization-carddemo@59cc6c2
**Confidence:** Map produced with the *post-fix* method. As-written procedure produced an empty map — see VALIDATION.md Run 11. Nothing executed on z/OS.

## Scope
The CardDemo application tree (`app/`). Not AWS M2 product configuration. Optional modules (`app-authorization-ims-db2-mq`, `app-transaction-type-db2`, `app-vsam-mq`) are named, not traced.

## At a glance
- **Purpose:** Credit-card management — accounts, cards, transactions, bill pay — online (CICS) and batch (JCL)
- **Size:** 329 files
- **Stack:** COBOL + CICS + JCL + VSAM; optional IMS / DB2 / MQ. **No package manifest, no lockfile, no CI.** `[confirmed: empty one-shot survey; case-folded mix 62 cpy / 55 jcl / 44 cbl / 21 bms]`
- **Activity:** 0 commits in 6 months; last commit 2025-10-16; 3 commits in 12 months; 32 total
- **Health:** `[unverified]` — no z/OS/CICS on this machine. No test files.

## Entry points
| Type | Entry | Handler | Notes |
|---|---|---|---|
| CICS | `CC00` | `COSGN00C` | Sign-on. Start here. `[confirmed: app/csd/CARDDEMO.CSD]` |
| CICS | `CM00` | `COMEN01C` | Main menu |
| CICS | `CAVW` / `CAUP` | `COACTVWC` / `COACTUPC` | Account view / update |
| CICS | `CCLI` / `CCDL` / `CCUP` / `CDV1` | `COCRDLIC` / `COCRDSLC` / `COCRDUPC` / `COCRDSEC` | Card list / view / update |
| CICS | `CT00` / `CT01` / `CT02` | `COTRN00C` / `COTRN01C` / `COTRN02C` | Transaction list / view / add |
| CICS | `CR00` / `CB00` | `CORPT00C` / `COBIL00C` | Reports / bill pay |
| CICS | `CA00`, `CU00`–`CU03` | `COADM01C`, `COUSR0xC` | Admin / users |
| CICS (optional) | `CPVS` `CPVD` `CP00` `CTLI` `CTTU` `CDRA` `CDRD` | see optional CSDs | IMS/DB2/MQ modules |
| Batch | 55 JCL members | mostly `IDCAMS` / utilities; app programs `CBTRN02C`, `CBACT04C`, `CBSTM03A`, … | `EXEC PGM=` `[confirmed]` |
| Scheduled | CA7 + Control-M (15 `<JOB>` in Control-M) | `app/scheduler/` | Not cron YAML |

**25** unique `DEFINE TRANSACTION` across all CSD files. **44** `PROGRAM-ID`. **21** BMS maps.

## Module map
| Module | Responsibility | Depends on | Notes |
|---|---|---|---|
| `app/cbl` | CICS and batch programs | `app/cpy`, CICS, VSAM | 44 programs |
| `app/cpy`, `app/cpy-bms` | Record layouts and maps | — | **the data model** |
| `app/jcl`, `app/proc` | Batch graph | programs + VSAM | |
| `app/csd` | CICS resource table | programs, files, maps | |
| `app/bms` | Screens | CICS | |
| `app/scheduler` | Daily job net | JCL | CA7 + Control-M |
| `app/app-authorization-ims-db2-mq` | Pending auths | IMS, DB2, MQ | optional |
| `app/app-transaction-type-db2` | Tran type ref data | DB2 | optional |
| `app/app-vsam-mq` | MQ + VSAM | MQ | optional |

Boundaries are `COPY` (359 includes), not `import`.

## Data
| Store | What lives there | Accessed via | Shared with |
|---|---|---|---|
| VSAM KSDS `ACCTDAT` | Accounts | CICS `DEFINE FILE` + copybooks | CICS + batch |
| VSAM `CARDDAT` / `CARDAIX` | Cards + AIX | CSD | |
| VSAM `CUSTDAT` | Customers | CSD | |
| VSAM `CCXREF` / `CXACAIX` | Card↔account xref | CSD | |
| VSAM `TRANSACT` | Transactions | CSD | |
| VSAM `USRSEC` | Users | CSD | |
| Copybooks (62) | Record layouts — 78 `01` levels | `COPY` | every program |
| DB2 (optional) | `TRANSACTION_TYPE`, `AUTHFRDS`, … | `*.ddl` | optional CICS |
| IMS (optional) | Auth databases | `*.dbd` / `*.psb` | optional CICS |

## Integrations
| System | Direction | Protocol | Where configured | Owner |
|---|---|---|---|---|
| CICS region | in | TRANSID | `app/csd/` | `[unverified]` ops |
| VSAM | both | CICS file / JCL IDCAMS | CSD + JCL | |
| MQ (optional) | both | MQPUT/MQGET — **377** hits | optional module | |
| IMS / DB2 (optional) | both | `EXEC SQL` 32; DBD/PSB | optional modules | |
| RACF | in | — | README | `[inferred]` |

## Test topology
- **Location:** none · **Kinds:** none · **Count:** 0 · **Runtime:** n/a · **Gates merge:** no CI
- **Coverage of the area we're changing:** none. `characterization-tests` before any change, and there is no local runner.

## Config and environments
| Environment | Config source | Notes |
|---|---|---|
| CICS region | `app/csd/*.CSD` | files, programs, transactions, mapsets |
| Batch | `app/jcl`, `app/proc`, `app/ctl` | |
| Schedule | `app/scheduler/CardDemo.ca7`, `CardDemo.controlm` | |
| Compile helpers | `scripts/*.sh` | FTP/JES to a remote region — not a local build |

## Churn hotspots
| File | Commits (12mo) | Why it matters |
|---|---|---|
| `app/scheduler/CardDemo.controlm` | 1 | schedule |
| `app/scheduler/CardDemo.ca7` | 1 | schedule |
| `app/cbl/CBIMPORT.cbl` / `CBEXPORT.cbl` | 1 each | last feature (data export/import) |

3 commits in 12 months. Quiet, not dead — a demo that still receives occasional additions.

## Landmines
| What | Where | Why it matters | Confidence |
|---|---|---|---|
| No tests, no CI | whole tree | any change is uncharacterized | `[confirmed]` |
| Optional modules not in base CSD | `app/app-*` | README lists 24 trans; base CSD has 18 | `[confirmed]` |
| Mixed-case extensions | `.cbl` vs `.CBL` | case-sensitive greps undercount | `[confirmed]` |
| Cannot run here | no z/OS | health `[unverified]` | `[confirmed]` |
| Default passwords in README | `ADMIN001` / `USER0001` | demo creds; do not treat as a secret store | `[confirmed: README]` |

## The five questions
1. **Enter:** CICS `CC00` → `COSGN00C`, or a JCL member via `EXEC PGM=`. `[confirmed: CSD + JCL]`
2. **Data:** VSAM files in the CSD; layouts in copybooks. Optional DB2/IMS. `[confirmed]`
3. **Talks to:** CICS, VSAM, optional MQ/IMS/DB2. `[confirmed]`
4. **Add a feature:** new copybook + program + CSD TRANSACTION/PROGRAM/MAPSET + BMS + JCL if batch.
5. **Scared to touch:** `POSTTRAN` / `CBTRN02C` (core posting), shared copybooks (`COCOM01Y`, `CSDAT01Y`), CSD file defs.

## Gaps
- No execution. Batch runtime and CICS install `[unverified]`.
- RACF and region topology are README-only.
- IMS/MQ optional path not mapped program-to-queue.
