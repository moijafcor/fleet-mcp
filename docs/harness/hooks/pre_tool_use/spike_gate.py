#!/usr/bin/env python3
"""
PreToolUse hook — enforces branch-first discipline for Spike sessions.

Arms when .harnessable/spike_gate is present. Blocks Write, Edit, and
MultiEdit until the current git branch starts with 'spike/'. Once on a
spike/ branch the gate clears automatically — the branch IS the artifact.

Secondary check: if the branch slug after spike/ is in the trivial name
list or fewer than five characters, blocks with a naming violation message.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_GUARDED_TOOLS = {"Write", "Edit", "MultiEdit"}
_TRIVIAL_NAMES = {"fix", "test", "misc", "temp", "wip", "quick"}
_MIN_SLUG_LEN = 5


def _find_project_root(cwd: str) -> Optional[Path]:
    for directory in [Path(cwd), *Path(cwd).parents]:
        if (directory / "AGENTS.md").exists() or (directory / ".harnessable").exists():
            return directory
    return None


def _gate_path(root: Path) -> Path:
    return root / ".harnessable" / "spike_gate"


def _current_branch(cwd: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if hook_data.get("tool_name") not in _GUARDED_TOOLS:
        sys.exit(0)

    cwd = hook_data.get("cwd", os.getcwd())
    root = _find_project_root(cwd)
    if root is None:
        sys.exit(0)

    gate = _gate_path(root)
    if not gate.exists():
        sys.exit(0)

    try:
        armed_at = datetime.fromisoformat(gate.read_text().strip()).replace(
            tzinfo=timezone.utc
        )
    except (ValueError, OSError):
        armed_at = datetime.now(timezone.utc)

    branch = _current_branch(cwd)

    if branch is not None and branch.startswith("spike/"):
        slug = branch[len("spike/"):]
        if slug.lower() in _TRIVIAL_NAMES or len(slug) < _MIN_SLUG_LEN:
            target = hook_data.get("tool_input", {}).get("file_path", "<unknown>")
            print(
                f"[spike_gate] NAMING VIOLATION\n"
                f"\n"
                f"Branch '{branch}' does not satisfy the intent-statement rule.\n"
                f"Gate armed: {armed_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
                f"Blocked:    {target}\n"
                f"\n"
                f"The branch name must describe the work, not just label it:\n"
                f"  Bad:  spike/fix  spike/test  spike/misc  spike/temp  spike/wip\n"
                f"  Good: spike/add-reports-menu-item  spike/fix-null-pointer-login\n"
                f"\n"
                f"Rename the branch and continue:\n"
                f"  git branch -m spike/{{descriptive-name}}",
                file=sys.stderr,
            )
            sys.exit(2)
        sys.exit(0)

    target = hook_data.get("tool_input", {}).get("file_path", "<unknown>")
    print(
        f"[spike_gate] BLOCKED\n"
        f"\n"
        f"Spike gate armed but not on a spike/ branch.\n"
        f"Gate armed: {armed_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"Current branch: {branch or '<unknown>'}\n"
        f"Blocked:    {target}\n"
        f"\n"
        f"Create the spike branch FIRST:\n"
        f"  git checkout -b spike/{{descriptive-name}}\n"
        f"\n"
        f"The branch name is the intent statement — make it descriptive.\n"
        f"Code edits unblock automatically once on a spike/ branch.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
