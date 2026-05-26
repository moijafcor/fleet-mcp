#!/usr/bin/env python3
"""
Stop hook — runs the project's completion gate before the agent can finish a turn.

Configure the gate by adding a ## Completion Gate section to AGENTS.md:

    ## Completion Gate
    - npx eslint src/
    - npx tsc --noEmit
    - npx jest --passWithNoTests

Each bullet is a shell command. All must exit 0 for the gate to pass.
If any command fails, this hook exits 2 and feeds the full output back to
the agent, which must fix the issue and complete again.

If AGENTS.md has no ## Completion Gate section, the hook is a no-op (exit 0).

Exit 0: gate passed (or no gate configured)
Exit 2: gate failed (stderr contains the failing command's output)
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


_GATE_HEADER = re.compile(r'^## Completion Gate\s*$', re.MULTILINE)
_NEXT_SECTION = re.compile(r'^##\s', re.MULTILINE)


def _parse_gate_commands(text: str) -> List[str]:
    match = _GATE_HEADER.search(text)
    if not match:
        return []

    start = match.end()
    nxt = _NEXT_SECTION.search(text, start)
    chunk = text[start : nxt.start() if nxt else len(text)]

    commands = []
    for line in chunk.splitlines():
        line = line.strip()
        if line.startswith('- '):
            cmd = line[2:].strip()
            if cmd:
                commands.append(cmd)
    return commands


def _find_agents_md(cwd: str) -> Optional[str]:
    for directory in [Path(cwd), *Path(cwd).parents]:
        candidate = directory / 'AGENTS.md'
        if candidate.exists():
            return candidate.read_text(encoding='utf-8')
    return None


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = hook_data.get('cwd', os.getcwd())
    agents_md = _find_agents_md(cwd)
    if not agents_md:
        sys.exit(0)

    commands = _parse_gate_commands(agents_md)
    if not commands:
        sys.exit(0)

    for cmd in commands:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            sys.stderr.write(
                f"[Harness: CompletionGate] FAILED — {cmd!r} exited {result.returncode}\n\n"
            )
            if result.stdout:
                sys.stderr.write(f"stdout:\n{result.stdout}\n")
            if result.stderr:
                sys.stderr.write(f"stderr:\n{result.stderr}\n")
            sys.stderr.write(
                "Fix the failure above before this turn can complete.\n"
                "Run the full gate suite after fixing, not just the failing command.\n"
            )
            sys.exit(2)


if __name__ == '__main__':
    main()
