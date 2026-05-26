#!/usr/bin/env python3
"""
Universal hook dispatcher for Harnessable.

Usage (from .claude/settings.json):
    python3 hooks/run.py pre_tool_use
    python3 hooks/run.py post_tool_use
    python3 hooks/run.py stop

Discovers every *.py file inside hooks/<event_subdir>/, sorts them
alphabetically, and runs each one in order, passing the original stdin
JSON payload to each script individually.

To add a new check, drop a .py script into the relevant subdirectory.
No settings.json edit required.

Exit 0  — all scripts passed (or no scripts found)
Exit 2  — a script exited 2; stderr from that script is forwarded and
          execution stops immediately (remaining scripts are not run)
"""
import json
import subprocess
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: run.py <event_subdir>\n")
        sys.exit(1)

    hooks_root = Path(sys.argv[0]).resolve().parent
    event_dir = hooks_root / sys.argv[1]

    # Read and validate stdin once; re-feed it to each child.
    try:
        raw = sys.stdin.buffer.read()
        json.loads(raw)
    except (json.JSONDecodeError, OSError, ValueError):
        sys.exit(0)

    if not event_dir.is_dir():
        sys.exit(0)

    scripts = sorted(event_dir.glob('*.py'))
    if not scripts:
        sys.exit(0)

    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(script)],
            input=raw,
            capture_output=True,
        )
        if result.stdout:
            sys.stdout.buffer.write(result.stdout)
        if result.stderr:
            sys.stderr.buffer.write(result.stderr)
        if result.returncode == 2:
            sys.exit(2)

    sys.exit(0)


if __name__ == '__main__':
    main()
