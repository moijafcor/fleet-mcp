#!/usr/bin/env python3
"""
Stop hook — removes .harnessable/spike_gate at session end.

The gate does not persist into the next session. Cleanup is silent:
if the gate file does not exist, the hook exits 0 without output.

Exit 0: always (this hook never blocks)
"""
import json
import os
import sys
from pathlib import Path
from typing import Optional


def _find_project_root(cwd: str) -> Optional[Path]:
    for directory in [Path(cwd), *Path(cwd).parents]:
        if (directory / "AGENTS.md").exists() or (directory / ".harnessable").exists():
            return directory
    return None


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = hook_data.get("cwd", os.getcwd())
    root = _find_project_root(cwd)
    if root is None:
        sys.exit(0)

    gate = root / ".harnessable" / "spike_gate"
    try:
        gate.unlink(missing_ok=True)
    except OSError:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
