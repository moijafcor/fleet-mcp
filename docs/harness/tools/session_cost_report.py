#!/usr/bin/env python3
"""
session_cost_report.py — Summarise token consumption logs.

Reads .harnessable/logs/session-cost.*.jsonl and produces
a summary useful for Orchestrator budget decisions.

Usage:
  python3 framework/tools/session_cost_report.py
  python3 framework/tools/session_cost_report.py --month 2026-06
  python3 framework/tools/session_cost_report.py --role SRE
  python3 framework/tools/session_cost_report.py --json
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def find_logs(project_root: Path, month: str | None) -> list[Path]:
    log_dir = project_root / ".harnessable" / "logs"
    if not log_dir.exists():
        return []
    pattern = f"session-cost.{month}.jsonl" if month \
              else "session-cost.*.jsonl"
    return sorted(log_dir.glob(pattern))


def load_entries(log_files: list[Path],
                 role_filter: str | None) -> list[dict]:
    entries = []
    for path in log_files:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if role_filter and \
                       entry.get("role") != role_filter:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    return entries


def summarise(entries: list[dict]) -> dict:
    by_role    = defaultdict(lambda: {
                   "sessions": 0, "tokens": 0, "cost": 0.0})
    by_mandate = defaultdict(lambda: {
                   "sessions": 0, "tokens": 0, "cost": 0.0})
    by_model   = defaultdict(lambda: {
                   "sessions": 0, "tokens": 0, "cost": 0.0})
    totals     = {"sessions": 0, "tokens": 0, "cost": 0.0}
    by_context = defaultdict(lambda: {
                   "sessions": 0, "warned": 0, "avg_pct": 0.0})

    for e in entries:
        role     = e.get("role",    "unknown")
        mandate  = e.get("mandate", "unknown")
        model    = e.get("model",   "unknown")
        tokens   = e.get("total_tokens",      0)
        cost     = e.get("estimated_cost_usd", 0.0)

        for bucket in [by_role[role],
                       by_mandate[mandate],
                       by_model[model],
                       totals]:
            bucket["sessions"] += 1
            bucket["tokens"]   += tokens
            bucket["cost"]     += cost

        ctx_pct = e.get("context_pct", 0)
        warned  = e.get("context_warning", False)

        by_context["all"]["sessions"] += 1
        if warned:
            by_context["all"]["warned"] += 1
        by_context["all"]["avg_pct"] = (
            by_context["all"]["avg_pct"] *
            (by_context["all"]["sessions"] - 1) +
            ctx_pct
        ) / by_context["all"]["sessions"]

    return {
        "by_role":    dict(by_role),
        "by_mandate": dict(by_mandate),
        "by_model":   dict(by_model),
        "totals":     totals,
        "by_context": dict(by_context),
        "entry_count": len(entries),
    }


def print_report(summary: dict) -> None:
    t = summary["totals"]
    print(f"\n{'='*56}")
    print(f"  Token Consumption Report")
    print(f"{'='*56}")
    print(f"  Sessions: {t['sessions']}  |  "
          f"Tokens: {t['tokens']:,}  |  "
          f"Est. cost: ${t['cost']:.4f} USD")
    print(f"{'='*56}")

    print(f"\n  By role:")
    for role, d in sorted(summary["by_role"].items(),
                           key=lambda x: -x[1]["cost"]):
        print(f"    {role:<20} "
              f"{d['sessions']:>4} sessions  "
              f"{d['tokens']:>10,} tokens  "
              f"${d['cost']:.4f}")

    print(f"\n  By model:")
    for model, d in sorted(summary["by_model"].items(),
                            key=lambda x: -x[1]["cost"]):
        print(f"    {model:<30} "
              f"{d['sessions']:>4} sessions  "
              f"${d['cost']:.4f}")

    print(f"\n  Top mandates by cost:")
    top = sorted(summary["by_mandate"].items(),
                 key=lambda x: -x[1]["cost"])[:10]
    for mandate, d in top:
        label = mandate[-45:] if len(mandate) > 45 \
                else mandate
        print(f"    {label:<45}  ${d['cost']:.4f}")

    ctx = summary.get("by_context", {}).get("all", {})
    if ctx.get("sessions", 0) > 0:
        print(f"\n  Context size:")
        print(f"    Sessions with data:  {ctx['sessions']}")
        print(f"    >150k warnings:      {ctx['warned']}")
        print(f"    Avg context usage:   {ctx['avg_pct']:.1f}%")
        if ctx["warned"] > 0:
            pct = round(ctx['warned'] /
                        ctx['sessions'] * 100)
            print(f"    Warning rate:        {pct}%")
            print(f"    ⚠  High warning rate indicates")
            print(f"       sessions running too long.")
            print(f"       Consider /compact mid-session.")
    print()


def find_project_root() -> Path:
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / ".harnessable").exists():
            return parent
    return current


def main():
    parser = argparse.ArgumentParser(
        description="Summarise harnessable token consumption logs."
    )
    parser.add_argument("--month",  default=None,
                        help="Month to report e.g. 2026-06")
    parser.add_argument("--role",   default=None,
                        help="Filter by role name")
    parser.add_argument("--json",   action="store_true",
                        help="Output JSON instead of text")
    args = parser.parse_args()

    project_root = find_project_root()
    log_files    = find_logs(project_root, args.month)

    if not log_files:
        print("No session cost logs found.", file=sys.stderr)
        return 1

    entries = load_entries(log_files, args.role)
    if not entries:
        print("No matching entries.", file=sys.stderr)
        return 1

    summary = summarise(entries)

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_report(summary)

    return 0


if __name__ == "__main__":
    sys.exit(main())
