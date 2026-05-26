from pathlib import Path
import pytest
from src.store.loader import FleetStore


@pytest.fixture
def store(tmp_path: Path) -> FleetStore:
    """FleetStore loaded from the generic example-fleet test fixture."""
    fleet_dir = Path(__file__).parent / "fixtures" / "example-fleet"
    s = FleetStore(fleet_dir)
    s.load()
    return s
