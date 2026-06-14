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
    session_id     = payload.get("session_id",
                       os.environ.get("CLAUDE_SESSION_ID", "unknown"))
    input_tokens   = payload.get("total_input_tokens",   0)
    output_tokens  = payload.get("total_output_tokens",  0)
    tool_calls     = payload.get("num_turns",            0)

    # Role and mandate from environment
    # Declare these in AGENTS.md skill wrapper or CC invocation
    role     = os.environ.get("HARNESS_ROLE",    "unknown")
    mandate  = os.environ.get("HARNESS_MANDATE", "unknown")
    model    = os.environ.get("HARNESS_MODEL",
               payload.get("model", "unknown"))

    # If no token data available, exit cleanly
    if input_tokens == 0 and output_tokens == 0:
        print("[session_cost] No token data in payload — skipping log.",
              file=sys.stderr)
        return 0

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
