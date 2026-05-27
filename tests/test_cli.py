import contextlib
import io
import json
from pathlib import Path

from src.cli import validate_command


EXAMPLE_FLEET = Path(__file__).parent / "fixtures" / "example-fleet"
INVALID_FLEET = Path(__file__).parent / "fixtures" / "invalid-fleet"


def test_validate_exits_0_on_valid_fleet() -> None:
    code = validate_command(EXAMPLE_FLEET, json_output=False)
    assert code == 0


def test_validate_exits_1_on_invalid_fleet() -> None:
    code = validate_command(INVALID_FLEET, json_output=False)
    assert code == 1


def test_validate_json_format_on_valid_fleet() -> None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = validate_command(EXAMPLE_FLEET, json_output=True)
    payload = json.loads(buf.getvalue())
    assert payload["valid"] is True
    assert payload["error_count"] == 0
    assert payload["errors"] == []
    assert code == 0


def test_validate_json_format_on_invalid_fleet() -> None:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = validate_command(INVALID_FLEET, json_output=True)
    payload = json.loads(buf.getvalue())
    assert payload["valid"] is False
    assert payload["error_count"] == 6
    assert len(payload["errors"]) == 6
    fields = {"file", "entry_id", "field", "value", "message"}
    for err in payload["errors"]:
        assert fields.issubset(err.keys())
    assert code == 1


def test_validate_exits_2_on_invalid_yaml(tmp_path: Path) -> None:
    """Structurally invalid YAML causes exit 2."""
    bad_yaml = tmp_path / "services.yaml"
    bad_yaml.write_text("{ invalid yaml: [[[")
    code = validate_command(tmp_path, json_output=False)
    assert code == 2


def test_validate_exits_2_on_invalid_yaml_json_output(tmp_path: Path) -> None:
    buf = io.StringIO()
    bad_yaml = tmp_path / "contracts.yaml"
    bad_yaml.write_text("{ not valid yaml: [[[")
    with contextlib.redirect_stdout(buf):
        code = validate_command(tmp_path, json_output=True)
    assert code == 2
    payload = json.loads(buf.getvalue())
    assert payload["valid"] is False
    assert "load_error" in payload


def test_validate_exits_0_on_empty_dir(tmp_path: Path) -> None:
    """Empty dir is vacuously valid."""
    code = validate_command(tmp_path, json_output=False)
    assert code == 0
