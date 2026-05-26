from src.store.loader import FleetStore
from src.tools.topology import get_fleet_topology
from src.tools.contracts import get_api_contract
from src.tools.data_model import get_shared_data_model
from src.tools.deployment import get_deployment_map
from src.tools.impact import check_cross_app_impact


async def test_topology_returns_all_services(store: FleetStore) -> None:
    result = await get_fleet_topology(store)
    assert result["service_count"] >= 4
    assert isinstance(result["fleet"], list)
    ids = {svc["id"] for svc in result["fleet"]}
    assert "api-adswire" in ids


async def test_contract_found(store: FleetStore) -> None:
    result = await get_api_contract("app-adswire", "api-adswire", store)
    assert "contracts" in result
    assert len(result["contracts"]) >= 1
    assert "warning" not in result


async def test_contract_direct_api_to_app(store: FleetStore) -> None:
    # [DEVIATION 006] api-to-app-policy-invalidation provides a direct match;
    # reverse-fallback path is not exercisable with current reference data.
    result = await get_api_contract("api-adswire", "app-adswire", store)
    assert "contracts" in result
    assert len(result["contracts"]) >= 1
    assert "warning" not in result


async def test_contract_not_found(store: FleetStore) -> None:
    result = await get_api_contract("api-adswire", "www-adswire", store)
    assert result["contracts"] == []
    assert "warning" in result


async def test_shared_data_model(store: FleetStore) -> None:
    result = await get_shared_data_model(store)
    assert result["model_count"] >= 3
    ids = {m["id"] for m in result["data_models"]}
    assert "landlord-db" in ids


async def test_deployment_map_all(store: FleetStore) -> None:
    result = await get_deployment_map(None, store)
    assert result["deployment_count"] >= 4
    assert result["environment_filter"] is None


async def test_deployment_map_filtered(store: FleetStore) -> None:
    result = await get_deployment_map("production", store)
    assert all(d["environment"] == "production" for d in result["deployments"])


async def test_impact_known_path(store: FleetStore) -> None:
    result = await check_cross_app_impact(
        "api.adswire.io/auth/sanctum.py", store
    )
    assert "api-adswire" in result["owning_services"]
    assert result["cross_app_risk"] in ("low", "medium", "high")


async def test_impact_unknown_path(store: FleetStore) -> None:
    result = await check_cross_app_impact("some/unknown/file.py", store)
    assert result["cross_app_risk"] == "none"
    assert "warning" in result
