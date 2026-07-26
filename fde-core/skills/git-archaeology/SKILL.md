---
name: git-archaeology
description: Recover intent from history when code looks wrong - blame to commit to pull request to linked ticket, plus revert and hotfix patterns - so you find out why something is the way it is before removing it. Use when code looks unnecessary or bizarre, before deleting anything odd, when a constant or special case has no explanation, when a comment contradicts the code, or when you are about to say "this can be simplified". Exists specifically to prevent Chesterton's Fence mistakes, where the ugly branch turns out to be an incident fix and removing it reopens the incident.
---

# Git archaeology

Finding out why, before you change it.

## Why this exists

An FDE reads a lot of code that looks wrong. Some of it is. Much of it is an incident fix, a regulatory requirement, a workaround for a downstream system's bug, or a special case for one customer worth more than the rest combined.

The odd-looking code is odd *because* something happened. Removing it re-creates whatever it was preventing — usually silently, usually in production, and usually with your name on the commit.

You are the person least equipped to tell the difference. The permanent team carries the scar tissue; you don't. History is how you acquire it in three minutes instead of three years.

## When this applies

- Code looks unnecessary, bizarre, or over-complicated
- Before deleting anything you don't understand
- A magic number or special case with no explanation
- A comment that contradicts the code
- You're about to say "this can be simplified"
- A `[confirmed]` claim you want to upgrade with the reasoning behind it

## When it doesn't

- Code you already understand
- Genuinely new code with no history
- You need runtime behavior rather than intent — that's `trace-the-flow`
- Shallow clone with no history — say so and tag conclusions `[unverified]`

## Procedure

### 1. Blame the specific lines

```bash
git blame -L 88,120 path/to/File.java
# Follow through moves and reformatting, which otherwise hide the real author
git blame -w -C -C -L 88,120 path/to/File.java
```

`-w` ignores whitespace changes, `-C -C` follows code moved between files. Without them, blame frequently points at whoever last reformatted the file, which tells you nothing and wastes the step.

### 2. Read the whole commit, not just the line

```bash
git show <sha>
git show <sha> --stat
```

The commit message may be useless, but the *other files in the same commit* are informative. A one-line change to a retry constant, committed alongside a monitoring alert threshold and a runbook edit, is visibly an incident response even when the message says "fix".

### 3. Find the pull request and the ticket

```bash
# Merge commit referencing the PR
git log --merges --ancestry-path <sha>..HEAD | head -20
# Ticket references anywhere in the history of this file
git log --format="%h %s" -- path/to/File.java | grep -oE "[A-Z]+-[0-9]+" | sort -u
```

Where `gh` or `glab` is available, the PR discussion is usually where the real reasoning lives — far more than the commit message:

```bash
gh pr view <n> --comments 2>/dev/null
```

Where it isn't, the ticket ID is still valuable: someone with access can look it up in a minute, and it's a good question for `knowledge-interview`.

### 4. Look for the revert-and-reapply pattern

The strongest possible signal that something is load-bearing.

```bash
git log --all --oneline --grep="revert" -i -- path/to/File.java
git log --all --oneline --grep="hotfix\|incident\|INC-\|P1\|urgent" -i -- path/to/File.java
```

Code that was removed and then put back means someone already tried your idea. Find out what happened to them. This single check has the best effort-to-value ratio in the skill.

### 5. Check whether the change was made under pressure

Commits authored at 3am, on a weekend, or in a burst of several within an hour are almost always incident response. That context changes how you read the code entirely — it was written to stop something, fast, and the ugliness is a symptom of urgency rather than of poor judgment.

```bash
git log --format="%h %ad %an %s" --date=format:'%Y-%m-%d %H:%M %a' -- path/to/File.java | head -20
```

### 6. Reach a verdict, and record it

Four outcomes, and they lead to different actions:

| Verdict | What to do |
|---|---|
| **Load-bearing, reason found** | Leave it. Add a comment explaining why, citing the commit — that's a real contribution. |
| **Load-bearing, reason not found** | Leave it. Record it as `[unverified]` and as a question for someone who was there. |
| **Genuinely obsolete** | Removable — cite the evidence that made it obsolete, in the PR description. |
| **No history** | Pre-dates the repository, or was squashed away. Treat as load-bearing until someone confirms otherwise. |

**When in doubt, it stays.** The cost of leaving odd code in place is a little ugliness. The cost of removing an incident fix is the incident.

Where you find the reason, **write it down in the code** as a comment with the commit reference. That comment is often worth more than any change you were planning, and it means the next person doesn't repeat this investigation.

## Output

Usually inline — a comment in the code and a note in whichever artifact prompted the question. Where the finding is significant, append to the relevant trace or feasibility entry:

```markdown
### Why `MAX_RETRIES = 3` (RefundClient:47)

**Verdict:** load-bearing
**Evidence:** commit `8b21f0`, 2021-11-04 02:41 Sat, alongside an alert threshold change
and a runbook edit — incident response `[confirmed]`. Ticket INC-4471 referenced.
**Meaning:** the downstream provider was flapping; 3 was empirical, not principled.
**Implication:** safe to change only with evidence about current downstream behavior.
Not a cleanup candidate.
```

## Common traps

**Blame without `-w -C -C`.** Points at whoever reformatted the file. Tells you nothing.

**Reading the message, not the commit.** Messages are often useless; the accompanying files are not.

**Not checking for reverts.** The single highest-value check, and the fastest.

**Assuming no explanation means no reason.** It usually means the reason was obvious to someone who is no longer here.

**Removing it because the author left.** Their departure is why nobody can defend the code, not evidence it's wrong.

**Finding the reason and not writing it down.** The next person repeats the whole investigation, and the one after that.

**Treating a squashed or migrated history as an absence of history.** Repositories migrated between VCS systems often lose everything before the migration date. Check whether the earliest commit is suspiciously large and recent.
