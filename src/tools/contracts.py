from typing import Any

from src.store.loader import FleetStore


async def get_api_contract(
    from_service: str, to_service: str, store: FleetStore
) -> dict[str, Any]:
    contracts = store.get_contracts(
        from_service=from_service, to_service=to_service
    )
    if contracts:
        return {"contracts": [c.model_dump(exclude_none=True) for c in contracts]}

    reverse = store.get_contracts(
        from_service=to_service, to_service=from_service
    )
    if reverse:
        return {
            "warning": (
                f"No contract found from '{from_service}' to '{to_service}'. "
                f"Found {len(reverse)} contract(s) in the reverse direction."
            ),
            "contracts": [c.model_dump(exclude_none=True) for c in reverse],
        }

    return {
        "contracts": [],
        "warning": (
            f"No contract found between '{from_service}' and '{to_service}'. "
            f"Verify service IDs via fleet_get_topology."
        ),
    }
