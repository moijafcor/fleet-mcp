from typing import Any

from src.store.loader import FleetStore


async def get_fleet_topology(store: FleetStore) -> dict[str, Any]:
    services = store.get_services()
    return {
        "service_count": len(services),
        "fleet": [
            {
                "id": s.id,
                "name": s.name,
                "role": s.role,
                "stack": s.stack.model_dump(),
                "urls": s.urls.model_dump(exclude_none=True),
                "entry_points": s.entry_points,
                "description": s.description,
            }
            for s in services
        ],
    }
