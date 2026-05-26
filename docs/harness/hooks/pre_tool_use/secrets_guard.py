#!/usr/bin/env python3
"""
PreToolUse hook — belt-and-suspenders guard against secret exposure.

Blocks Bash commands that read, print, or transmit credentials regardless
of what the AGENTS.md Blocked list says. This is a hardcoded safety floor.

Exit 0: allow
Exit 2: block (stderr is fed back to the agent as the reason)
"""
import json
import os
import re
import sys


# File patterns whose contents must never be read or deleted by the agent.
_SENSITIVE_FILE_PATTERNS = [
    r'\.env(?:\.\w+)?(?:\s|$|["\'])',  # .env, .env.local, .env.production …
    r'\.pem\b',
    r'\.key\b',
    r'id_rsa',
    r'id_ed25519',
    r'credentials\.json',
    r'service[-_]account.*\.json',
    r'secrets\.(json|yaml|yml|toml)',
]

# Command substrings that suggest credential exfiltration regardless of target.
_EXFIL_PATTERNS = [
    r'\bcurl\b.*(-u|--user|--header.*Authorization)',
    r'\bwget\b.*--header.*Authorization',
    r'\becho\b.*\$[A-Z_]{6,}',          # echo $AWS_SECRET_ACCESS_KEY style
    r'\bprintenv\b',
    r'\benv\b\s*\|',                     # env | grep …
    r'\bexport\b.*PASSWORD',
    r'\bexport\b.*SECRET',
    r'\bexport\b.*TOKEN',
]

_SENSITIVE_RE = re.compile('|'.join(_SENSITIVE_FILE_PATTERNS), re.IGNORECASE)
_EXFIL_RE = re.compile('|'.join(_EXFIL_PATTERNS), re.IGNORECASE)


def _reason(command: str) -> str:
    if _SENSITIVE_RE.search(command):
        return 'Command targets a sensitive credential file.'
    return 'Command matches a credential exfiltration pattern.'


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

    if _SENSITIVE_RE.search(command) or _EXFIL_RE.search(command):
        sys.stderr.write(
            f"[Harness: SecretsGuard] Blocked — {_reason(command)}\n"
            f"Command: {command!r}\n"
            f"Use .env.example for templates. Never read or transmit raw credentials.\n"
            f"If this command is intentional, have a human run it outside the agent session.\n"
        )
        sys.exit(2)


if __name__ == '__main__':
    main()
