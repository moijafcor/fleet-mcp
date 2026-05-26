from typing import Any

from src.store.loader import FleetStore


async def get_shared_data_model(store: FleetStore) -> dict[str, Any]:
    models = store.get_data_models()
    return {
        "model_count": len(models),
        "data_models": [m.model_dump(exclude_none=True) for m in models],
    }
