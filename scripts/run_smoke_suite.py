"""Discover and run every committed Falcon Intelligence smoke check."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"


def discover_smoke_scripts() -> tuple[Path, ...]:
    """Return every smoke entry point under scripts in stable path order."""

    return tuple(sorted(SCRIPTS_ROOT.rglob("smoke_*.py")))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list discovered smoke scripts without running them")
    args = parser.parse_args(argv)

    scripts = discover_smoke_scripts()
    if not scripts:
        print("No smoke scripts were discovered under scripts/.", file=sys.stderr)
        return 1

    if args.list:
        for script in scripts:
            print(script.relative_to(REPO_ROOT).as_posix())
        return 0

    environment = os.environ.copy()
    source_path = str(REPO_ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (source_path, environment.get("PYTHONPATH", "")) if part
    )

    failures: list[Path] = []
    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        relative_path = script.relative_to(REPO_ROOT).as_posix()
        if result.returncode == 0:
            print(f"PASS {relative_path}")
            continue

        failures.append(script)
        print(f"FAIL {relative_path} (exit {result.returncode})", file=sys.stderr)
        if result.stdout:
            print(result.stdout.rstrip(), file=sys.stderr)
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)

    passed = len(scripts) - len(failures)
    print(f"Smoke suite: {passed}/{len(scripts)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
