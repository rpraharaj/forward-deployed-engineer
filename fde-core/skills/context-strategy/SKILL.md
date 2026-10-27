---
name: context-strategy
description: Work effectively in a codebase far larger than any context window, across an engagement that spans many sessions. Decide what to read versus search versus script versus delegate, maintain a durable working guide so each session does not re-derive the same map, define a working set, and hand off cleanly when context runs low. Use when a repository is too large to explore file-by-file, when context is filling up mid-task, when starting a multi-session engagement, when you catch yourself re-discovering something you already worked out, or when someone says "this repo is huge". Run before repo-recon when the tree is large; this sets the budget, it does not replace the system map.
---

# Context strategy

The craft of staying effective when the system is bigger than what you can hold.

## Why this exists

Every coding agent has a finite context window. Enterprise repositories do not respect it — a monorepo with forty thousand files exceeds any window by orders of magnitude, and the naive approach (start reading, keep reading) fails in a specific and expensive way: context fills with low-value file contents, the genuinely important findings get summarized away, and the next session starts from zero and re-derives the same partial map.

The fix isn't reading faster. It's deciding, deliberately and repeatedly, **what deserves to occupy context** — and writing everything else down where it survives.

## When this applies

- A repository too large to survey file by file
- Any engagement spanning more than one session
- Context filling up while a task is unfinished
- Re-discovering something you worked out earlier — the clearest signal this skill is needed
- Before `repo-recon` on anything large, to set the budget

## When it doesn't

- Small, well-understood repository, single session — just work
- A one-off question with a known answer location
- "Help me understand this repo" when you need a map — that is `repo-recon`. Run this first only to set a budget on a large tree.

## Prerequisites

Resolve `<workspace>` before reading or writing artifacts: read `../_shared/workspace-conventions.md` and follow its location and header rules. All artifact paths below use that resolved workspace. Preserve existing sections when appending.

`00-engagement.md` if it exists — it scopes which subtree matters. If there is no workspace yet, still set the budget in the response, then persist `00c-context.md` after `fde-orient` creates the chosen workspace. Do not scatter artifacts next to the checkout or invent a system map.

## Procedure

### 1. Size the problem before entering it

Thirty seconds, and it determines everything downstream. **Do not** `xargs wc` the tree or run `git log` once per file — those hang on the repositories this skill is for.

```bash
git ls-files | wc -l
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
du -sh .git
```

| Scale | Approach |
|---|---|
| **< 500 files** | Read freely. Structure barely matters. |
| **500 – 5,000** | Survey structurally, read selectively. Working set discipline starts paying. |
| **5,000 – 50,000** | Never read broadly. Search and script first, read only the working set. The working guide becomes essential. |
| **> 50,000** | Treat subdirectories as separate repositories. Scope hard to one, and say so in every artifact. |

Record the file count in `00c-context.md`. When `repo-recon` runs, it copies that number into the system map. It calibrates every claim you'll make about coverage.

### 2. Choose the cheapest tool that answers the question

The core discipline. Before opening a file, ask what kind of question this is.

| Question shape | Right tool | Wrong move |
|---|---|---|
| "Where is X defined?" | Grep for the definition | Reading candidate files |
| "How many / which files / how often?" | Shell one-liner, count the output | Reading and tallying by hand |
| "What does this one flow do?" | Read the ~5–15 files on the path | Reading the whole module |
| "What's the overall shape?" | Directory listing + entry points | Reading representative files |
| "Does this pattern appear elsewhere?" | Grep with context, count first | Opening each hit |
| "Broad survey across many areas" | Delegate to a subagent, keep the conclusion | Doing it inline and filling context |

**The counting habit is worth building.** Before reading any grep result, count it:

```bash
# Bind EXT from stack-detection / the extension counts in step 1
grep -rl "<SymbolOrTerm>" --include="*.$EXT" . | wc -l
```

Three hits: read them. Two hundred: you asked the wrong question — narrow it, or you're about to spend most of your context on one term.

### 3. Write a script when the question is mechanical

If a question is "the same lookup, many times," writing ten lines of shell or Python is dramatically cheaper than reading files, and it produces a **checkable, re-runnable** answer rather than an impression. This is the highest-leverage habit in the skill and the most consistently underused.

```bash
# Which modules mention the legacy client? Bind EXT from detection.
grep -rl "<LegacyClientName>" --include="*.$EXT" . \
  | awk -F/ '{print $1"/"$2"/"$3}' | sort -u

# Where does churn concentrate? (the files that will bite you)
git log --format= --name-only --since="12 months ago" \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -30
```

Do **not** loop `git log -1` over every file to find dead zones. That is one process per path and will consume the session. If you need untouched areas, sample top-level directories (`git log -1 --format=%ad -- <dir>`) or ask `repo-recon` step 6, which already filters noise.

Put anything you'll re-run into the scratchpad, and mention the useful ones in the working guide so the next session doesn't reinvent them.

The output of a script is also *citable* under `../_shared/evidence-discipline.md` — command plus output is a valid citation, and it upgrades a claim from `[inferred]` to `[confirmed]` for free.

### 4. Delegate breadth, keep only conclusions

When subagents are available and delegation is authorized, they're the right instrument for breadth-first questions across many locations: their exploration burns *their* context, and only the conclusion returns to yours.

Good delegations: "find every place the retry policy is configured", "which services publish to this topic", "survey how error handling is done across these six modules".

Two rules. **Ask for a conclusion, not a file dump** — otherwise the context you saved comes straight back. And **specify the search breadth**, because an under-specified survey either stops too early or explores forever.

If subagents are unavailable or delegation is not authorized, do the same thing with scripts and record only the summary.

### 5. Define the working set

For any given task, name the files that actually matter — typically five to fifteen. Write the list down at the top of your task notes:

```markdown
## Working set — add currency to refund flow
- <module>/RefundService:88-160   ← the change lands here
- <module>/RefundRequest          ← DTO, needs the field
- <module>/CurrencyConverter      ← existing helper, reuse
- db/migration/…                  ← schema
- <module>/RefundServiceTest      ← characterization target
```

Everything else is reference, reachable by grep when needed. When the working set grows past about twenty files, the task is too big — split it. That's a useful signal rather than an inconvenience.

### 6. Maintain a durable working guide

Use `../_shared/agent-context.md` to choose the guide: preserve the team's existing instruction file, or use `<workspace>/repo-guide.md` when none exists. Record the path and read it explicitly at session start; automatic loading differs between agents.

**Belongs in the working guide:**

- Exact build, test, and run commands — including the flags that matter
- The layout map: which directory does what, in one line each
- Conventions that differ from the language default
- Landmines: files that look safe and aren't, and why
- Where things live: config, migrations, secrets *(locations, never values)*
- Useful one-liners discovered while exploring
- The stack summary from `../_shared/stack-detection.md`

**Does not belong:**

- Anything a grep answers in two seconds
- Full file contents or long code excerpts
- Engagement narrative — that's `<workspace>/`, not the working guide
- Speculation. If it's `[inferred]`, tag it, or leave it out.

Aim for well under 200 lines. A bloated guide wastes context whenever it is loaded and eventually gets skimmed rather than read — the same failure as an over-long README, with a per-session price.

If the repository already has a working guide, extend it rather than replacing it, and keep your additions in the existing voice. Rewriting a team's file is a bad first impression.

### 7. Watch the context budget and hand off deliberately

Notice when context is filling. The failure mode is not running out — it's running out *mid-task* and losing findings you never wrote down.

When you're roughly two-thirds through and the task isn't done, stop and persist:

1. Write findings to the relevant `<workspace>/` artifact **with citations** — a finding without a citation is one you'll have to re-derive
2. Update the working guide with anything durable
3. Note the working set and the exact next step
4. Then continue

The test: **if this session ended right now, could a fresh session pick up from the files on disk alone?** If not, you have unwritten state, and it's about to be lost.

### 8. Structure long engagements around artifacts, not memory

Across weeks, the `<workspace>/` workspace is the engagement's memory and each session is stateless. Start a session by reading the artifacts relevant to today's task — not by re-exploring — and end it by updating them.

An FDE re-deriving the system map in week three has a workspace problem, not a memory problem.

### 9. Stop

You have enough when all of these are true:

1. File count and scale band are recorded
2. A working set of at most fifteen files is named (or explicitly "none yet — waiting on recon")
3. The working guide is updated, or you wrote down why it was deferred
4. The next step is written so a fresh session can start

Do not keep surveying. Breadth belongs to `repo-recon`.

## Output template

Write to `<workspace>/00c-context.md`:

```markdown
# Context strategy

**Engagement:** <name>
**Author:** FDE
**Date:** <YYYY-MM-DD>
**Status:** draft
**Source revision:** <repo>@<short SHA>
**Confidence:** scale is confirmed from `git ls-files`; working set is a judgment

## Scale
- **Files:** <n> · **Band:** <500 | 5k | 50k | above>
- **Scope:** <subtree, or whole repo>
- **Approach:** <from the table in step 1>

## Working set
<the 5–15 files for the current task, or "none — recon not run">

## Working guide
<path; updated | deferred because …>

## Next step
<one sentence a fresh session can execute>
```

## Common traps

**Reading to feel informed.** Reading a file you have no specific question about is almost always waste. Have the question first.

**Grepping without counting.** Two hundred hits will consume your context if you start opening them. Count, then narrow.

**Doing mechanically what a script does better.** Ten lines of shell beats twenty file reads, and unlike the reads it's re-runnable and citable.

**Letting subagents return file contents.** Ask for conclusions. A delegation that dumps files back has moved the cost, not removed it.

**Treating the working guide as documentation.** It's a working aid for the next session. Write what you'd want to be told, not what a newcomer would want explained.

**Discovering something important and not writing it down.** The one unrecoverable mistake — context is lost silently, and you won't remember what you knew.

**Re-exploring at the start of each session.** If that's happening, the artifacts aren't carrying enough. Fix the artifacts.

**Scoping to a whole monorepo.** "I mapped the repo" is not credible above about fifty thousand files, and a reader who trusts it will be misled. Scope hard, and say what you scoped to.
