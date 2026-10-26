# Contributing

Thanks for considering it. This project improves fastest through a specific kind of contribution, so here's what's most useful, in order.

---

## 1. Run a cold-start test 🔬

**The highest-value contribution, and it takes about twenty minutes.**

Every round of testing found something reasoning alone had missed — ten defects across three runs, each a more fundamental assumption than the last. The pattern is unmistakable: **the skills are wrong in ways nobody can predict from a desk.**

Five stacks are covered (Rust workspace, .NET monolith, XML-configured Java, Elixir/Phoenix, COBOL/CICS/JCL). Many aren't.

### How

1. Pick a real, substantial codebase in a stack we haven't tested. Something you know well is ideal — you can tell when the output is wrong.
2. Follow [`repo-recon`](fde-core/skills/repo-recon/SKILL.md) **exactly as written**, including [`entry-points-by-stack.md`](fde-core/skills/repo-recon/references/entry-points-by-stack.md).
3. Compare what it found against what's actually there.
4. Open an issue with the [cold-start report template](.github/ISSUE_TEMPLATE/cold-start-report.md).

### What we're looking for

Anywhere the procedure produced a **confidently wrong answer** — especially where a search returned few or zero results and that silence read as fact. That's the failure mode all three previous runs shared.

> *"It found 4 entry points. There are 200 — they're declared in a `.bnd` descriptor, not in code."*

That one paragraph is worth more than a new skill.

### Stacks we'd especially like

Salesforce Apex · Low-code platforms (OutSystems, Mendix, Power Platform) · Embedded C/C++ · Erlang (OTP without Phoenix) · Anything where there is no repository at all

**Six classes so far.** The latest: don't assume the files in the repository are the source of truth (`kubernetes-client/python` — 91% generated). Still open: low-code with no repo.

---

## 2. Report a procedure that didn't fit 🧭

**39 of 50 skills have no recorded procedure trial.** Four have at least partial repository-based trials: `repo-recon`, `blast-radius`, `env-bootstrap`, and `characterization-tests`. Seven additions have initial synthetic artifact trials, recorded in [VALIDATION.md](VALIDATION.md#run-16--seven-synthetic-procedure-trials), and remain experimental. Neither kind establishes live client-engagement effectiveness; shared-reference checks are counted separately.

If you used one on real work and the steps were wrong for your situation — a missing step, an ordering that doesn't hold, a stopping condition that fired too early — that's the highest-signal feedback available, and it can't be obtained any other way.

You don't need a fix. Describing the mismatch is the contribution.

---

## 3. Write or improve a skill ✍️

### House style

Full detail in [DESIGN.md §8](DESIGN.md). The rules that matter most:

**No stack specifics in a `SKILL.md` body.** Maven, npm, `pytest`, `@RestController`, `--include="*.java"` — none of it belongs in the main file. Bind search extensions from `stack-detection.md` after detection. Stack knowledge goes in `references/`, loaded only when detection matches. *Three of our ten defects were violations of exactly this*, so it's enforced rather than preferred.

**Qualify pack skill names.** If a core skill mentions `cutover-plan` or `db-change-management`, say which pack it lives in so a core-only install does not invoke a missing skill.

**Explain why, don't issue rules.** A skill that says "ALWAYS do X" gets followed mechanically. One that explains what goes wrong without X gets applied with judgment — which matters, because these run in environments we can't anticipate.

**Every skill produces a named artifact.** Output that lives only in the terminal doesn't survive the engagement.

**State the stopping condition.** Comprehension skills without one run until context is exhausted.

**Keep `SKILL.md` under ~250 lines.** Depth goes one level down into `references/`.

### Structure

```
skill-name/
├── SKILL.md              # frontmatter (name, description) + body
└── references/           # optional, loaded on demand
```

Body sections:
```markdown
## When this applies / when it doesn't
## Prerequisites          ← upstream artifacts, and what to do if missing
## Procedure              ← cheap steps first; explicit stopping condition
## Output template        ← the exact artifact structure
## Common traps           ← failure modes specific to this activity
```

### The description field

This is the **only** triggering mechanism. It must say what the skill does *and* the concrete situations that should invoke it, phrased the way someone would actually describe the moment.

Lean slightly assertive — under-triggering is the common failure. But bound it: our one triggering defect came from writing *"Run this before any other FDE skill,"* which turned an entry-point skill into a catch-all.

### Test your triggering

Before opening a PR, check your skill doesn't steal queries from existing ones:

```bash
# Set up the evaluator in an isolated Python environment (3.10+).
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r eval/requirements.txt

# Offline regression tests; these make no model calls.
python3 -m unittest discover -s eval -p 'test_*.py' -v

# Run the expanded suite (82 queries) without overwriting historic results.
# Requires `grok` on PATH.
python3 eval/run-trigger-eval.py --out eval/trigger-results-expanded.json

# Claude rematch (needs a working Anthropic path — not an OpenRouter remap).
# Writes eval/trigger-results-claude.json so it does not overwrite the Grok run.
python3 eval/run-trigger-eval.py --judge claude --out eval/trigger-results-expanded-claude.json
```

Or a single ad-hoc query:

```bash
# 1. Build the description list
python3 - <<'PY' > /tmp/skills.txt
import runpy
runner = runpy.run_path('eval/run-trigger-eval.py')
print(runner['load_skills']())
PY

# 2. Ask which skill fires for a realistic query
printf 'You are Claude Code. These skills are available:\n\n%s\n\nA user says:\n"%s"\n\nWhich skill(s) would you invoke? Reply with ONLY skill names, comma-separated, most relevant first (max 2). If none apply, reply exactly NONE. No explanation.' \
  "$(cat /tmp/skills.txt)" "your realistic test query here" | grok --single --output-format plain
```

Test both directions: your skill wins its own queries, **and** neighbouring skills still win theirs. Include the results in your PR.

The evaluator parses real YAML, including quoted and folded descriptions, and rejects malformed metadata before calling a judge. A reply must contain one or two known skill names, comma-separated, or exactly `NONE` (inline Markdown formatting is tolerated). Empty replies, explanatory prose, unknown names, subprocess failures, and timeouts are errors, not negative passes. Failed cases and errors both return a nonzero exit status. Historic result files retain their original parser's scores; do not present them as a fresh run of the repaired evaluator.

### Trial the new procedures

`eval/procedure-scenarios.json` contains seven synthetic scenarios with requests, raw context, and review checks. Run each in a separate temporary engagement workspace. Give a fresh session the named skill, request, and context; withhold the review checks until inspecting the artifact. Compare with a baseline that has no skill. Use only permitted local resources and synthetic state; do not contact people, make paid model calls, or mutate external systems as part of a scenario without separate authorization.

Record the produced artifact, environment/revision, checks met/missed, evidence, and limitations in `VALIDATION.md`. A fixture that parses correctly or a well-formed template is not an executed procedure trial. Favor observed corrections over extra universal rules.

The first executed set is in `eval/procedure-results.json`, with complete synthetic artifact snapshots in `eval/procedure-trials/run-16/`. It includes seven baselines, seven skill-assisted trials, and three standalone optional-pack retests. Preserve those snapshots; use a new run directory and result file for later trials.

---

## 4. Propose a new pack 📦

`fde-core` plus six optional packs is the current split. Sensible extensions:

- Industry verticals — `fde-fintech`, `fde-healthcare`, `fde-public-sector`
- Compliance regimes — regional data protection, sector-specific regulation
- Platform-specific — deeper SAP, Salesforce, or ServiceNow coverage

Open an issue to discuss the boundary before building. The test for a separate pack is whether the skills fire on a *specific engagement type* rather than universally — that's what keeps `fde-core`'s always-on context cost down.

---

## PR checklist

- [ ] `name:` in frontmatter matches the directory name exactly
- [ ] `description:` covers what it does **and** when to invoke it
- [ ] No stack-specific patterns in the `SKILL.md` body
- [ ] Under ~250 lines; depth pushed into `references/`
- [ ] Produces a named artifact with the standard header
- [ ] Has an explicit stopping condition, if it's a comprehension skill
- [ ] Cross-references resolve (`../_shared/...`, `references/...`)
- [ ] Triggering tested in both directions, results included

Run the structural checks:

```bash
# Validate the marketplace and every pack with Claude's runtime-aware validator.
claude plugin validate . || exit 1
for pack in fde-core fde-data fde-migration fde-platform fde-operate fde-product fde-ai; do
  claude plugin validate --strict "$pack" || exit 1
done

for f in fde-*/skills/*/SKILL.md; do
  d=$(dirname "$f")
  [ "$(sed -n '2s/^name: //p' "$f")" = "$(basename $d)" ] || echo "NAME MISMATCH: $d"
  grep -o "\.\./[a-z_-]*/\(references/\)\?[a-z-]*\.md\|references/[a-z-]*\.md" "$f" | sort -u | while read r; do
    [ -f "$d/$r" ] || echo "BROKEN REF: $(basename $d) -> $r"
  done
done
```

---

## What we won't merge

- Skills that duplicate what Claude Code already provides (`/code-review`, `/security-review`)
- Stack-specific patterns in a `SKILL.md` body — push them down a level
- Skills with unbounded procedures and no stopping condition
- Claims in the docs that aren't backed by a test result. [VALIDATION.md](VALIDATION.md) states what's untested precisely, and that honesty is load-bearing — it's the same standard the skills demand of their users.

---

## Ground rules

Be decent to each other. Assume good faith. Critique the procedure, not the person who wrote it.

Contributions are MIT licensed, same as the project.
