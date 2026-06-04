#!/usr/bin/env python3
"""
stop/credential_ops_cleanup.py

Removes .harnessable/credential_ops.json at session end.
Credential exemptions are session-scoped and must not persist.
Always exits 0.
"""

import json
import pathlib
import sys
from datetime import datetime, timezone


def main() -> int:
    ops_file = pathlib.Path('.harnessable/credential_ops.json')
    if not ops_file.exists():
        return 0
    try:
        # Log the cleanup
        log_dir = pathlib.Path('.harnessable/logs')
        log_dir.mkdir(parents=True, exist_ok=True)
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_file = log_dir / f'audit.{today}.jsonl'
        entry = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'event': 'CredentialOpsCleanup',
            'credential_op_exemption': False,
            'note': 'Session-scoped credential exemption removed at Stop',
        }
        with log_file.open('a') as f:
            f.write(json.dumps(entry) + '\n')
        ops_file.unlink()
        print('[credential_ops_cleanup] exemption file removed')
    except OSError as e:
        err = pathlib.Path('.harnessable/credential_ops_cleanup.err')
        err.parent.mkdir(parents=True, exist_ok=True)
        with err.open('a') as f:
            f.write(
                f'[{datetime.now(timezone.utc).isoformat()}] {e}\n'
            )
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
