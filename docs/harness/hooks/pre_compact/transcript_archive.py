#!/usr/bin/env python3
"""
pre_compact/transcript_archive.py — PreCompact hook

Preserves the complete session transcript before every compaction event.
Disk space is cheap. Nothing is deleted automatically. Operators decide
purging policy.

Each compaction event produces:
  - A gzip-compressed transcript archive
  - One append-only index entry

Storage layout (relative to project root):
  .harness/
    transcripts/
      index.jsonl                                         ← NDJSON, one entry per event
      20260526T142301Z_a1b2c3d4_auto.transcript.jsonl.gz
      20260526T161045Z_a1b2c3d4_manual.transcript.jsonl.gz
      ...

Archive filename format:
  {YYYYMMDDTHHMMSSZ}_{session_id[:8]}_{trigger}.transcript.jsonl.gz

Index entry format (one JSON line per compaction):
  {
    "ts":              "2026-05-26T14:23:01Z",
    "session_id":      "a1b2c3d4...",
    "trigger":         "auto" | "manual",
    "file":            "20260526T142301Z_a1b2c3d4_auto.transcript.jsonl.gz",
    "lines":           1847,
    "bytes_raw":       284736,
    "bytes_compressed": 43291,
    "ratio":           "84.8%",
    "cwd":             "/home/user/project"
  }

Exit codes:
  0  — archive written successfully
  1  — non-fatal error (logged, compaction proceeds)

The hook must not block or fail compaction. All errors are caught and
written to .harness/transcript_archive.err before exiting 0.
"""

import gzip
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def log_error(harnessable_dir: Path, message: str) -> None:
    """Write errors to a dedicated error log rather than stderr."""
    err_log = harnessable_dir / "transcript_archive.err"
    ts = datetime.now(timezone.utc).isoformat()
    try:
        with err_log.open("a") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass  # Do not let error logging itself block compaction


def main() -> int:
    harnessable_dir = Path(".harness")
    transcripts_dir = harnessable_dir / "transcripts"

    # ── Parse stdin payload ───────────────────────────────────────────────────

    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        log_error(harnessable_dir, f"Invalid JSON payload: {e}")
        return 0  # Non-fatal: let compaction proceed

    session_id = payload.get("session_id", "unknown")
    trigger    = payload.get("trigger", "unknown")
    transcript_path = payload.get("transcript_path", "")

    # ── Resolve transcript ────────────────────────────────────────────────────

    if not transcript_path:
        log_error(harnessable_dir, "No transcript_path in payload — nothing to archive")
        return 0

    transcript_path = Path(transcript_path).expanduser()

    if not transcript_path.exists():
        log_error(harnessable_dir, f"Transcript not found: {transcript_path}")
        return 0

    # ── Prepare storage ───────────────────────────────────────────────────────

    try:
        transcripts_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log_error(harnessable_dir, f"Cannot create transcripts dir: {e}")
        return 0

    # ── Build archive filename ────────────────────────────────────────────────

    ts_now   = datetime.now(timezone.utc)
    ts_stamp = ts_now.strftime("%Y%m%dT%H%M%SZ")
    sid_short = session_id[:8] if len(session_id) >= 8 else session_id
    archive_name = f"{ts_stamp}_{sid_short}_{trigger}.transcript.jsonl.gz"
    archive_path = transcripts_dir / archive_name

    # ── Read and compress ─────────────────────────────────────────────────────

    try:
        raw_bytes = transcript_path.read_bytes()
    except OSError as e:
        log_error(harnessable_dir, f"Cannot read transcript: {e}")
        return 0

    line_count = raw_bytes.count(b"\n")
    bytes_raw  = len(raw_bytes)

    try:
        with gzip.open(archive_path, "wb", compresslevel=9) as gz:
            gz.write(raw_bytes)
        bytes_compressed = archive_path.stat().st_size
    except OSError as e:
        log_error(harnessable_dir, f"Cannot write archive {archive_path}: {e}")
        return 0

    ratio = (1 - bytes_compressed / bytes_raw) * 100 if bytes_raw > 0 else 0

    # ── Append index entry ────────────────────────────────────────────────────

    index_path = transcripts_dir / "index.jsonl"
    entry = {
        "ts":               ts_now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session_id":       session_id,
        "trigger":          trigger,
        "file":             archive_name,
        "lines":            line_count,
        "bytes_raw":        bytes_raw,
        "bytes_compressed": bytes_compressed,
        "ratio":            f"{ratio:.1f}%",
        "cwd":              str(Path.cwd()),
    }

    try:
        with index_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        log_error(harnessable_dir, f"Cannot write index: {e}")
        # Archive was written — this is recoverable. Continue.

    # ── Emit summary to stdout ────────────────────────────────────────────────

    print(
        f"[transcript_archive] {archive_name} "
        f"({bytes_raw:,} bytes → {bytes_compressed:,} bytes, "
        f"{ratio:.1f}% reduction, {line_count:,} lines)"
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Last-resort catch: never let this hook block compaction
        harnessable_dir = Path(".harness")
        log_error(harnessable_dir, f"Unhandled exception: {e}")
        sys.exit(0)
