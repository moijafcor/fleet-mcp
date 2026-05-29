#!/usr/bin/env python3
"""
One-time migration: splits .harnessable/audit.log into date-bucketed
.gz archives under .harnessable/logs/.

Run once after deploying the updated audit_logger.py:

    python3 .harnessable/migrate_audit_log.py

The original log is preserved at .harnessable/audit.log.pre-migration.
"""
import gzip
import io
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    harnessable = Path(__file__).resolve().parent
    log_path = harnessable / 'audit.log'
    logs_dir = harnessable / 'logs'
    index_path = logs_dir / 'index.jsonl'
    malformed_path = logs_dir / 'audit.migrated-malformed.jsonl'

    if not log_path.exists():
        print(f'ERROR: {log_path} not found. Nothing to migrate.')
        sys.exit(1)

    logs_dir.mkdir(parents=True, exist_ok=True)

    raw_size = log_path.stat().st_size

    by_date: defaultdict[str, list[str]] = defaultdict(list)
    malformed: list[str] = []
    total_lines = 0

    with open(log_path, encoding='utf-8', errors='replace') as f:
        for raw_line in f:
            raw_line = raw_line.rstrip('\n')
            if not raw_line.strip():
                continue
            total_lines += 1
            try:
                entry = json.loads(raw_line)
                ts = entry.get('ts', '')
                date_part = ts[:10] if len(ts) >= 10 else 'unknown'
                by_date[date_part].append(raw_line)
            except json.JSONDecodeError:
                malformed.append(raw_line)

    dates_found = sorted(by_date.keys())
    archives_created = 0
    total_compressed = 0

    for date_part in dates_found:
        lines = by_date[date_part]
        gz_path = logs_dir / f'audit.{date_part}.jsonl.gz'

        existing_lines: list[str] = []
        if gz_path.exists():
            with gzip.open(gz_path, 'rt', encoding='utf-8') as ef:
                for line in ef:
                    stripped = line.rstrip('\n')
                    if stripped.strip():
                        existing_lines.append(stripped)

        all_lines = existing_lines + lines
        content = '\n'.join(all_lines) + '\n'
        content_bytes = content.encode('utf-8')

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=9) as gz_f:
            gz_f.write(content_bytes)
        with open(gz_path, 'wb') as out_f:
            out_f.write(buf.getvalue())

        compressed_size = gz_path.stat().st_size
        total_compressed += compressed_size
        archives_created += 1

        raw_len = len(content_bytes)
        ratio = (1 - compressed_size / raw_len) * 100 if raw_len > 0 else 0
        index_entry = {
            'ts_rotated': datetime.now(timezone.utc).isoformat(),
            'file': gz_path.name,
            'date': date_part,
            'events': len(all_lines),
            'bytes_raw': raw_len,
            'bytes_compressed': compressed_size,
            'ratio': f'{ratio:.1f}%',
            'source': 'migration',
        }
        with open(index_path, 'a', encoding='utf-8') as idx:
            idx.write(json.dumps(index_entry) + '\n')

    if malformed:
        with open(malformed_path, 'a', encoding='utf-8') as mf:
            for line in malformed:
                mf.write(line + '\n')

    pre_migration = harnessable / 'audit.log.pre-migration'
    shutil.move(str(log_path), str(pre_migration))

    reduction = (1 - total_compressed / raw_size) * 100 if raw_size > 0 else 0
    print('Migration complete')
    print(f'Lines processed:   {total_lines:,}')
    if malformed:
        print(f'Malformed lines:   {len(malformed):,}  → {malformed_path}')
    print(f'Dates found:       {", ".join(dates_found)}')
    print(f'Archives created:  {archives_created}')
    print(f'Bytes before:      {raw_size:,} ({raw_size / 1024 / 1024:.1f}MB)')
    print(f'Bytes after (gz):  {total_compressed:,} ({total_compressed / 1024:.0f}KB)')
    print(f'Reduction:         {reduction:.1f}%')
    print(f'Original at:       {pre_migration}')


if __name__ == '__main__':
    main()
