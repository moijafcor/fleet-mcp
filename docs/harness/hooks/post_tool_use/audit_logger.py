#!/usr/bin/env python3
"""
PostToolUse hook — appends a structured entry to the project audit log.

Log location: .harnessable/logs/audit.YYYY-MM-DD.jsonl (one JSON object per line).
Previous days are compressed to .gz on next write. Large fields are capped.

Config: .harnessable/config.json  {"audit": {"max_field_bytes": 512, "retain_days": 90}}

Exit 0 always — a logging failure must never block the agent.
"""
import copy
import gzip
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict


_DEFAULT_MAX_FIELD_BYTES = 512
_DEFAULT_RETAIN_DAYS = 90


def _find_project_root(cwd: str) -> Path:
    for directory in [Path(cwd), *Path(cwd).parents]:
        if (directory / 'AGENTS.md').exists() or (directory / '.git').exists():
            return directory
    return Path(cwd)


def _load_audit_config(root: Path) -> Dict:
    try:
        with open(root / '.harnessable' / 'config.json') as f:
            return json.load(f).get('audit', {})
    except (OSError, json.JSONDecodeError):
        return {}


def _cap(value: str, max_bytes: int) -> str:
    if len(value) <= max_bytes:
        return value
    dropped = len(value) - max_bytes
    return value[:max_bytes] + f'... [truncated {dropped}B]'


def _apply_field_limits(entry: Dict, max_bytes: int) -> Dict:
    entry = copy.deepcopy(entry)
    response = entry.get('response', {})
    if not isinstance(response, dict):
        return entry

    stdout = response.get('stdout')
    if isinstance(stdout, str):
        response['stdout'] = _cap(stdout, max_bytes)

    file_obj = response.get('file', {})
    if isinstance(file_obj, dict):
        content = file_obj.get('content')
        if isinstance(content, str):
            file_obj['content'] = _cap(content, max_bytes)

    entry['response'] = response
    return entry


def _sanitise_input(tool_input: Dict, max_bytes: int) -> Dict:
    if not tool_input:
        return {}
    out = {}
    for k, v in tool_input.items():
        out[k] = _cap(v, max_bytes) if isinstance(v, str) else v
    return out


def _rotate_old_files(logs_dir: Path, today: str, retain_days: int) -> None:
    for old_path in sorted(logs_dir.glob('audit.*.jsonl')):
        date_part = old_path.stem.replace('audit.', '', 1)
        if date_part >= today:
            continue
        gz_path = Path(str(old_path) + '.gz')
        line_count = sum(1 for _ in open(old_path, encoding='utf-8'))
        raw_size = old_path.stat().st_size
        with open(old_path, 'rb') as f_in:
            with gzip.open(str(gz_path), 'wb', compresslevel=9) as f_out:
                shutil.copyfileobj(f_in, f_out)
        old_path.unlink()
        compressed_size = gz_path.stat().st_size
        ratio = (1 - compressed_size / raw_size) * 100 if raw_size > 0 else 0
        index_entry = {
            'ts_rotated': datetime.now(timezone.utc).isoformat(),
            'file': gz_path.name,
            'date': date_part,
            'events': line_count,
            'bytes_raw': raw_size,
            'bytes_compressed': compressed_size,
            'ratio': f'{ratio:.1f}%',
        }
        with open(logs_dir / 'index.jsonl', 'a', encoding='utf-8') as idx:
            idx.write(json.dumps(index_entry) + '\n')

    cutoff = datetime.now(timezone.utc).date() - timedelta(days=retain_days)
    for gz in logs_dir.glob('audit.*.jsonl.gz'):
        try:
            date_str = gz.stem.replace('audit.', '', 1).replace('.jsonl', '')
            file_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if file_date < cutoff:
                gz.unlink()
                purge_entry = {
                    'ts_purged': datetime.now(timezone.utc).isoformat(),
                    'file': gz.name,
                    'date': date_str,
                    'reason': f'older than {retain_days} days',
                }
                with open(logs_dir / 'index.jsonl', 'a', encoding='utf-8') as idx:
                    idx.write(json.dumps(purge_entry) + '\n')
        except ValueError:
            pass


def main() -> None:
    try:
        hook_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = hook_data.get('cwd', os.getcwd())
    root = None

    try:
        root = _find_project_root(cwd)
        cfg = _load_audit_config(root)
        max_bytes = int(cfg.get('max_field_bytes', _DEFAULT_MAX_FIELD_BYTES))
        retain_days = int(cfg.get('retain_days', _DEFAULT_RETAIN_DAYS))

        logs_dir = root / '.harnessable' / 'logs'
        logs_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_path = logs_dir / f'audit.{today}.jsonl'

        _rotate_old_files(logs_dir, today, retain_days)

        entry = {
            'ts': datetime.now(timezone.utc).isoformat(),
            'session_id': hook_data.get('session_id', ''),
            'event': hook_data.get('hook_event_name', 'PostToolUse'),
            'tool': hook_data.get('tool_name', ''),
            'input': _sanitise_input(hook_data.get('tool_input', {}), max_bytes),
            'response': hook_data.get('tool_response', {}),
        }
        entry = _apply_field_limits(entry, max_bytes)

        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    except Exception as exc:
        try:
            err_dir = (root / '.harnessable') if root else Path(cwd) / '.harnessable'
            err_dir.mkdir(parents=True, exist_ok=True)
            with open(err_dir / 'audit_logger.err', 'a', encoding='utf-8') as ef:
                ef.write(f'{datetime.now(timezone.utc).isoformat()} {exc}\n')
        except Exception:
            pass

    sys.exit(0)


if __name__ == '__main__':
    main()
