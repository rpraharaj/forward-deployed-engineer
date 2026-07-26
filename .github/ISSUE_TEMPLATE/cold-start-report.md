---
name: Cold-start test report
about: You pointed repo-recon at an unfamiliar codebase and found where it was wrong
title: "[cold-start] <stack> — <short description of what broke>"
labels: cold-start, validation
---

## Subject

**Repository:** <public URL, or "private — <stack>, <rough size>">
**Stack:** <language, framework, build system>
**Size:** <file count, from `git ls-files | wc -l`>
**Why this subject:** <what makes it different from Rust workspace / .NET monolith / XML-configured Java>

## What the procedure found

<What `repo-recon` produced — entry points, stack detection, module boundaries. Paste the numbers.>

```
e.g. entry points found: 4
```

## What's actually there

<The reality, with the command that shows it.>

```bash
# the command that reveals the truth
```

```
e.g. actual entry points: 200, declared in <mechanism>
```

## Why the procedure missed it

<Your diagnosis. This is the most valuable part — it's what determines whether the fix is a
pattern or a method.>

## Would a method fix it, or just a pattern?

<Every fix so far had to be generic. "Add X to the list" fixes one repo; "here's how to find
whatever the local equivalent of X is" fixes the class. Any idea which this is?>

## Anything that worked well

<Optional, and genuinely useful — it tells us which earlier fixes generalized.>

---

<!--
Reference: the three classes found so far
  1. Rust workspace  — don't assume the language
  2. .NET monolith   — don't assume the codebase uses its framework's vocabulary
  3. XML-config Java — don't assume the entry points are in the code at all

We think a fourth exists. See VALIDATION.md.
-->
