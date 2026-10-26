#!/usr/bin/env python3
"""Trigger discrimination eval. Same prompt as CONTRIBUTING.md.

Judges: grok --single (default) or claude -p (--judge claude).
Skills are presented only as name+description; no SKILL.md bodies, no tools.

    python3 eval/run-trigger-eval.py
    python3 eval/run-trigger-eval.py --judge claude --out eval/trigger-results-claude.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
QUERIES = Path(__file__).resolve().parent / "trigger-queries.json"
SKILL_GLOB = "fde-*/skills/*/SKILL.md"
KNOWN = set()


def load_skills() -> str:
    lines = []
    KNOWN.clear()
    for f in sorted(ROOT.glob(SKILL_GLOB)):
        source = f.read_text(encoding="utf-8").splitlines()
        label = f.relative_to(ROOT)
        if not source or source[0] != "---":
            raise ValueError(f"{label}: missing YAML frontmatter")
        try:
            end = source.index("---", 1)
        except ValueError as exc:
            raise ValueError(f"{label}: missing YAML frontmatter closing delimiter") from exc
        try:
            metadata = yaml.safe_load("\n".join(source[1:end]))
        except yaml.YAMLError as exc:
            raise ValueError(f"{label}: invalid YAML frontmatter") from exc
        if not isinstance(metadata, dict):
            raise ValueError(f"{label}: frontmatter must be a mapping")
        name, desc = metadata.get("name"), metadata.get("description")
        if not isinstance(name, str) or name != f.parent.name:
            raise ValueError(f"{label}: name must match the skill directory")
        if not isinstance(desc, str) or not desc.strip():
            raise ValueError(f"{label}: description must be a nonempty string")
        if name in KNOWN:
            raise ValueError(f"{label}: duplicate skill name {name}")
        KNOWN.add(name)
        lines.append(f"- {name}: {' '.join(desc.split())}")
    if not lines:
        raise ValueError("No skills found")
    return "\n".join(lines)


def build_prompt(skills: str, query: str) -> str:
    return (
        "You are Claude Code. These skills are available:\n\n"
        f"{skills}\n\n"
        "A user says:\n"
        f'"{query}"\n\n'
        "Which skill(s) would you invoke? Reply with ONLY skill names, "
        "comma-separated, most relevant first (max 2). If none apply, "
        "reply exactly NONE. No explanation."
    )


def parse_reply(raw: str) -> list[str]:
    """Require the answer format requested by build_prompt; never guess from prose."""
    text = re.sub(r"[*`]", "", raw).strip()
    if text.upper() == "NONE":
        return []
    picked = [part.strip() for part in text.split(",")]
    if not 1 <= len(picked) <= 2 or len(set(picked)) != len(picked):
        raise ValueError("Judge must return at most two distinct skill names or NONE")
    if any(name not in KNOWN for name in picked):
        raise ValueError("Judge returned an empty, unknown, or malformed answer")
    return picked


def ask_grok(prompt: str) -> tuple[str, str]:
    proc = subprocess.run(
        [
            "grok",
            "--single",
            prompt,
            "--output-format",
            "plain",
            "--disallowed-tools",
            "run_terminal_command,read_file,search_replace,write,grep,list_dir,"
            "web_search,web_fetch,spawn_subagent,use_tool,open_page,image_gen",
        ],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=180,
        check=True,
    )
    stdout = proc.stdout or ""
    return stdout, stdout


def ask_claude(prompt: str) -> tuple[str, str]:
    # Bare: no skills, no CLAUDE.md, no tools. Description list is the only context.
    proc = subprocess.run(
        [
            "claude",
            "-p",
            prompt,
            "--bare",
            "--output-format",
            "text",
            "--disallowed-tools",
            "Bash,Read,Edit,Write,Glob,Grep,WebSearch,WebFetch,Agent,Skill",
        ],
        cwd="/tmp",
        capture_output=True,
        text=True,
        timeout=180,
        env=os.environ.copy(),
        check=True,
    )
    stdout = proc.stdout or ""
    return stdout, stdout


def ask(skills: str, query: str, judge: str) -> tuple[str, list[str]]:
    prompt = build_prompt(skills, query)
    if judge == "claude":
        raw, stdout = ask_claude(prompt)
    else:
        raw, stdout = ask_grok(prompt)
    return raw, parse_reply(stdout)


def score_item(kind: str, item: dict, picked: list[str]) -> dict:
    expect = item.get("expect") or []
    accept_second = item.get("accept_second") or []
    first = picked[0] if picked else None
    if kind == "negatives" or (kind == "regressions" and expect == []):
        ok = picked == []
        # R05: pass if access-and-onboarding is not first (login 401)
        if item.get("id") == "R05":
            ok = first != "access-and-onboarding"
        verdict = "pass" if ok else "fail"
    else:
        ok_first = first in expect
        # known-acceptable: R10 / C05-style
        if not ok_first and first in accept_second and expect:
            verdict = "acceptable"
        else:
            verdict = "pass" if ok_first else "fail"
    return {
        "id": item["id"],
        "kind": kind,
        "query": item["query"],
        "expect": expect,
        "picked": picked,
        "verdict": verdict,
        "note": item.get("note", ""),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Trigger discrimination eval")
    ap.add_argument(
        "--judge",
        choices=("grok", "claude"),
        default="grok",
        help="grok --single (default) or claude -p. Claude needs a working Anthropic path.",
    )
    ap.add_argument(
        "--out",
        default=None,
        help="Results JSON (default: eval/trigger-results.json, or -claude.json for --judge claude)",
    )
    args = ap.parse_args()
    out = Path(args.out) if args.out else (
        ROOT / "eval" / ("trigger-results-claude.json" if args.judge == "claude" else "trigger-results.json")
    )

    spec = json.loads(QUERIES.read_text())
    try:
        skills = load_skills()
    except (OSError, ValueError) as exc:
        ap.error(str(exc))
    jobs = []
    for kind in ("positives", "negatives", "collisions", "regressions"):
        for item in spec[kind]:
            jobs.append((kind, item))

    results = []
    workers = 4
    print(f"Running {len(jobs)} queries with {workers} workers, judge={args.judge}…", flush=True)

    def run_one(pair):
        kind, item = pair
        raw, picked = ask(skills, item["query"], args.judge)
        row = score_item(kind, item, picked)
        row["judge"] = args.judge
        row["raw"] = raw.strip()[:400]
        return row

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}
        done = 0
        for fut in as_completed(futs):
            kind, item = futs[fut]
            try:
                row = fut.result()
            except Exception as e:
                # Subprocess exceptions include command arguments and may include
                # credentials in stderr. Persist only the failure class and status.
                if isinstance(e, subprocess.CalledProcessError):
                    note = f"Judge exited with status {e.returncode}"
                elif isinstance(e, subprocess.TimeoutExpired):
                    note = "Judge timed out"
                else:
                    note = str(e)
                row = {
                    "id": item["id"],
                    "kind": kind,
                    "query": item["query"],
                    "expect": item.get("expect") or [],
                    "picked": [],
                    "judge": args.judge,
                    "verdict": "error",
                    "note": note,
                    "raw": "",
                }
            results.append(row)
            done += 1
            print(
                f"[{done}/{len(jobs)}] {row['id']} {row['verdict']}: "
                f"{row['picked'] or ['NONE']}  (expect {row['expect'] or ['NONE']})",
                flush=True,
            )

    results.sort(key=lambda r: r["id"])
    out.write_text(json.dumps(results, indent=2) + "\n")

    by = {}
    for r in results:
        by.setdefault(r["kind"], []).append(r)

    def tally(rows, include_acceptable=True):
        p = sum(1 for r in rows if r["verdict"] == "pass")
        a = sum(1 for r in rows if r["verdict"] == "acceptable")
        f = sum(1 for r in rows if r["verdict"] == "fail")
        e = sum(1 for r in rows if r["verdict"] == "error")
        n = len(rows)
        first_ok = p + (a if include_acceptable else 0)
        return n, p, a, f, e, first_ok

    print("\n=== SUMMARY ===")
    for kind, rows in by.items():
        n, p, a, f, e, first_ok = tally(rows, include_acceptable=(kind != "positives"))
        # positives: intended first only; acceptable only for collisions/R10
        if kind == "positives":
            print(f"{kind}: {p}/{n} first-choice  fail={f} error={e}")
        else:
            print(f"{kind}: {first_ok}/{n} ok (pass={p} acceptable={a} fail={f} error={e})")

    fails = [r for r in results if r["verdict"] in ("fail", "error")]
    if fails:
        print("\n=== FAILURES ===")
        for r in fails:
            print(f"{r['id']} expect={r['expect'] or ['NONE']} got={r['picked'] or ['NONE']}")
            print(f"  {r['query']}")
    print(f"\nWrote {out}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
