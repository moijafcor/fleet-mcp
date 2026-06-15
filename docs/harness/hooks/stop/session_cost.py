#!/usr/bin/env python3
"""
Stop hook: session_cost.py

Fires at session end. Reads token usage from CC environment
and delegates to framework/tools/session_cost.py.

CC exposes token usage via the stop hook payload on stdin.
Expected payload fields (from CC stop hook spec):
  session_id, total_input_tokens, total_output_tokens,
  num_turns (tool calls approximation)

If payload is absent or incomplete, logs what is available
and exits cleanly — never blocks session exit.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def find_tool(start: Path, tool_name: str) -> Path | None:
    """Find framework/tools/{tool_name} from project root."""
    current = start
    for parent in [current] + list(current.parents):
        candidate = parent / "framework" / "tools" / tool_name
        if candidate.exists():
            return candidate
        candidate = parent / "docs" / "harness" / "tools" / tool_name
        if candidate.exists():
            return candidate
    return None


def _count_audit_tool_calls(session_id: str) -> int:
    """
    Count tool calls for this session from today's audit log as a proxy
    when payload has no data. Returns 0 if audit log is absent or unreadable.
    """
    from datetime import datetime, timezone

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = Path.cwd() / ".harnessable" / "logs" / f"audit.{today}.jsonl"

    if not log_path.exists():
        return 0
    try:
        count = 0
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if session_id == "unknown" or \
                       entry.get("session_id") == session_id:
                        count += 1
                except json.JSONDecodeError:
                    continue
        return count
    except Exception:
        return 0


def _extract_context_size(payload: dict) -> int:
    """
    Extract context window usage from stop payload.
    CC uses inconsistent field names across versions —
    try all known variants.
    Returns 0 if unavailable.
    """
    candidates = [
        "context_window_usage",
        "context_tokens_used",
        "total_context_tokens",
        "context_length",
        "input_token_count",
        "context_window",
    ]
    for field in candidates:
        val = payload.get(field, 0)
        if val and int(val) > 0:
            return int(val)

    # Check nested usage object
    usage = payload.get("usage", {})
    if isinstance(usage, dict):
        for field in candidates:
            val = usage.get(field, 0)
            if val and int(val) > 0:
                return int(val)

    return 0


def main():
    # Read stop hook payload from stdin
    payload = {}
    try:
        raw = sys.stdin.read()
        if raw.strip():
            payload = json.loads(raw)
    except Exception:
        pass  # Degrade gracefully — never block exit

    # Extract what CC provides
    session_id    = payload.get("session_id",
                      os.environ.get("CLAUDE_SESSION_ID", "unknown"))
    # CC stop payload does not include token counts.
    # Log 0 explicitly — session record is still useful
    # for role/mandate/model tracking even without tokens.
    input_tokens  = payload.get("total_input_tokens",  0)
    output_tokens = payload.get("total_output_tokens", 0)
    tool_calls    = payload.get("num_turns",            0)

    # Count tool calls from today's audit log as proxy
    # when payload provides no data
    if tool_calls == 0:
        tool_calls = _count_audit_tool_calls(session_id)

    context_size    = _extract_context_size(payload)
    context_warning = context_size > 150_000
    context_pct     = round(
        (context_size / 200_000) * 100, 1
    ) if context_size > 0 else 0
    # 200k = claude-sonnet-4-6 context window
    # adjust per model in AGENTS.md ## Models

    tokens_available = (input_tokens > 0 or output_tokens > 0)

    # Role and mandate from environment
    # Declare these in AGENTS.md skill wrapper or CC invocation
    role     = os.environ.get("HARNESS_ROLE",    "unknown")
    mandate  = os.environ.get("HARNESS_MANDATE", "unknown")
    model    = os.environ.get("HARNESS_MODEL",
               payload.get("model", "unknown"))

    # Find the logging tool
    tool = find_tool(Path.cwd(), "session_cost.py")
    if not tool:
        print("[session_cost] framework/tools/session_cost.py not found"
              " — skipping log.", file=sys.stderr)
        return 0

    # Delegate to the tool
    cmd = [
        sys.executable, str(tool),
        "--role",             role,
        "--mandate",          mandate,
        "--model",            model,
        "--input-tokens",     str(input_tokens),
        "--output-tokens",    str(output_tokens),
        "--tool-calls",       str(tool_calls),
        "--session-id",       session_id,
        "--context-size",     str(context_size),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.returncode != 0 and result.stderr:
            print(f"[session_cost] {result.stderr.strip()}",
                  file=sys.stderr)
    except Exception as e:
        print(f"[session_cost] Failed: {e}", file=sys.stderr)

    # Never block session exit
    return 0


if __name__ == "__main__":
    sys.exit(main())
