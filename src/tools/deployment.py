from typing import Any, Optional

from src.store.loader import FleetStore


async def get_deployment_map(
    environment: Optional[str], store: FleetStore
) -> dict[str, Any]:
    deployments = store.get_deployments(environment=environment)
    return {
        "environment_filter": environment,
        "deployment_count": len(deployments),
        "deployments": [d.model_dump(exclude_none=True) for d in deployments],
    }
