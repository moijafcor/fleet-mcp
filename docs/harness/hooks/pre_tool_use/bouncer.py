#!/usr/bin/env python3
"""
PreToolUse hook — enforces the ## Blocked action list from AGENTS.md.

Reads the project's AGENTS.md, extracts the ## Blocked section, and
blocks any Bash command that matches a listed pattern.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional


_BLOCKED_HEADER = re.compile(r'^## Blocked\s*$', re.MULTILINE)
_NEXT_SECTION = re.compile(r'^##\s', re.MULTILINE)
_BACKTICK = re.compile(r'`([^`]+)`')


def _parse_blocked_patterns(text: str) -> List[str]:
    match = _BLOCKED_HEADER.search(text)
    if not match:
        return []

    start = match.end()
    nxt = _NEXT_SECTION.search(text, start)
    chunk = text[start : nxt.start() if nxt else len(text)]

    patterns = []
    for line in chunk.splitlines():
        line = line.strip()
        if not line.startswith('- '):
            continue
        item = line[2:].strip()
        # Prefer the contents of backticks if present, otherwise use the raw item.
        backtick_match = _BACKTICK.search(item)
        patterns.append(backtick_match.group(1) if backtick_match else item)
    return patterns


def _find_agents_md(cwd: str) -> Optional[str]:
    for directory in [Path(cwd), *Path(cwd).parents]:
        candidate = directory / 'AGENTS.md'
        if candidate.exists():
            return candidate.read_text(encoding='utf-8')
    return None


def _matching_pattern(command: str, patterns: List[str]) -> Optional[str]:
    command_lower = command.lower()
    for pattern in patterns:
        if pattern.lower() in command_lower:
            return pattern
    return None


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if hook_data.get('tool_name') != 'Bash':
        sys.exit(0)

    command = hook_data.get('tool_input', {}).get('command', '')
    if not command:
        sys.exit(0)

    cwd = hook_data.get('cwd', os.getcwd())
    agents_md = _find_agents_md(cwd)
    if not agents_md:
        sys.exit(0)

    patterns = _parse_blocked_patterns(agents_md)
    hit = _matching_pattern(command, patterns)

    if hit:
        sys.stderr.write(
            f"[Harness: Bouncer] Blocked — command matches '{hit}' "
            f"from AGENTS.md ## Blocked.\n"
            f"Command: {command!r}\n"
            f"To permit this action, the Architect must move it to ## Ask First "
            f"and a human must approve it, or remove it from ## Blocked.\n"
        )
        sys.exit(2)


if __name__ == '__main__':
    main()
