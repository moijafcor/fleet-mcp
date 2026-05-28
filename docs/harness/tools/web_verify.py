#!/usr/bin/env python3
"""
tools/web_verify.py — live external fact verification helper

Gives Engineer agents a single entry point for verifying external facts
against live sources rather than training knowledge.

Usage:
  # Fetch a URL and return readable text (HTML stripped)
  python3 docs/harness/tools/web_verify.py fetch <url> [--chars 3000]

  # Search for current information (requires: pip install duckduckgo-search)
  python3 docs/harness/tools/web_verify.py search "<query>" [--results 5]

  # Resolve installed version and substitute into URL template
  python3 docs/harness/tools/web_verify.py resolve <detector> "<url_template>"
    detectors: laravel, node, python, composer-package:<name>, npm-package:<name>
    template:  use {version} or {major} as placeholders

Examples:
  python3 docs/harness/tools/web_verify.py fetch \
    "https://laravel.com/docs/13.x/boost"

  python3 docs/harness/tools/web_verify.py search \
    "laravel boost 13.x compatibility" --results 3

  python3 docs/harness/tools/web_verify.py resolve laravel \
    "https://laravel.com/docs/{major}.x/boost"

  python3 docs/harness/tools/web_verify.py resolve composer-package:spatie/laravel-permission \
    "https://spatie.be/docs/laravel-permission/v{major}/introduction"

Exit codes:
  0 — success, output on stdout
  1 — fetch/search failed, reason on stderr
"""

import argparse
import re
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path


# ── Version detectors ─────────────────────────────────────────────────────────

def detect_laravel() -> str:
    try:
        out = subprocess.check_output(
            ["php", "artisan", "--version"], stderr=subprocess.DEVNULL, text=True
        )
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
        if m:
            return m.group(0), m.group(1)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    raise RuntimeError("Could not detect Laravel version (php artisan --version failed)")


def detect_node() -> tuple:
    try:
        out = subprocess.check_output(
            ["node", "--version"], stderr=subprocess.DEVNULL, text=True
        ).strip().lstrip("v")
        parts = out.split(".")
        return out, parts[0]
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    raise RuntimeError("Could not detect Node.js version")


def detect_python() -> tuple:
    v = sys.version_info
    full = f"{v.major}.{v.minor}.{v.micro}"
    return full, str(v.major)


def detect_composer_package(package_name: str) -> tuple:
    """Read installed version from composer.lock"""
    lock = Path("composer.lock")
    if not lock.exists():
        raise RuntimeError("composer.lock not found")
    import json
    data = json.loads(lock.read_text())
    for pkg in data.get("packages", []) + data.get("packages-dev", []):
        if pkg.get("name", "").lower() == package_name.lower():
            v = pkg.get("version", "").lstrip("v")
            parts = v.split(".")
            return v, parts[0] if parts else v
    raise RuntimeError(f"Package {package_name!r} not found in composer.lock")


def detect_npm_package(package_name: str) -> tuple:
    """Read installed version from package-lock.json or node_modules"""
    lock = Path("package-lock.json")
    if lock.exists():
        import json
        data = json.loads(lock.read_text())
        deps = data.get("dependencies", {})
        if package_name in deps:
            v = deps[package_name].get("version", "").lstrip("v")
            parts = v.split(".")
            return v, parts[0] if parts else v
    raise RuntimeError(f"Package {package_name!r} not found in package-lock.json")


def resolve_version(detector: str) -> tuple:
    """Returns (full_version, major_version)"""
    if detector == "laravel":
        return detect_laravel()
    elif detector == "node":
        return detect_node()
    elif detector == "python":
        return detect_python()
    elif detector.startswith("composer-package:"):
        return detect_composer_package(detector.split(":", 1)[1])
    elif detector.startswith("npm-package:"):
        return detect_npm_package(detector.split(":", 1)[1])
    else:
        raise RuntimeError(f"Unknown detector: {detector!r}. "
                           f"Supported: laravel, node, python, "
                           f"composer-package:<name>, npm-package:<name>")


# ── Fetch ─────────────────────────────────────────────────────────────────────

def fetch_url(url: str, max_chars: int = 3000) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; harnessable-web-verify/1.0; "
            "+https://github.com/moijafcor/harnessable)"
        )
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content_type = resp.headers.get("Content-Type", "")
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {url}")
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error: {e.reason}")

    if "html" in content_type.lower():
        raw = strip_html(raw)

    truncated = raw[:max_chars]
    if len(raw) > max_chars:
        truncated += f"\n\n[... {len(raw) - max_chars:,} chars truncated. Full content at: {url}]"
    return truncated


def strip_html(html: str) -> str:
    """Strip HTML tags and normalise whitespace."""
    # Remove script and style blocks
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    # Remove tags
    html = re.sub(r"<[^>]+>", " ", html)
    # Decode common entities
    for entity, char in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                          ("&quot;", '"'), ("&#39;", "'"), ("&nbsp;", " ")]:
        html = html.replace(entity, char)
    # Normalise whitespace
    return re.sub(r"\s{3,}", "\n\n", html).strip()


# ── Search ────────────────────────────────────────────────────────────────────

def search_web(query: str, max_results: int = 5) -> str:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return (
            "duckduckgo-search is not installed.\n"
            "Install with: pip install duckduckgo-search\n\n"
            "Alternative — use fetch with a known URL:\n"
            f"  python3 docs/harness/tools/web_verify.py fetch <url>"
        )

    results = list(DDGS().text(query, max_results=max_results))
    if not results:
        return f"No results for: {query!r}"

    lines = [f"Search: {query!r}\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r.get('title', '(no title)')}")
        lines.append(f"   {r.get('href', '')}")
        snippet = r.get("body", "")[:200]
        if snippet:
            lines.append(f"   {snippet}")
        lines.append("")

    lines.append(
        "Verify by fetching the primary source:\n"
        "  python3 docs/harness/tools/web_verify.py fetch <url>"
    )
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Live external fact verification helper for harnessable agents."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    fetch_p = sub.add_parser("fetch", help="Fetch a URL and return readable text")
    fetch_p.add_argument("url", help="URL to fetch")
    fetch_p.add_argument("--chars", type=int, default=3000,
                         help="Max characters to return (default: 3000)")

    search_p = sub.add_parser("search", help="Search for current information")
    search_p.add_argument("query", help="Search query")
    search_p.add_argument("--results", type=int, default=5,
                          help="Max results to return (default: 5)")

    resolve_p = sub.add_parser(
        "resolve",
        help="Resolve installed version and substitute into URL template"
    )
    resolve_p.add_argument(
        "detector",
        help="Version detector: laravel, node, python, "
             "composer-package:<name>, npm-package:<name>"
    )
    resolve_p.add_argument(
        "url_template",
        help="URL template with {version} or {major} placeholders"
    )
    resolve_p.add_argument("--chars", type=int, default=3000)
    resolve_p.add_argument(
        "--dry-run", action="store_true",
        help="Print resolved URL without fetching"
    )

    args = parser.parse_args()

    try:
        if args.command == "fetch":
            print(fetch_url(args.url, args.chars))

        elif args.command == "search":
            print(search_web(args.query, args.results))

        elif args.command == "resolve":
            full_ver, major_ver = resolve_version(args.detector)
            url = args.url_template.format(version=full_ver, major=major_ver)
            print(f"Detector:  {args.detector}")
            print(f"Installed: {full_ver} (major: {major_ver})")
            print(f"URL:       {url}")
            print()
            if not args.dry_run:
                print(fetch_url(url, args.chars))

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
