from typing import Any

from src.store.loader import FleetStore


async def check_cross_app_impact(file_path: str, store: FleetStore) -> dict[str, Any]:
    owning = store.get_services_owning_path(file_path)

    if not owning:
        return {
            "file_path": file_path,
            "owning_services": [],
            "impacted_contracts": [],
            "landmines": [],
            "cross_app_risk": "none",
            "warning": (
                "No service ownership mapping found for this path. "
                "Add a matching pattern to fleet/services.yaml owns.path_patterns."
            ),
        }

    contracts: list[str] = []
    seen_contracts: set[str] = set()
    landmines: list[dict[str, Any]] = []
    seen_landmines: set[str] = set()

    for service in owning:
        for c in (
            store.get_contracts(from_service=service.id)
            + store.get_contracts(to_service=service.id)
        ):
            if c.id not in seen_contracts:
                contracts.append(c.id)
                seen_contracts.add(c.id)
        for lm in store.get_landmines(service_id=service.id):
            if lm.id not in seen_landmines:
                landmines.append(
                    {
                        "id": lm.id,
                        "severity": lm.severity,
                        "trigger": lm.trigger,
                        "consequence": lm.consequence,
                        "remedy": lm.remedy,
                    }
                )
                seen_landmines.add(lm.id)

    risk = (
        "high" if landmines
        else "medium" if contracts
        else "low"
    )

    return {
        "file_path": file_path,
        "owning_services": [s.id for s in owning],
        "impacted_contracts": contracts,
        "landmines": landmines,
        "cross_app_risk": risk,
    }
