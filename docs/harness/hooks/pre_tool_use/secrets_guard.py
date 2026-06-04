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
import pathlib
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

# ── Credential ops exemption ──────────────────────────────────────────────

VERIFY_ONLY_PATTERNS = [
    # These patterns access file metadata or structure — never content
    r'\bls\s+-[la]+\s+',
    r'\bwc\s+-[lc]\s+',
    r'\bmd5sum\s+',
    r'\bsha256sum\s+',
    r'\bsha1sum\s+',
    r'\bstat\s+',
    r'\bgrep\s+-[cq]+\s+[\'"^]',  # grep -c or grep -q with anchored pattern
    r'\bfile\s+',
]

CONTENT_EXPOSING_PATTERNS = [
    # These always block — no exemption possible
    r'\bcat\b',
    r'\bless\b',
    r'\bmore\b',
    r'\btail\b',
    r'\bhead\b',
    r'\becho\s+\$',
    r'\bprintenv\b',
    r'\benv\b.*\bgrep\b',
]


def load_credential_exemptions() -> dict:
    """Load session-scoped credential ops exemption file if present."""
    import json
    from datetime import datetime, timezone
    ops_file = pathlib.Path('.harnessable/credential_ops.json')
    if not ops_file.exists():
        return {}
    try:
        data = json.loads(ops_file.read_text())
        # Check expiry
        expires = data.get('expires_at')
        if expires:
            expiry_dt = datetime.fromisoformat(expires)
            if datetime.now(timezone.utc) > expiry_dt:
                return {}  # Expired — treat as absent
        return data
    except Exception:
        return {}


def is_verify_only_command(command: str) -> bool:
    """Return True if command only accesses file metadata, not content."""
    # Content-exposing always wins — check first
    for pattern in CONTENT_EXPOSING_PATTERNS:
        if re.search(pattern, command):
            return False
    for pattern in VERIFY_ONLY_PATTERNS:
        if re.search(pattern, command):
            return True
    return False


def check_credential_exemption(command: str, payload: dict) -> bool:
    """
    Return True if this credential access is governed and verify-only.
    Side effect: logs the exempted access to audit.
    """
    exemptions = load_credential_exemptions()
    if not exemptions:
        return False

    approved_paths = exemptions.get('approved_paths', [])
    if not approved_paths:
        return False

    # Check if command references an approved path
    path_match = any(
        pathlib.Path(p).name in command or p in command
        for p in approved_paths
    )
    if not path_match:
        return False

    # Verify-only pattern required — no exemption for content reads
    if not is_verify_only_command(command):
        return False

    # Log the exempted access
    log_credential_exemption(command, exemptions, payload)
    return True


def log_credential_exemption(
    command: str,
    exemptions: dict,
    payload: dict
) -> None:
    """Append credential exemption entry to audit log."""
    import json
    from datetime import datetime, timezone

    log_dir = pathlib.Path('.harnessable/logs')
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    log_file = log_dir / f'audit.{today}.jsonl'

    entry = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'session_id': payload.get('session_id', ''),
        'event': 'CredentialOpExemption',
        'tool': 'Bash',
        'command_truncated': command[:200],
        'credential_op_exemption': True,
        'mandate': exemptions.get('mandate', ''),
        'approved_paths': exemptions.get('approved_paths', []),
    }
    try:
        with log_file.open('a') as f:
            f.write(json.dumps(entry) + '\n')
    except OSError:
        pass  # Never block on log failure


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
        if check_credential_exemption(command, hook_data):
            sys.exit(0)  # Governed verify-only access — allow
        sys.stderr.write(
            f"[Harness: SecretsGuard] Blocked — {_reason(command)}\n"
            f"Command: {command!r}\n"
            f"Use .env.example for templates. Never read or transmit raw credentials.\n"
            f"If this command is intentional, have a human run it outside the agent session.\n"
        )
        sys.exit(2)


if __name__ == '__main__':
    main()
