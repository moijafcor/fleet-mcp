#!/usr/bin/env python3
"""
PreToolUse hook — blocks destructive git operations.

Catches operations that rewrite shared history, permanently discard
work, or delete branches and remote refs without a safety net.

Each check carries an explanation of exactly why it is dangerous and
what the safe alternative is, so the agent can propose a corrected
approach rather than simply failing.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import re
import sys
from typing import List, Optional, Tuple

Pattern = re.Pattern

_CHECKS: List[Tuple[Pattern, str]] = [
    (
        re.compile(r'\bgit\s+push\b.*\s(--force|-f)\b'),
        "Blocked 'git push --force' — rewrites shared remote history and will destroy "
        "commits pushed by others since your last fetch.\n"
        "Use 'git push --force-with-lease' if you understand the risk and have "
        "confirmed no one else has pushed, or have a human approve the force push.",
    ),
    (
        re.compile(r'\bgit\s+push\b[^|&;]*\s:\S+'),
        "Blocked remote ref deletion via 'git push origin :<ref>'.\n"
        "Deleting a remote branch or tag cannot be undone without a backup. "
        "Have a human run this directly after confirming no open PRs target it.",
    ),
    (
        re.compile(r'\bgit\s+reset\s+--hard\b'),
        "Blocked 'git reset --hard' — permanently discards all uncommitted changes "
        "in the working tree and index with no recovery path.\n"
        "Use 'git stash' to preserve work before resetting, or have a human run "
        "this directly after reviewing what will be lost.",
    ),
    (
        re.compile(r'\bgit\s+branch\s+.*-D\b'),
        "Blocked 'git branch -D' (force delete) — removes a local branch even if it "
        "has commits not present on any remote, which cannot be recovered.\n"
        "Use 'git branch -d' (safe delete) instead; it refuses to delete unmerged branches.",
    ),
    (
        re.compile(r'\bgit\s+clean\s+[^|&;]*-f'),
        "Blocked 'git clean -f' — permanently deletes all untracked files with no "
        "recovery path.\n"
        "Run 'git clean -n' first to preview what would be removed, then have a "
        "human approve the destructive run.",
    ),
    (
        re.compile(r'\bgit\s+rebase\b[^|&;]*(--onto|main|master|develop)'),
        "Blocked rebase onto a shared branch — rebasing commits that have already "
        "been pushed rewrites history for anyone who has pulled them.\n"
        "If this rebase is intentional, have a human run it after coordinating "
        "with the team.",
    ),
    (
        re.compile(r'\bgit\s+tag\s+-d\b'),
        "Blocked 'git tag -d' — deleting a tag that has been pushed to a remote "
        "leaves the remote tag in place but breaks local/remote consistency.\n"
        "Have a human delete both the local and remote tag together.",
    ),
]


def _blocked_reason(command: str) -> Optional[str]:
    for pattern, message in _CHECKS:
        if pattern.search(command):
            return message
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
        sys.stderr.write(f"[Harness: GitGuard] {reason}\n")
        sys.exit(2)


if __name__ == '__main__':
    main()
