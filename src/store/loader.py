import fnmatch
from pathlib import Path
from typing import Optional, TypeVar

import yaml
from pydantic import BaseModel

from src.models.contract import ApiContract
from src.models.data_model import SharedDataModel
from src.models.deployment import DeploymentEntry
from src.models.landmine import Landmine
from src.models.service import Service

M = TypeVar("M", bound=BaseModel)


class FleetStore:
    def __init__(self, fleet_dir: Path) -> None:
        self._fleet_dir = fleet_dir
        self._services: list[Service] = []
        self._contracts: list[ApiContract] = []
        self._data_models: list[SharedDataModel] = []
        self._deployments: list[DeploymentEntry] = []
        self._landmines: list[Landmine] = []

    def load(self) -> None:
        self._services = self._load_yaml("services.yaml", Service)
        self._contracts = self._load_yaml("contracts.yaml", ApiContract)
        self._data_models = self._load_yaml("data_models.yaml", SharedDataModel)
        self._deployments = self._load_yaml("deployment.yaml", DeploymentEntry)
        self._landmines = self._load_yaml("landmines.yaml", Landmine)

    def _load_yaml(self, filename: str, model_class: type[M]) -> list[M]:
        path = self._fleet_dir / filename
        if not path.exists():
            return []
        with open(path) as f:
            data = yaml.safe_load(f) or []
        return [model_class.model_validate(item) for item in data]

    # ── Services ──────────────────────────────────────────────────────────────

    def get_services(self) -> list[Service]:
        return list(self._services)

    def get_service(self, service_id: str) -> Optional[Service]:
        return next((s for s in self._services if s.id == service_id), None)

    def get_services_owning_path(self, file_path: str) -> list[Service]:
        matching: list[Service] = []
        for service in self._services:
            for pattern in service.owns.path_patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    matching.append(service)
                    break
        return matching

    # ── Contracts ─────────────────────────────────────────────────────────────

    def get_contracts(
        self,
        from_service: Optional[str] = None,
        to_service: Optional[str] = None,
    ) -> list[ApiContract]:
        result = list(self._contracts)
        if from_service:
            result = [c for c in result if c.from_service == from_service]
        if to_service:
            result = [c for c in result if c.to_service == to_service]
        return result

    # ── Shared data models ────────────────────────────────────────────────────

    def get_data_models(self) -> list[SharedDataModel]:
        return list(self._data_models)

    # ── Deployments ───────────────────────────────────────────────────────────

    def get_deployments(self, environment: Optional[str] = None) -> list[DeploymentEntry]:
        if environment:
            return [d for d in self._deployments if d.environment == environment]
        return list(self._deployments)

    # ── Landmines ─────────────────────────────────────────────────────────────

    def get_landmines(self, service_id: Optional[str] = None) -> list[Landmine]:
        if service_id:
            return [lm for lm in self._landmines if service_id in lm.affected_services]
        return list(self._landmines)
