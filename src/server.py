"""fleet-mcp — fleet-level MCP server for multi-app SaaS situational awareness.

Transport : stdio (default) or HTTP via `mcp run src/server.py --transport http`
Auth      : none (developer tool)
Tools     : fleet_get_topology, fleet_get_api_contract, fleet_get_shared_data_model,
            fleet_get_deployment_map, fleet_check_cross_app_impact
"""

from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from src.config import get_settings
from src.store.loader import FleetStore
from src.tools.contracts import get_api_contract
from src.tools.data_model import get_shared_data_model
from src.tools.deployment import get_deployment_map
from src.tools.impact import check_cross_app_impact
from src.tools.topology import get_fleet_topology

settings = get_settings()
_store = FleetStore(Path(settings.fleet_data_dir))
_store.load()

mcp = FastMCP("fleet-mcp")


@mcp.tool()
async def fleet_get_topology() -> dict[str, Any]:
    """Get all services in the fleet with their roles, stacks, and URLs."""
    return await get_fleet_topology(_store)


@mcp.tool()
async def fleet_get_api_contract(from_service: str, to_service: str) -> dict[str, Any]:
    """Get the API contract(s) between two services. Pass service IDs (e.g.
    'api-adswire', 'app-adswire'). Use fleet_get_topology to discover valid IDs."""
    return await get_api_contract(from_service, to_service, _store)


@mcp.tool()
async def fleet_get_shared_data_model() -> dict[str, Any]:
    """Get the shared data model — all cross-app data stores with ownership and
    critical tables."""
    return await get_shared_data_model(_store)


@mcp.tool()
async def fleet_get_deployment_map(environment: Optional[str] = None) -> dict[str, Any]:
    """Get the runtime deployment topology. Optionally filter by environment:
    'production', 'staging', or 'local'."""
    return await get_deployment_map(environment, _store)


@mcp.tool()
async def fleet_check_cross_app_impact(file_path: str) -> dict[str, Any]:
    """Check which other apps are affected by touching a file. Pass a path such as
    'api.adswire.io/auth/sanctum.py'. Returns owning services, impacted contracts,
    landmines, and a cross_app_risk rating (none | low | medium | high)."""
    return await check_cross_app_impact(file_path, _store)


if __name__ == "__main__":
    mcp.run()
