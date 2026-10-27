#!/usr/bin/env python3
"""Copy selected FDE packs into a local Agent Skills directory; no dependencies."""
import argparse
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
PACKS = sorted(p.name for p in ROOT.glob("fde-*") if (p / "skills").is_dir())


def files(directory):
    return {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def install(destination, packs):
    sources = {"_shared": ROOT / "fde-core/skills/_shared"}
    for pack in packs:
        for skill in sorted((ROOT / pack / "skills").glob("*/SKILL.md")):
            if skill.parent.name in sources:
                raise ValueError(f"Duplicate skill: {skill.parent.name}")
            sources[skill.parent.name] = skill.parent

    # Check every destination before writing; never merge into team-owned skills.
    pending = {}
    for name, source in sources.items():
        target = destination / name
        if target == source.resolve() or target.is_relative_to(source.resolve()):
            raise ValueError(f"Destination overlaps source: {name}")
        if target.is_symlink():
            raise ValueError(f"Existing symlink conflicts with {name}; nothing installed")
        if target.exists():
            if not target.is_dir() or files(target) != files(source):
                raise ValueError(f"Existing files conflict with {name}; nothing installed. "
                                 "Back up and remove only the intended FDE folder before updating.")
        else:
            pending[name] = source

    if pending:
        destination.mkdir(parents=True, exist_ok=True)
        # Finish copying resources before making any new skill discoverable.
        with tempfile.TemporaryDirectory(prefix=".fde-install-", dir=destination.parent) as stage:
            for name, source in pending.items():
                shutil.copytree(source, Path(stage) / name,
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            for name in pending:
                (Path(stage) / name).rename(destination / name)
    return len(sources) - 1, len(pending)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", type=Path, required=True,
                        help="Agent skill directory, e.g. /your/project/.agents/skills")
    parser.add_argument("--packs", nargs="+", choices=PACKS, default=["fde-core"])
    args = parser.parse_args()
    try:
        count, written = install(args.dest.expanduser().resolve(), sorted(set(args.packs)))
    except (OSError, ValueError) as exc:
        print(f"Install failed: {exc}", file=sys.stderr)
        return 1
    print(f"{count} skills available at {args.dest.expanduser().resolve()}; "
          f"{written} new folders (including shared resources when needed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
