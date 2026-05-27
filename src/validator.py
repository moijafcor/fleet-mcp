from __future__ import annotations

import dataclasses
from pathlib import Path

from src.store.loader import FleetStore


@dataclasses.dataclass
class ValidationError:
    file: str
    entry_id: str
    field: str
    value: str
    message: str


@dataclasses.dataclass
class ValidationResult:
    valid: bool
    errors: list[ValidationError]


class FleetValidator:
    def validate(self, fleet_dir: Path) -> ValidationResult:
        store = FleetStore(fleet_dir)
        store.load()
        errors: list[ValidationError] = []
        valid_ids: set[str] = {s.id for s in store.get_services()}
        self._check_contracts(store, valid_ids, errors)
        self._check_landmines(store, valid_ids, errors)
        self._check_data_models(store, valid_ids, errors)
        self._check_deployments(store, valid_ids, errors)
        return ValidationResult(valid=len(errors) == 0, errors=errors)

    def _check_contracts(
        self,
        store: FleetStore,
        valid_ids: set[str],
        errors: list[ValidationError],
    ) -> None:
        for c in store.get_contracts():
            for field in ("from_service", "to_service"):
                val: str = getattr(c, field)
                if val == "":
                    errors.append(ValidationError(
                        file="contracts.yaml",
                        entry_id=c.id,
                        field=field,
                        value=val,
                        message="empty-string service ID",
                    ))
                elif val not in valid_ids:
                    errors.append(ValidationError(
                        file="contracts.yaml",
                        entry_id=c.id,
                        field=field,
                        value=val,
                        message=f"unknown service ID '{val}'",
                    ))

    def _check_landmines(
        self,
        store: FleetStore,
        valid_ids: set[str],
        errors: list[ValidationError],
    ) -> None:
        for lm in store.get_landmines():
            for i, svc_id in enumerate(lm.affected_services):
                if svc_id == "":
                    errors.append(ValidationError(
                        file="landmines.yaml",
                        entry_id=lm.id,
                        field=f"affected_services[{i}]",
                        value=svc_id,
                        message="empty-string service ID",
                    ))
                elif svc_id not in valid_ids:
                    errors.append(ValidationError(
                        file="landmines.yaml",
                        entry_id=lm.id,
                        field=f"affected_services[{i}]",
                        value=svc_id,
                        message=f"unknown service ID '{svc_id}'",
                    ))

    def _check_data_models(
        self,
        store: FleetStore,
        valid_ids: set[str],
        errors: list[ValidationError],
    ) -> None:
        for dm in store.get_data_models():
            owner = dm.owner_service
            if owner == "":
                errors.append(ValidationError(
                    file="data_models.yaml",
                    entry_id=dm.id,
                    field="owner_service",
                    value=owner,
                    message="empty-string service ID",
                ))
            elif owner not in valid_ids:
                errors.append(ValidationError(
                    file="data_models.yaml",
                    entry_id=dm.id,
                    field="owner_service",
                    value=owner,
                    message=f"unknown service ID '{owner}'",
                ))
            for i, svc_id in enumerate(dm.consumer_services):
                if svc_id == "":
                    errors.append(ValidationError(
                        file="data_models.yaml",
                        entry_id=dm.id,
                        field=f"consumer_services[{i}]",
                        value=svc_id,
                        message="empty-string service ID",
                    ))
                elif svc_id not in valid_ids:
                    errors.append(ValidationError(
                        file="data_models.yaml",
                        entry_id=dm.id,
                        field=f"consumer_services[{i}]",
                        value=svc_id,
                        message=f"unknown service ID '{svc_id}'",
                    ))

    def _check_deployments(
        self,
        store: FleetStore,
        valid_ids: set[str],
        errors: list[ValidationError],
    ) -> None:
        for d in store.get_deployments():
            composite_id = f"{d.service_id}/{d.environment}"
            if d.service_id == "":
                errors.append(ValidationError(
                    file="deployment.yaml",
                    entry_id=composite_id,
                    field="service_id",
                    value=d.service_id,
                    message="empty-string service ID",
                ))
            elif d.service_id not in valid_ids:
                errors.append(ValidationError(
                    file="deployment.yaml",
                    entry_id=composite_id,
                    field="service_id",
                    value=d.service_id,
                    message=f"unknown service ID '{d.service_id}'",
                ))
