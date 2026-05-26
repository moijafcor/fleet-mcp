import sys
from pathlib import Path

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
