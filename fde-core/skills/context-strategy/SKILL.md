---
name: context-strategy
description: Work effectively in a codebase far larger than any context window, across an engagement that spans many sessions. Decide what to read versus search versus script versus delegate, build a durable CLAUDE.md so each session does not re-derive the same map, define a working set, and hand off cleanly when context runs low. Use when a repository is too large to explore file-by-file, when context is filling up mid-task, when starting a multi-session engagement, when you catch yourself re-discovering something you already worked out, or when someone says "this repo is huge" or "where do I even start reading". Especially important in monorepos and legacy enterprise systems.
---

# Context strategy

The craft of staying effective when the system is bigger than what you can hold.

## Why this exists

An FDE's only tool is Claude Code, and Claude Code has a finite context window. Enterprise repositories do not respect it — a monorepo with forty thousand files exceeds any window by orders of magnitude, and the naive approach (start reading, keep reading) fails in a specific and expensive way: context fills with low-value file contents, the genuinely important findings get summarized away, and the next session starts from zero and re-derives the same partial map.

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

## Procedure

### 1. Size the problem before entering it

Thirty seconds, and it determines everything downstream:

```bash
git ls-files | wc -l
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
git ls-files | xargs wc -l 2>/dev/null | tail -1
du -sh .git
```

| Scale | Approach |
|---|---|
| **< 500 files** | Read freely. Structure barely matters. |
| **500 – 5,000** | Survey structurally, read selectively. Working set discipline starts paying. |
| **5,000 – 50,000** | Never read broadly. Search and script first, read only the working set. `CLAUDE.md` becomes essential. |
| **> 50,000** | Treat subdirectories as separate repositories. Scope hard to one, and say so in every artifact. |

Record the number in `02-system-map.md`. It calibrates every claim you'll make about coverage.

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
grep -rl "PaymentProcessor" --include="*.java" . | wc -l
```

Three hits: read them. Two hundred: you asked the wrong question — narrow it, or you're about to spend most of your context on one term.

### 3. Write a script when the question is mechanical

If a question is "the same lookup, many times," writing ten lines of shell or Python is dramatically cheaper than reading files, and it produces a **checkable, re-runnable** answer rather than an impression. This is the highest-leverage habit in the skill and the most consistently underused.

```bash
# Which modules import the legacy client?
grep -rl "com.acme.legacy.Client" --include="*.java" src/ \
  | cut -d/ -f1-3 | sort -u

# Endpoints, in one pass
grep -rhoE "@(Get|Post|Put|Delete)Mapping\([^)]*\)" --include="*.java" src/ | sort -u

# Where does churn concentrate? (the files that will bite you)
git log --format= --name-only --since="12 months ago" \
  | grep -v '^$' | sort | uniq -c | sort -rn | head -30

# Anything not touched in two years — candidate dead zones
git ls-files | while read f; do
  echo "$(git log -1 --format=%ad --date=short -- "$f") $f"
done | sort | head -30
```

Put anything you'll re-run into the scratchpad, and mention the useful ones in `CLAUDE.md` so the next session doesn't reinvent them.

The output of a script is also *citable* under `../_shared/evidence-discipline.md` — command plus output is a valid citation, and it upgrades a claim from `[inferred]` to `[confirmed]` for free.

### 4. Delegate breadth, keep only conclusions

When subagents are available, they're the right instrument for breadth-first questions across many locations: their exploration burns *their* context, and only the conclusion returns to yours.

Good delegations: "find every place the retry policy is configured", "which services publish to this topic", "survey how error handling is done across these six modules".

Two rules. **Ask for a conclusion, not a file dump** — otherwise the context you saved comes straight back. And **specify the search breadth**, because an under-specified survey either stops too early or explores forever.

If subagents aren't available, do the same thing with scripts and record only the summary.

### 5. Define the working set

For any given task, name the files that actually matter — typically five to fifteen. Write the list down at the top of your task notes:

```markdown
## Working set — add currency to refund flow
- src/refunds/RefundService.java:88-160   ← the change lands here
- src/refunds/RefundRequest.java          ← DTO, needs the field
- src/payments/CurrencyConverter.java     ← existing helper, reuse
- db/migration/V218__refunds.sql          ← schema
- src/refunds/RefundServiceTest.java      ← characterization target
```

Everything else is reference, reachable by grep when needed. When the working set grows past about twenty files, the task is too big — split it. That's a useful signal rather than an inconvenience.

### 6. Make `CLAUDE.md` the durable memory

The single highest-return artifact for a long engagement. It loads automatically each session, so anything in it is knowledge you never re-derive.

**Belongs in `CLAUDE.md`:**

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
- Engagement narrative — that's `.fde/`, not `CLAUDE.md`
- Speculation. If it's `[inferred]`, tag it, or leave it out.

Aim for well under 200 lines. A bloated `CLAUDE.md` costs context every single session and eventually gets skimmed rather than read — the same failure as an over-long README, with a per-session price.

If the repository already has a `CLAUDE.md`, extend it rather than replacing it, and keep your additions in the existing voice. Rewriting a team's file is a bad first impression.

### 7. Watch the context budget and hand off deliberately

Notice when context is filling. The failure mode is not running out — it's running out *mid-task* and losing findings you never wrote down.

When you're roughly two-thirds through and the task isn't done, stop and persist:

1. Write findings to the relevant `.fde/` artifact **with citations** — a finding without a citation is one you'll have to re-derive
2. Update `CLAUDE.md` with anything durable
3. Note the working set and the exact next step
4. Then continue

The test: **if this session ended right now, could a fresh session pick up from the files on disk alone?** If not, you have unwritten state, and it's about to be lost.

### 8. Structure long engagements around artifacts, not memory

Across weeks, the `.fde/` workspace is the engagement's memory and each session is stateless. Start a session by reading the artifacts relevant to today's task — not by re-exploring — and end it by updating them.

An FDE re-deriving the system map in week three has a workspace problem, not a memory problem.

## Common traps

**Reading to feel informed.** Reading a file you have no specific question about is almost always waste. Have the question first.

**Grepping without counting.** Two hundred hits will consume your context if you start opening them. Count, then narrow.

**Doing mechanically what a script does better.** Ten lines of shell beats twenty file reads, and unlike the reads it's re-runnable and citable.

**Letting subagents return file contents.** Ask for conclusions. A delegation that dumps files back has moved the cost, not removed it.

**Treating `CLAUDE.md` as documentation.** It's a working aid for the next session. Write what you'd want to be told, not what a newcomer would want explained.

**Discovering something important and not writing it down.** The one unrecoverable mistake — context is lost silently, and you won't remember what you knew.

**Re-exploring at the start of each session.** If that's happening, the artifacts aren't carrying enough. Fix the artifacts.

**Scoping to a whole monorepo.** "I mapped the repo" is not credible above about fifty thousand files, and a reader who trusts it will be misled. Scope hard, and say what you scoped to.
