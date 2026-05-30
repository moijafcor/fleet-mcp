#!/usr/bin/env python3
"""
PreToolUse hook — blocks code edits until an EIR file exists.

Arms when .harnessable/emergency_gate is present. Blocks Write, Edit,
and MultiEdit until a file matching docs/mandates/emergency/*_eir.md
exists in the project root.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_GUARDED_TOOLS = {"Write", "Edit", "MultiEdit"}


def _find_project_root(cwd: str) -> Optional[Path]:
    for directory in [Path(cwd), *Path(cwd).parents]:
        if (directory / "AGENTS.md").exists() or (directory / ".harnessable").exists():
            return directory
    return None


def _gate_path(root: Path) -> Path:
    return root / ".harnessable" / "emergency_gate"


def _eir_exists(root: Path) -> bool:
    eir_dir = root / "docs" / "mandates" / "emergency"
    if not eir_dir.is_dir():
        return False
    return any(eir_dir.glob("*_eir.md"))


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

    if _eir_exists(root):
        sys.exit(0)

    target = hook_data.get("tool_input", {}).get("file_path", "<unknown>")
    print(
        f"[emergency_gate] BLOCKED\n"
        f"\n"
        f"Emergency gate armed but no EIR file exists yet.\n"
        f"Gate armed: {armed_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"Blocked:    {target}\n"
        f"\n"
        f"Create the EIR file FIRST:\n"
        f"  docs/mandates/emergency/{{YYYY-MM-DD}}_{{slug}}_eir.md\n"
        f"\n"
        f"Minimum EIR content:\n"
        f"  Title:    [EMERGENCY] {{what broke}}\n"
        f"  Symptom:  {{what the system is doing}}\n"
        f"  Approach: {{what you are going to try}}\n"
        f"\n"
        f"Code edits unblock automatically once the EIR file exists.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
