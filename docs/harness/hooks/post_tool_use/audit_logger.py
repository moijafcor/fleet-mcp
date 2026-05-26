#!/usr/bin/env python3
"""
PostToolUse hook — appends a structured entry to the project audit log.

Log location: <project-root>/.harnessable/audit.log (one JSON object per line).
Add .harnessable/audit.log to .gitignore to exclude, or track it for compliance.

Exit 0 always — a logging failure must never block the agent.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


_MAX_FIELD_CHARS = 2000


def _find_project_root(cwd: str) -> Path:
    for directory in [Path(cwd), *Path(cwd).parents]:
        if (directory / 'AGENTS.md').exists() or (directory / '.git').exists():
            return directory
    return Path(cwd)


def _truncate(value: Any, label: str) -> Any:
    if not isinstance(value, str) or len(value) <= _MAX_FIELD_CHARS:
        return value
    dropped = len(value) - _MAX_FIELD_CHARS
    return value[:_MAX_FIELD_CHARS] + f' … [{dropped} chars truncated from {label}]'


def _sanitise_response(response: Dict) -> Dict:
    if not response:
        return {}
    out = {}
    for k, v in response.items():
        out[k] = _truncate(v, k)
    return out


def _sanitise_input(tool_input: Dict) -> Dict:
    """Truncate large inputs; never strip — the audit trail should be complete."""
    if not tool_input:
        return {}
    out = {}
    for k, v in tool_input.items():
        out[k] = _truncate(v, k)
    return out


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = hook_data.get('cwd', os.getcwd())

    entry = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'session_id': hook_data.get('session_id', ''),
        'event': hook_data.get('hook_event_name', 'PostToolUse'),
        'tool': hook_data.get('tool_name', ''),
        'input': _sanitise_input(hook_data.get('tool_input', {})),
        'response': _sanitise_response(hook_data.get('tool_response', {})),
    }

    try:
        root = _find_project_root(cwd)
        log_dir = root / '.harnessable'
        log_dir.mkdir(exist_ok=True)
        with open(log_dir / 'audit.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except OSError:
        # Never block the agent because logging failed.
        pass

    sys.exit(0)


if __name__ == '__main__':
    main()
