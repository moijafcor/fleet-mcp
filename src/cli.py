import argparse
import dataclasses
import json
import sys
from pathlib import Path

from src.config import get_settings


_TEMPLATES: dict[str, str] = {
    "services.yaml": (
        "# Fleet services — one entry per deployable application.\n"
        "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/services.yaml\n"
        "[]\n"
    ),
    "contracts.yaml": (
        "# API contracts between services.\n"
        "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/contracts.yaml\n"
        "[]\n"
    ),
    "data_models.yaml": (
        "# Shared data models (databases, caches, object stores).\n"
        "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/data_models.yaml\n"
        "[]\n"
    ),
    "deployment.yaml": (
        "# Deployment entries — one per service per environment.\n"
        "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/deployment.yaml\n"
        "[]\n"
    ),
    "landmines.yaml": (
        "# Cross-app breakage risks.\n"
        "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/landmines.yaml\n"
        "[]\n"
    ),
}


def init_command() -> None:
    """Scaffold a blank fleet/ directory in the current working directory."""
    dest = Path.cwd() / "fleet"
    if dest.exists():
        print(
            f"fleet/ already exists at {dest}. "
            "Remove or rename it before running init.",
            file=sys.stderr,
        )
        sys.exit(1)
    dest.mkdir()
    for filename, content in _TEMPLATES.items():
        (dest / filename).write_text(content)
    print(f"fleet/ scaffolded at {dest}")
    print(f"Set FLEET_DATA_DIR={dest} or run from this directory.")


def validate_command(fleet_dir: Path, json_output: bool = False) -> int:
    """Run cross-reference validation against fleet_dir. Returns exit code."""
    import pydantic
    import yaml as _yaml

    from src.validator import FleetValidator

    try:
        result = FleetValidator().validate(fleet_dir)
    except (pydantic.ValidationError, _yaml.YAMLError, OSError) as exc:
        if json_output:
            print(json.dumps({"valid": False, "load_error": str(exc), "errors": []}))
        else:
            print(f"Fatal: could not load fleet YAML: {exc}", file=sys.stderr)
        return 2

    if json_output:
        print(
            json.dumps(
                {
                    "valid": result.valid,
                    "error_count": len(result.errors),
                    "errors": [dataclasses.asdict(e) for e in result.errors],
                }
            )
        )
    else:
        if result.valid:
            print("✓ Fleet YAML is consistent.")
        else:
            print(f"Fleet YAML validation failed: {len(result.errors)} error(s):")
            for err in result.errors:
                print(
                    f"  {err.file} [{err.entry_id}] {err.field}:"
                    f" {err.message} (value: {err.value!r})"
                )
    return 0 if result.valid else 1


def validate_command_entry() -> None:
    """Entry point for `fleet-mcp-validate`. Parses args and calls validate_command()."""
    parser = argparse.ArgumentParser(
        prog="fleet-mcp-validate",
        description="Validate fleet YAML cross-reference consistency.",
    )
    parser.add_argument(
        "--fleet-dir",
        default=get_settings().fleet_data_dir,
        help="Path to fleet/ data directory (default: $FLEET_DATA_DIR or 'fleet')",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output.",
    )
    args = parser.parse_args()
    sys.exit(validate_command(Path(args.fleet_dir), args.json))


def fleet_mcp_main() -> None:
    """Dispatcher for the `fleet-mcp` entry point.

    Routes `fleet-mcp validate [...]` to validate_command_entry().
    All other invocations fall through to the MCP server runner unchanged.
    sys.argv is NOT modified in the server branch.
    """
    if len(sys.argv) >= 2 and sys.argv[1] == "validate":
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        validate_command_entry()
    else:
        from src.server import mcp
        mcp.run()
