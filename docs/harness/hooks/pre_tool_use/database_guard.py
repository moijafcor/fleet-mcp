#!/usr/bin/env python3
"""
PreToolUse hook — blocks destructive database operations.

Catches DROP, TRUNCATE, and WHERE-less DELETE/UPDATE regardless of how
the SQL reaches the shell (psql -c, mysql -e, sqlite3, heredocs, etc.).

The WHERE-less check is intentional: DELETE FROM orders is catastrophic,
DELETE FROM orders WHERE id = 42 is routine. Pattern matching alone cannot
make this distinction — this script does.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import re
import sys


_DROP_RE = re.compile(
    r'\bDROP\s+(TABLE|DATABASE|SCHEMA|INDEX|VIEW|TRIGGER|FUNCTION|PROCEDURE|SEQUENCE)\b',
    re.IGNORECASE,
)
_TRUNCATE_RE = re.compile(r'\bTRUNCATE\b', re.IGNORECASE)
_DELETE_RE = re.compile(r'\bDELETE\s+FROM\s+\S+', re.IGNORECASE)
_UPDATE_RE = re.compile(r'\bUPDATE\s+\S+\s+SET\b', re.IGNORECASE)
_WHERE_RE = re.compile(r'\bWHERE\b', re.IGNORECASE)


def _blocked_reason(command: str):
    m = _DROP_RE.search(command)
    if m:
        return (
            f"Blocked destructive DDL: '{m.group(0)}'.\n"
            f"DROP operations are irreversible. Have a human run this directly "
            f"after verifying there is a current backup."
        )

    if _TRUNCATE_RE.search(command):
        return (
            "Blocked TRUNCATE — removes all rows instantly and cannot be rolled back "
            "outside an open transaction.\n"
            "Have a human run this directly after verifying there is a current backup."
        )

    if _DELETE_RE.search(command) and not _WHERE_RE.search(command):
        return (
            "Blocked DELETE without a WHERE clause — this would delete every row in the table.\n"
            "Add a WHERE clause to target specific rows, or have a human run the "
            "unrestricted DELETE directly."
        )

    if _UPDATE_RE.search(command) and not _WHERE_RE.search(command):
        return (
            "Blocked UPDATE without a WHERE clause — this would overwrite every row in the table.\n"
            "Add a WHERE clause to target specific rows, or have a human run the "
            "unrestricted UPDATE directly."
        )

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

    reason = _blocked_reason(command)
    if reason:
        sys.stderr.write(f"[Harness: DatabaseGuard] {reason}\n")
        sys.exit(2)


if __name__ == '__main__':
    main()
