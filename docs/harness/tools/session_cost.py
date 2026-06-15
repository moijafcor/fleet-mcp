#!/usr/bin/env python3
"""
session_cost.py — Token consumption logger for harnessable.

Reads token usage from CC session environment, cross-references
against the Models Manifest, and appends a structured entry to
.harnessable/logs/session-cost.YYYY-MM.jsonl

Usage:
  Called by hooks/stop/session_cost.py at session end.
  Can also be called directly for manual logging.

  python3 framework/tools/session_cost.py \
    --role SRE \
    --mandate docs/mandates/infra/staging_vps.md \
    --model claude-sonnet-4-6 \
    --input-tokens 42180 \
    --output-tokens 8934 \
    --tool-calls 47 \
    --duration-seconds 1842
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


# Cost per 1k tokens — fallback if not in Models Manifest
# Update when Anthropic pricing changes
FALLBACK_COSTS = {
    "claude-opus-4-6":     {"input": 0.015, "output": 0.075},
    "claude-sonnet-4-6":   {"input": 0.003, "output": 0.015},
    "claude-haiku-4-5":    {"input": 0.00025, "output": 0.00125},
}


def find_project_root() -> Path:
    """Walk up from cwd to find .harnessable directory."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".harnessable").exists():
            return parent
    # Fallback: use cwd
    return current


def load_models_manifest(project_root: Path) -> dict:
    """Load docs/harness/models.yaml if present."""
    manifest_path = project_root / "docs" / "harness" / "models.yaml"
    if not manifest_path.exists():
        return {}
    try:
        import yaml
        with open(manifest_path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def get_cost_per_1k(model: str, manifest: dict) -> dict:
    """
    Look up cost per 1k tokens from Models Manifest.
    Falls back to FALLBACK_COSTS if not declared.
    """
    roles = manifest.get("roles", {})
    for role_data in roles.values():
        model_id = role_data.get("model_id", "")
        if model_id == model:
            cost = role_data.get("cost_per_1k_tokens", {})
            if cost:
                return cost
    # Try fallback
    return FALLBACK_COSTS.get(model, {"input": 0.0, "output": 0.0})


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    cost_per_1k: dict
) -> float:
    """Estimate USD cost from token counts."""
    input_cost  = (input_tokens  / 1000) * cost_per_1k.get("input",  0.0)
    output_cost = (output_tokens / 1000) * cost_per_1k.get("output", 0.0)
    return round(input_cost + output_cost, 6)


def get_log_path(project_root: Path) -> Path:
    """Return monthly log file path, creating directory if needed."""
    log_dir = project_root / ".harnessable" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return log_dir / f"session-cost.{month}.jsonl"


def write_log_entry(log_path: Path, entry: dict) -> None:
    """Append a JSONL entry to the log file."""
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def build_entry(args, cost_per_1k: dict) -> dict:
    """Build the structured log entry."""
    estimated_cost = estimate_cost(
        args.input_tokens,
        args.output_tokens,
        cost_per_1k
    )
    return {
        "ts":                datetime.now(timezone.utc).isoformat(),
        "session_id":        args.session_id or os.environ.get(
                               "CLAUDE_SESSION_ID", "unknown"),
        "role":              args.role,
        "mandate":           args.mandate or "unknown",
        "model":             args.model,
        "input_tokens":      args.input_tokens,
        "output_tokens":     args.output_tokens,
        "total_tokens":      args.input_tokens + args.output_tokens,
        "tool_calls":        args.tool_calls,
        "duration_seconds":  args.duration_seconds,
        "estimated_cost_usd": estimated_cost,
        "cost_per_1k":       cost_per_1k,
        "tokens_available":  (args.input_tokens > 0 or
                              args.output_tokens > 0),
        "context_size":      args.context_size,
        "context_pct":       round(
                               (args.context_size / 200_000) * 100, 1
                             ) if args.context_size > 0 else 0,
        "context_warning":   args.context_size > 150_000,
        # context_warning: True = approaching limit
        # correlates with increased cost and
        # THROTTLING / JAIL_TIME risk
    }


def main():
    parser = argparse.ArgumentParser(
        description="Log token consumption for a harnessable session."
    )
    parser.add_argument("--role",             required=True)
    parser.add_argument("--mandate",          default=None)
    parser.add_argument("--model",            required=True)
    parser.add_argument("--input-tokens",     type=int, default=0)
    parser.add_argument("--output-tokens",    type=int, default=0)
    parser.add_argument("--tool-calls",       type=int, default=0)
    parser.add_argument("--duration-seconds", type=int, default=0)
    parser.add_argument("--session-id",       default=None)
    parser.add_argument(
        "--context-size",
        type=int,
        default=0,
        help="Context window tokens used at session end"
    )
    args = parser.parse_args()

    project_root = find_project_root()
    manifest     = load_models_manifest(project_root)
    cost_per_1k  = get_cost_per_1k(args.model, manifest)
    entry        = build_entry(args, cost_per_1k)
    log_path     = get_log_path(project_root)

    write_log_entry(log_path, entry)

    context_str = (
        f", context: {entry['context_size']:,} tokens "
        f"({entry['context_pct']}%)"
        f"{'  ⚠ >150k' if entry['context_warning'] else ''}"
    ) if entry['context_size'] > 0 else ""

    print(
        f"Session logged: {entry['total_tokens']} tokens "
        f"(~${entry['estimated_cost_usd']:.4f} USD)"
        f"{context_str}"
        f" → {log_path.name}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
