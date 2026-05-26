from pathlib import Path
import pytest
from src.store.loader import FleetStore


@pytest.fixture
def store(tmp_path: Path) -> FleetStore:
    """FleetStore loaded from the AdsWire reference dataset in examples/adswire/."""
    fleet_dir = Path(__file__).parent.parent / "examples" / "adswire"
    s = FleetStore(fleet_dir)
    s.load()
    return s
