from pathlib import Path

import pytest

from src.validator import FleetValidator


EXAMPLE_FLEET = Path(__file__).parent / "fixtures" / "example-fleet"
INVALID_FLEET = Path(__file__).parent / "fixtures" / "invalid-fleet"


def test_valid_fleet_passes() -> None:
    result = FleetValidator().validate(EXAMPLE_FLEET)
    assert result.valid is True
    assert result.errors == []


def test_invalid_fleet_reports_errors() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    assert result.valid is False
    assert len(result.errors) == 6


def test_empty_string_service_id_in_contract() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "contracts.yaml"
        and e.entry_id == "bad-contract-empty-from"
        and e.field == "from_service"
    )
    assert err.value == ""
    assert err.message == "empty-string service ID"


def test_unknown_service_in_contract_from_service() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "contracts.yaml"
        and e.entry_id == "bad-contract-unknown-from"
        and e.field == "from_service"
    )
    assert err.value == "svc-unknown"
    assert "unknown service ID" in err.message


def test_unknown_service_in_landmine_affected_services() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "landmines.yaml"
        and e.entry_id == "bad-landmine-unknown-service"
        and e.field == "affected_services[1]"
    )
    assert err.value == "svc-unknown"
    assert "unknown service ID" in err.message


def test_unknown_owner_service_in_data_model() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "data_models.yaml"
        and e.entry_id == "bad-data-model"
        and e.field == "owner_service"
    )
    assert err.value == "svc-unknown"
    assert "unknown service ID" in err.message


def test_unknown_consumer_service_in_data_model() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "data_models.yaml"
        and e.entry_id == "bad-data-model"
        and e.field == "consumer_services[1]"
    )
    assert err.value == "svc-also-unknown"
    assert "unknown service ID" in err.message


def test_unknown_service_id_in_deployment() -> None:
    result = FleetValidator().validate(INVALID_FLEET)
    err = next(
        e for e in result.errors
        if e.file == "deployment.yaml"
        and e.field == "service_id"
        and e.value == "svc-unknown"
    )
    assert "unknown service ID" in err.message


def test_empty_fleet_dir_passes() -> None:
    """An empty fleet dir (no YAML files) is vacuously valid."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        result = FleetValidator().validate(Path(tmpdir))
        assert result.valid is True
        assert result.errors == []


def test_valid_fleet_has_no_cross_reference_errors() -> None:
    """Explicitly assert no errors leak from the example fleet fixture."""
    result = FleetValidator().validate(EXAMPLE_FLEET)
    for err in result.errors:
        pytest.fail(
            f"Unexpected error in example-fleet: {err.file}[{err.entry_id}].{err.field}={err.value!r}"
        )
