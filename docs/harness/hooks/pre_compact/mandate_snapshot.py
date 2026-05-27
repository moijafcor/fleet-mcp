#!/usr/bin/env python3
"""
pre_compact/mandate_snapshot.py — PreCompact hook

Captures operational state before compaction so the next context window
has a structured handover rather than relying on the compaction summary.

Runs after transcript_archive.py. Both hooks fire on PreCompact.

Produces:
  .harness/compaction-handover.md  — overwritten on each compaction;
                                         latest state only. Historical
                                         state is in the transcript archives.

Handover document sections:
  - Compaction event metadata (ts, trigger, session_id)
  - Active mandate (last DMT/DIP reference found in transcript)
  - Open discoveries (ONTOLOGY_GAP, BLOCKER, DEVIATION not yet resolved)
  - Git state per codebase (configurable via .harness/config.json)
  - Last known board status
  - Unresolved checklist items from TIR sign-off

Configuration (.harness/config.json, optional):
  {
    "codebase_paths": [
      ".",
      "../app.adswire.io",
      "../api.adswire.io",
      "../console.adswire.io"
    ]
  }

If no config exists, only the current working directory is checked for git.

Exit codes:
  0  — always. Snapshot failure must not block compaction.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    "codebase_paths": ["."]
}

DISCOVERY_CLASSES = [
    "ONTOLOGY_GAP",
    "BLOCKER",
    "DEVIATION",
    "HARNESS_IMPROVEMENT",
]

# Patterns that suggest an open/unresolved discovery
OPEN_DISCOVERY_PATTERNS = [
    "filed:",
    "discovery:",
    "[ ]",   # unchecked markdown checkbox
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def log_error(harnessable_dir: Path, message: str) -> None:
    err_log = harnessable_dir / "mandate_snapshot.err"
    ts = datetime.now(timezone.utc).isoformat()
    try:
        with err_log.open("a") as f:
            f.write(f"[{ts}] {message}\n")
    except Exception:
        pass


def load_config(harnessable_dir: Path) -> dict:
    config_path = harnessable_dir / "config.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            pass
    return DEFAULT_CONFIG


def git_state(path: str) -> dict:
    """Run git status and log in a given directory. Returns structured result."""
    p = Path(path).expanduser().resolve()
    result = {"path": str(p), "is_git_repo": False, "status": "", "log": "", "error": ""}

    if not p.exists():
        result["error"] = "path does not exist"
        return result

    try:
        # Check if git repo
        check = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=p, capture_output=True, text=True, timeout=5
        )
        if check.returncode != 0:
            result["error"] = "not a git repository"
            return result

        result["is_git_repo"] = True

        # git status --short
        status = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=p, capture_output=True, text=True, timeout=5
        )
        result["status"] = status.stdout.strip()

        # git log --oneline -5
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=p, capture_output=True, text=True, timeout=5
        )
        result["log"] = log.stdout.strip()

    except subprocess.TimeoutExpired:
        result["error"] = "git command timed out"
    except FileNotFoundError:
        result["error"] = "git not found in PATH"
    except Exception as e:
        result["error"] = str(e)

    return result


def extract_transcript_signals(transcript_path: Path) -> dict:
    """
    Extract operational signals from the transcript JSONL.
    Scans for: mandate references, discovery classes, board statuses,
    unchecked TIR checklist items.
    """
    signals = {
        "last_board_status": None,
        "open_discoveries":  [],
        "mandate_refs":      [],
        "unchecked_items":   [],
        "last_role":         None,
        "line_count":        0,
    }

    if not transcript_path or not Path(transcript_path).exists():
        return signals

    board_statuses = [
        "MANDATED", "IN_RECON", "PLANNED", "IN_PROGRESS",
        "IN_REVIEW", "BLOCKED", "NEEDS_REVISION", "VERIFIED", "DONE"
    ]

    roles = ["Architect", "Engineer", "Coder", "QA"]

    try:
        lines = Path(transcript_path).expanduser().read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()

        signals["line_count"] = len(lines)

        for raw_line in lines:
            try:
                entry = json.loads(raw_line)
            except json.JSONDecodeError:
                continue

            # Extract text content from the entry
            content = ""
            if isinstance(entry, dict):
                # Handle various transcript formats
                for key in ("content", "text", "message", "summary"):
                    val = entry.get(key)
                    if isinstance(val, str):
                        content += val + " "
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                content += item.get("text", "") + " "

            if not content:
                continue

            # Board status — last one wins
            for status in board_statuses:
                if status in content:
                    signals["last_board_status"] = status

            # Role — last one wins
            for role in roles:
                if f"Act as {role}" in content or f"acting as {role}" in content.lower():
                    signals["last_role"] = role

            # Open discovery classes
            for dc in DISCOVERY_CLASSES:
                if dc in content and dc not in signals["open_discoveries"]:
                    signals["open_discoveries"].append(dc)

            # Mandate file references (DIP paths)
            if "implementation_plan.md" in content or "docs/mandates" in content:
                import re
                refs = re.findall(r'docs/mandates/[^\s\)\"\']+', content)
                for ref in refs:
                    if ref not in signals["mandate_refs"]:
                        signals["mandate_refs"].append(ref)

            # Unchecked TIR checklist items
            import re
            unchecked = re.findall(r'- \[ \] (.+)', content)
            signals["unchecked_items"].extend(unchecked)

    except Exception as e:
        signals["error"] = str(e)

    # Deduplicate unchecked items, keep last 10
    seen = set()
    deduped = []
    for item in reversed(signals["unchecked_items"]):
        if item not in seen:
            seen.add(item)
            deduped.append(item)
        if len(deduped) >= 10:
            break
    signals["unchecked_items"] = list(reversed(deduped))

    # Keep last 5 mandate refs
    signals["mandate_refs"] = signals["mandate_refs"][-5:]

    return signals


def format_git_block(git_results: list) -> str:
    lines = []
    for r in git_results:
        lines.append(f"### `{r['path']}`")
        if r.get("error"):
            lines.append(f"_Error: {r['error']}_\n")
            continue
        if not r["is_git_repo"]:
            lines.append("_Not a git repository_\n")
            continue

        status = r["status"] or "_(clean)_"
        log    = r["log"]    or "_(no commits)_"

        lines.append("**Status:**")
        lines.append("```")
        lines.append(status)
        lines.append("```")
        lines.append("**Recent commits:**")
        lines.append("```")
        lines.append(log)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    harnessable_dir = Path(".harness")

    try:
        payload = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        log_error(harnessable_dir, f"Invalid JSON payload: {e}")
        return 0

    session_id      = payload.get("session_id", "unknown")
    trigger         = payload.get("trigger", "unknown")
    transcript_path = payload.get("transcript_path", "")
    ts_now          = datetime.now(timezone.utc)
    ts_iso          = ts_now.strftime("%Y-%m-%dT%H:%M:%SZ")
    ts_human        = ts_now.strftime("%Y-%m-%d %H:%M UTC")

    try:
        harnessable_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        log_error(harnessable_dir, f"Cannot create .harness dir: {e}")
        return 0

    config = load_config(harnessable_dir)

    # ── Extract transcript signals ────────────────────────────────────────────

    signals = extract_transcript_signals(
        Path(transcript_path).expanduser() if transcript_path else None
    )

    # ── Git state per configured codebase ────────────────────────────────────

    codebase_paths = config.get("codebase_paths", ["."])
    git_results = [git_state(p) for p in codebase_paths]

    # ── Build handover document ───────────────────────────────────────────────

    doc_lines = [
        "# Compaction Handover",
        "",
        "> This document was generated automatically by `pre_compact/mandate_snapshot.py`.",
        "> It reflects state at the moment of compaction. Load it at session start",
        "> to restore operational context.",
        "> Full transcript archived in `.harness/transcripts/`.",
        "",
        "---",
        "",
        "## Compaction Event",
        "",
        f"| Field | Value |",
        f"|---|---|",
        f"| Timestamp | `{ts_iso}` |",
        f"| Trigger | `{trigger}` |",
        f"| Session ID | `{session_id}` |",
        f"| Transcript lines | `{signals['line_count']:,}` |",
        "",
    ]

    # Board status
    doc_lines += [
        "## Last Known Board Status",
        "",
        f"`{signals['last_board_status'] or 'unknown — not detected in transcript'}`",
        "",
    ]

    # Active role
    if signals["last_role"]:
        doc_lines += [
            "## Last Active Role",
            "",
            f"`{signals['last_role']}`",
            "",
        ]

    # Mandate references
    if signals["mandate_refs"]:
        doc_lines += [
            "## Mandate References (recent)",
            "",
        ]
        for ref in signals["mandate_refs"]:
            doc_lines.append(f"- `{ref}`")
        doc_lines.append("")
    else:
        doc_lines += [
            "## Mandate References",
            "",
            "_None detected in transcript._",
            "",
        ]

    # Open discoveries
    doc_lines += [
        "## Open Discovery Classes Detected",
        "",
    ]
    if signals["open_discoveries"]:
        doc_lines.append(
            "> These classes appeared in the transcript. Verify which are still open."
        )
        doc_lines.append("")
        for dc in signals["open_discoveries"]:
            doc_lines.append(f"- `{dc}`")
    else:
        doc_lines.append("_None detected._")
    doc_lines.append("")

    # Unchecked TIR items
    if signals["unchecked_items"]:
        doc_lines += [
            "## Unchecked Sign-off Items (TIR)",
            "",
            "> These `- [ ]` items appeared in the transcript and may be unresolved.",
            "",
        ]
        for item in signals["unchecked_items"]:
            doc_lines.append(f"- [ ] {item}")
        doc_lines.append("")

    # Git state
    doc_lines += [
        "## Git State at Compaction",
        "",
        "> A dirty working tree at compaction means uncommitted work.",
        "> Verify before resuming.",
        "",
        format_git_block(git_results),
    ]

    # Resume instructions
    doc_lines += [
        "---",
        "",
        "## Resume Instructions",
        "",
        "At the start of the next session, load this document and:",
        "",
        "1. Confirm the board status above is current — check the project tracker.",
        "2. For any open `ONTOLOGY_GAP` or `BLOCKER` discoveries, verify they",
        "   were resolved before compaction or resolve them now.",
        "3. For any dirty git repos above, run `git status` to confirm current state.",
        "4. For any unchecked TIR sign-off items, confirm their actual status.",
        "5. Resume from the last active role unless the Architect has redirected.",
        "",
        f"_Generated: {ts_human} | Trigger: {trigger} | Session: {session_id[:8]}..._",
    ]

    # ── Write document ────────────────────────────────────────────────────────

    handover_path = harnessable_dir / "compaction-handover.md"
    try:
        handover_path.write_text("\n".join(doc_lines), encoding="utf-8")
    except OSError as e:
        log_error(harnessable_dir, f"Cannot write handover doc: {e}")
        return 0

    print(
        f"[mandate_snapshot] handover written → {handover_path} "
        f"(trigger={trigger}, status={signals['last_board_status'] or 'unknown'}, "
        f"discoveries={signals['open_discoveries'] or 'none'})"
    )

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        harnessable_dir = Path(".harness")
        log_error(harnessable_dir, f"Unhandled exception: {e}")
        sys.exit(0)
