from src.store.loader import FleetStore


def test_services_loaded(store: FleetStore) -> None:
    services = store.get_services()
    assert len(services) >= 4
    ids = {s.id for s in services}
    assert "api-adswire" in ids
    assert "app-adswire" in ids


def test_get_service_by_id(store: FleetStore) -> None:
    svc = store.get_service("api-adswire")
    assert svc is not None
    assert svc.role == "mcp-server"
    assert svc.port == 8095


def test_get_contracts(store: FleetStore) -> None:
    contracts = store.get_contracts(from_service="app-adswire", to_service="api-adswire")
    assert len(contracts) >= 1
    assert contracts[0].from_service == "app-adswire"


def test_get_data_models(store: FleetStore) -> None:
    models = store.get_data_models()
    ids = {m.id for m in models}
    assert "landlord-db" in ids
    assert "tenant-db" in ids


def test_get_deployments(store: FleetStore) -> None:
    all_deps = store.get_deployments()
    assert len(all_deps) >= 4
    prod = store.get_deployments(environment="production")
    assert all(d.environment == "production" for d in prod)


def test_get_landmines(store: FleetStore) -> None:
    all_lm = store.get_landmines()
    assert len(all_lm) >= 5
    api_lm = store.get_landmines(service_id="api-adswire")
    assert all("api-adswire" in lm.affected_services for lm in api_lm)


def test_get_services_owning_path(store: FleetStore) -> None:
    matching = store.get_services_owning_path("api.adswire.io/auth/sanctum.py")
    assert len(matching) == 1
    assert matching[0].id == "api-adswire"


def test_unmapped_path_returns_empty(store: FleetStore) -> None:
    matching = store.get_services_owning_path("some/unknown/path.py")
    assert matching == []
