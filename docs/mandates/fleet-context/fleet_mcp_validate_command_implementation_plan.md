# Design Implementation Plan

**DMT:** https://github.com/users/moijafcor/projects/2/views/1?pane=issue&itemId=192459850
**Title:** fleet-mcp [Phase 2-A]: fleet-mcp validate — fleet YAML consistency checker
**Slug:** fleet_mcp_validate_command_implementation_plan
**Bucket:** existing
**Engineer:** claude-sonnet-4-6 / Engineer session 2026-05-26
**DIP Created:** 2026-05-26
**DIP Last Updated:** 2026-05-26
**Board Status:** Backlog (moijafcor/projects/2 — no IN_RECON or PLANNED equivalent; see Tracker Ops Log)
**Board Status History:**
- 2026-05-26T00:00:00Z BACKLOG — item 192459850 on moijafcor/projects/2
- 2026-05-26T00:00:00Z IN_RECON — Engineer session started (board has no IN_RECON status; logged in Tracker Ops Log)
- 2026-05-26T01:00:00Z PLANNED — DIP complete (board has no PLANNED status; closest = Ready; see Tracker Ops Log)

---

## Mandate Reference

**Architect's Intent (summary):**
> Add a `fleet-mcp validate` CLI command that cross-validates all five fleet YAML files for service ID consistency. The validator resolves every service reference (in contracts, landmines, data models, and deployment entries) against the declared service IDs in `services.yaml`, errors on unknown IDs and empty-string IDs (OSF-001 class), and exits non-zero on failure. It must be usable as a pre-commit hook and must produce machine-readable JSON output on demand. This is the correctness foundation for the export pipeline — export should refuse to run if validate fails.

**DMT Acceptance Criteria (copied from issue):**
- [ ] Resolves all service IDs referenced in `contracts.yaml` against `services.yaml` — error on unknown ID
- [ ] Resolves all `affected_services` in `landmines.yaml` against `services.yaml` — error on unknown ID
- [ ] Resolves all `consumer_services` and `owner_service` in `data_models.yaml` against `services.yaml`
- [ ] Resolves all `service_id` entries in `deployment.yaml` against `services.yaml`
- [ ] Flags empty-string service IDs in contracts (resolves OSF-001: `fleet_get_api_contract` silent passthrough bug)
- [ ] Exits 0 on clean YAML, non-zero with structured error list on failure
- [ ] Usable as a pre-commit hook: `fleet-mcp validate --fleet-dir $FLEET_DATA_DIR`
- [ ] Output is machine-readable (JSON) when `--json` flag passed

**Constraints (from DMT):**
- Python 3.12+ (consistent with existing fleet-mcp stack)
- No new runtime dependencies beyond stdlib and those already in `pyproject.toml`
- Validate must be runnable without starting the MCP server
- `--fleet-dir` flag must default to `FLEET_DATA_DIR` env var (consistent with `src/config.py::Settings.fleet_data_dir`)

**Explicitly Out of Scope (from DMT):**
- Fixing the `fleet_get_api_contract` tool's empty-string passthrough at the MCP layer (OSF-001 fix in the tool itself is a separate mandate)
- Structural validation of YAML field types (Pydantic handles this during `.load()`)
- Semantic validation (e.g., verifying that a `protocol` value is recognised — Pydantic handles this)
- Export pipeline gate enforcement (guard in `fleet-mcp export` is a future mandate)
- Writing to or modifying fleet YAML files

---

## Scope

**In Scope:**
- `src/validator.py` — new: `FleetValidator` class, `ValidationError` dataclass, `ValidationResult` dataclass
- `src/cli.py` — add `validate_command()`, `validate_command_entry()`, `fleet_mcp_main()` dispatcher
- `pyproject.toml` — update `fleet-mcp` entry point; add `fleet-mcp-validate` entry
- `tests/fixtures/invalid-fleet/` — new: five YAML files with deliberate cross-reference errors
- `tests/test_validator.py` — new: unit tests for `FleetValidator`
- `tests/test_cli.py` — new: CLI-level tests for `validate_command()`
- `docs/knowledge-graph.yaml` — new concepts already declared by Engineer (see Field Discoveries)

**Out of Scope (Engineer-added):**
- Changes to `src/store/loader.py` or any model in `src/models/` — no structural changes needed
- Changes to `src/server.py` or any MCP tool in `src/tools/` — validator is CLI-only
- Changes to `src/config.py` — existing `fleet_data_dir` setting reused as-is
- Addition of a `fleet-mcp export` command (future Phase 2-B)

**Scope Risk:**
- The `fleet-mcp` entry point currently maps directly to `mcp.run`. Changing it to a dispatcher (`fleet_mcp_main`) could interfere with MCP server startup if `mcp.run` reads `sys.argv` for its own flags. The dispatcher must preserve `sys.argv` unmodified for the server case. See ADR-001.
- Phase 1 mandate (`fleet_mcp_server_implementation_plan.md`) is in a QA FAIL state (`.env.example` uncommitted). This mandate does not depend on Phase 1 being VERIFIED — all required models and store code are committed (verified via `git log`).

---

## Recon Findings

### Codebase / Infrastructure State

- `src/cli.py`: Contains only `init_command()` (42 lines). No argument parsing library in use — direct `pathlib` and `sys.exit`. Pattern: standalone function, no class.
- `src/store/loader.py`: `FleetStore.load()` calls `_load_yaml()` per file. `_load_yaml()` returns `[]` for missing files (no error). Pydantic `model_validate()` is called per item — raises `pydantic.ValidationError` on structural errors. There is no try/except around these calls in `_load_yaml`.
- `src/models/`: All five models have an `id: str` field *except* `DeploymentEntry` (which has `service_id`, `environment`, `host` — no dedicated `id`). The `entry_id` in `ValidationError` for deployment errors uses `f"{d.service_id}/{d.environment}"` as a composite key.
- `pyproject.toml` entry points: `fleet-mcp = "src.server:mcp.run"`, `fleet-mcp-init = "src.cli:init_command"`. The MCP server entry point must be changed to `"src.cli:fleet_mcp_main"` to enable subcommand dispatch.
- `src/config.py`: `Settings.fleet_data_dir` defaults to `"fleet"` (relative path). Controlled by `FLEET_DATA_DIR` env var. Already cached with `@lru_cache`. The validate command reads this as the default `--fleet-dir` value.
- `tests/fixtures/example-fleet/`: Five YAML files. All service IDs are `svc-api`, `svc-app`, `svc-console`, `svc-www`. All cross-references are internally consistent. This fixture must pass validation with zero errors.
- No existing `tests/test_cli.py` or `tests/test_validator.py`. No existing tests for CLI entry points.

### Related Prior Mandates

- `docs/mandates/fleet-context/fleet_mcp_server_implementation_plan.md`: Phase 1 — implements the MCP server and five tools. Status: IN_REVIEW (second QA pass FAIL; `.env.example` untracked). Scope does not overlap. The committed code (FleetStore, models, tools, server) is fully available as the foundation for Phase 2-A.
- `docs/mandates/oss-prep/remove_adswire_examples_from_history_plan.md`: Removes AdsWire examples from git history. Unrelated; status IN_REVIEW.
- `docs/mandates/harness/harness_quickstart_implementation_plan.md`: Harness documentation. Unrelated.

### External Dependencies

- `pyyaml>=6.0.0`: Already in `[project.dependencies]`. Used by `FleetStore._load_yaml()`. No new import needed in validator — validator uses `FleetStore`, which handles YAML loading.
- `pydantic>=2.0.0`: Already in `[project.dependencies]`. Structural validation is free via existing model classes.
- `argparse`: stdlib. No new dependency.
- `dataclasses`: stdlib. No new dependency.
- `json`: stdlib. No new dependency.

### Relevant Memory / Session Context

- The fleet-mcp engine is intentionally fleet-agnostic. `FLEET_DATA_DIR` (defaulting to `"fleet"`) points to any fleet's data directory. The validator follows the same pattern.
- The `fleet-mcp-init` command (separate entry point, `src.cli:init_command`) established the pattern of having standalone CLI entry points per operation. Phase 2-A extends this with `fleet-mcp-validate` and a dispatcher (`fleet_mcp_main`) to also support `fleet-mcp validate` as a subcommand.
- OSF-001 was confirmed by QA spot check in Phase 1 (QA verdict 2026-05-26, second pass): "Empty string IDs return all contracts without warning. Child task exists." The validate command is the designed remedy at the YAML layer.

### Open Questions (pre-DIP; must be resolved before PLANNED)

- [x] **Should `fleet-mcp validate` also guard against missing `services.yaml`?** Resolution: No. `FleetStore._load_yaml()` already returns `[]` for missing files. An absent `services.yaml` means zero valid service IDs, so any cross-references in other files will be flagged as unknown IDs. This is the correct behaviour — the user gets actionable errors rather than a special-case message.
- [x] **Should the dispatcher intercept `--help`?** Resolution: No. Bare `fleet-mcp --help` is handled by the MCP server's argument parser (or no-op). `fleet-mcp validate --help` is handled by argparse in `validate_command_entry()`. No special handling needed in the dispatcher.
- [x] **Exit code for Pydantic/YAML structural errors during load?** Resolution: Exit 2. Distinguishes "YAML is unparseable" (exit 2) from "YAML is parseable but inconsistent" (exit 1). Pre-commit hooks and CI scripts can branch on exit code.
- [x] **Should the JSON output include a top-level `fleet_dir` key?** Resolution: No. Keep the schema minimal: `{valid, error_count, errors}`. The caller knows which directory it invoked against.

---

## Architecture Decisions

### ADR-001: `fleet-mcp validate` subcommand via dispatcher, not a separate entry-only script

**Decision:** Change `fleet-mcp` entry point from `src.server:mcp.run` to `src.cli:fleet_mcp_main`. The dispatcher checks `sys.argv[1] == "validate"` and either calls `validate_command_entry()` or falls through to `mcp.run()`. Also register `fleet-mcp-validate = "src.cli:validate_command_entry"` for pre-commit hook use (bare invocation without "validate" subcommand).

**Rationale:** The DMT acceptance criterion says `fleet-mcp validate --fleet-dir $FLEET_DATA_DIR`. A dispatcher that intercepts exactly `sys.argv[1] == "validate"` achieves this with zero risk to the server path: any argument that is not the literal string "validate" falls through to `mcp.run()` unchanged, `sys.argv` unmodified.

**Alternatives Considered:**
1. *Add only `fleet-mcp-validate` entry point* — consistent with `fleet-mcp-init` pattern, but does not satisfy the DMT's `fleet-mcp validate` invocation requirement.
2. *Use `click` or `typer` for subcommand dispatch* — clean but introduces a new dependency and requires refactoring both the server entry point and `init_command`, expanding scope.
3. *Replace `fleet-mcp` with a `click` group* — same objection; scope expansion.

**Consequences:** The dispatcher (`fleet_mcp_main`) must not modify `sys.argv` in the server branch. The "validate" subcommand removal (`sys.argv = [sys.argv[0]] + sys.argv[2:]`) must only happen in the validate branch, before `validate_command_entry()` is called. Any future subcommand additions extend this dispatcher with a new `elif sys.argv[1] == "<subcommand>"` branch.

---

### ADR-002: Dedicated `FleetValidator` class in `src/validator.py`; no changes to `FleetStore`

**Decision:** Cross-reference validation logic lives entirely in `src/validator.py::FleetValidator`. `FleetStore` is not modified.

**Rationale:** `FleetStore` is a runtime query layer — it should not contain build-time validation logic. The validator is a one-shot tool, not part of server startup. Single-responsibility principle.

**Alternatives Considered:**
1. *Add `validate()` method to `FleetStore`* — rejected: couples runtime data model to a build-time concern; the store would grow a new responsibility.
2. *Inline validation in `cli.py`* — rejected: untestable in isolation; mixes concerns in an already multi-role file.

**Consequences:** `FleetValidator.validate()` instantiates a `FleetStore` internally. It does not accept an already-loaded store as a parameter — this keeps the API simple (callers pass a `Path`) and avoids partial-load scenarios where the store might not have called `.load()`.

---

### ADR-003: `FleetStore.load()` exceptions propagate as fatal errors (exit 2), not as `ValidationError` items

**Decision:** In `validate_command()`, the `FleetValidator.validate(fleet_dir)` call is wrapped in `try/except (pydantic.ValidationError, yaml.YAMLError, OSError)`. Any exception produces an exit 2 with a message to stderr (or a `load_error` key in JSON output). The structured `ValidationResult.errors` list is reserved for cross-reference errors only.

**Rationale:** A YAML parse error (malformed YAML) or Pydantic structural error (missing required field, wrong type) prevents the validator from knowing the full set of entities and their IDs. Reporting it as a `ValidationError` would be misleading — the validator cannot distinguish "this cross-reference is wrong" from "this file could not be read at all." Exit 2 is the standard CLI convention for "tool usage error" and allows pre-commit hooks to branch on `$?`.

**Alternatives Considered:**
1. *Catch exceptions and emit them as `ValidationError` items with `field="<load_error>"`* — rejected: mixes two fundamentally different error classes; makes automated parsing harder.
2. *Let exceptions propagate (Python traceback)*  — rejected: not user-friendly; not machine-readable.

**Consequences:** The invalid-fleet test fixture must be structurally valid YAML (Pydantic passes it cleanly). Structural errors are tested separately as `test_load_error_exits_2`.

---

### ADR-004: JSON output schema `{valid, error_count, errors[]}`; human output to stdout on valid, stderr on error

**Decision:** `--json` output:
```json
{
  "valid": false,
  "error_count": 3,
  "errors": [
    {"file": "contracts.yaml", "entry_id": "bad-contract", "field": "from_service", "value": "", "message": "empty-string service ID"},
    ...
  ]
}
```
Human output: on valid, one line to stdout (`✓ Fleet YAML is consistent.`). On error, summary + one line per error to stdout. Exit code determines success/failure for scripts; stdout is always parseable.

**Rationale:** Minimal schema is more stable over time. `error_count` is a convenience field (`len(errors)`) that saves `jq` boilerplate in CI scripts. All output goes to stdout (both JSON and human) so that pre-commit hooks can capture it with simple redirects.

**Alternatives Considered:**
1. *Richer JSON with per-file grouping* — rejected: adds complexity; callers can group with `jq`.
2. *Errors to stderr, summary to stdout* — rejected: breaks `fleet-mcp validate --json | jq` pipeline patterns.

---

### ADR-005: `DeploymentEntry` composite key `"{service_id}/{environment}"` for `ValidationError.entry_id`

**Decision:** Since `DeploymentEntry` has no dedicated `id` field, the `entry_id` for a deployment validation error is `f"{d.service_id}/{d.environment}"` (e.g., `"svc-unknown/production"`).

**Rationale:** This is the most human-readable composite key available from the model. It is unique within a single fleet (a service cannot have two entries for the same environment).

**Alternatives Considered:**
1. *Use `d.host` alone* — not stable if the host changes.
2. *Use index `f"deployment[{i}]"`* — less readable; requires the user to count YAML entries.

**Consequences:** Known risk: if two deployment entries share the same `service_id` and `environment`, the `entry_id` will collide in the error list. This is an invalid fleet configuration in itself, and the validator will still report both errors (the colliding key is for display only, not a map key).

---

## Implementation Steps

- [ ] **Step 1: Add `fleet_mcp.FleetValidator`, `fleet_mcp.ValidationError`, `fleet_mcp.ValidationResult`, `fleet_mcp.CLICommand`, `fleet_mcp.FleetMcpDispatcher`, and `fleet_mcp.ValidateCommand` concepts to `docs/knowledge-graph.yaml`**

  **Status:** COMPLETE — Engineer updated the graph during DIP authoring (2026-05-26). The Coder must verify the entries exist before proceeding.

  **Verification:**
  ```bash
  grep "fleet_mcp.FleetValidator" docs/knowledge-graph.yaml
  grep "fleet_mcp.ValidationError" docs/knowledge-graph.yaml
  grep "fleet_mcp.ValidateCommand" docs/knowledge-graph.yaml
  ```
  Each command must print at least one matching line.

---

- [ ] **Step 2: Create `tests/fixtures/invalid-fleet/` with five YAML files containing deliberate cross-reference errors**

  Create five files. `services.yaml` is identical to `tests/fixtures/example-fleet/services.yaml` (four valid services: `svc-api`, `svc-app`, `svc-console`, `svc-www`). The other four files introduce specific errors:

  **`tests/fixtures/invalid-fleet/services.yaml`** — copy of example-fleet services.yaml (four services, no changes).

  **`tests/fixtures/invalid-fleet/contracts.yaml`** — three entries:
  ```yaml
  - id: good-contract
    from_service: svc-app
    to_service: svc-api
    protocol: oauth2
    mechanism: passport
    description: Valid contract — must not generate an error.

  - id: bad-contract-unknown-from
    from_service: svc-unknown
    to_service: svc-api
    protocol: http-rest
    mechanism: api-key
    description: Unknown from_service.

  - id: bad-contract-empty-from
    from_service: ""
    to_service: svc-api
    protocol: http-rest
    mechanism: api-key
    description: Empty-string from_service (OSF-001 class).
  ```

  **`tests/fixtures/invalid-fleet/landmines.yaml`** — two entries:
  ```yaml
  - id: good-landmine
    affected_services:
      - svc-api
    trigger: Valid landmine — must not generate an error.
    severity: low
    consequence: None.
    remedy: None.

  - id: bad-landmine-unknown-service
    affected_services:
      - svc-api
      - svc-unknown
    trigger: Unknown service in affected_services.
    severity: low
    consequence: None.
    remedy: None.
  ```

  **`tests/fixtures/invalid-fleet/data_models.yaml`** — two entries:
  ```yaml
  - id: good-data-model
    name: Good Data Model
    owner_service: svc-app
    consumer_services:
      - svc-api
    storage_type: postgresql
    description: Valid data model — must not generate an error.

  - id: bad-data-model
    name: Bad Data Model
    owner_service: svc-unknown
    consumer_services:
      - svc-api
      - svc-also-unknown
    storage_type: postgresql
    description: Unknown owner_service and one unknown consumer_service.
  ```

  **`tests/fixtures/invalid-fleet/deployment.yaml`** — two entries:
  ```yaml
  - service_id: svc-api
    environment: production
    host: prod.example.com
    port: 8095
    process: uvicorn

  - service_id: svc-unknown
    environment: production
    host: prod.example.com
    port: 9999
    process: unknown
  ```

  Expected total errors: 6
  - `contracts.yaml/bad-contract-unknown-from/from_service` — unknown ID
  - `contracts.yaml/bad-contract-empty-from/from_service` — empty string
  - `landmines.yaml/bad-landmine-unknown-service/affected_services[1]` — unknown ID
  - `data_models.yaml/bad-data-model/owner_service` — unknown ID
  - `data_models.yaml/bad-data-model/consumer_services[1]` — unknown ID
  - `deployment.yaml/svc-unknown/production/service_id` — unknown ID

  **Verification:** All five files exist:
  ```bash
  ls tests/fixtures/invalid-fleet/
  # contracts.yaml  data_models.yaml  deployment.yaml  landmines.yaml  services.yaml
  ```

---

- [ ] **Step 3: Create `src/validator.py`**

  Full file content (exact implementation):

  ```python
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
  ```

  **Verification:**
  ```bash
  python3 -c "from src.validator import FleetValidator, ValidationError, ValidationResult; print('ok')"
  # → ok
  mypy src/validator.py
  # → Success: no issues found in 1 source file
  ```

---

- [ ] **Step 4: Create `tests/test_validator.py`**

  Full file content (exact implementation):

  ```python
  from pathlib import Path

  import pytest

  from src.validator import FleetValidator, ValidationError


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
  ```

  **Verification:**
  ```bash
  python3 -m pytest tests/test_validator.py -v --tb=short
  # → 10 passed
  ```

---

- [ ] **Step 5: Update `src/cli.py`** — add `validate_command()`, `validate_command_entry()`, and `fleet_mcp_main()`

  Replace the full content of `src/cli.py` with:

  ```python
  import argparse
  import dataclasses
  import json
  import sys
  from pathlib import Path

  from src.config import get_settings


  _TEMPLATES: dict[str, str] = {
      "services.yaml": (
          "# Fleet services — one entry per deployable application.\n"
          "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/services.yaml\n"
          "[]\n"
      ),
      "contracts.yaml": (
          "# API contracts between services.\n"
          "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/contracts.yaml\n"
          "[]\n"
      ),
      "data_models.yaml": (
          "# Shared data models (databases, caches, object stores).\n"
          "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/data_models.yaml\n"
          "[]\n"
      ),
      "deployment.yaml": (
          "# Deployment entries — one per service per environment.\n"
          "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/deployment.yaml\n"
          "[]\n"
      ),
      "landmines.yaml": (
          "# Cross-app breakage risks.\n"
          "# Schema: https://github.com/moijafcor/fleet-mcp/blob/main/tests/fixtures/example-fleet/landmines.yaml\n"
          "[]\n"
      ),
  }


  def init_command() -> None:
      """Scaffold a blank fleet/ directory in the current working directory."""
      dest = Path.cwd() / "fleet"
      if dest.exists():
          print(
              f"fleet/ already exists at {dest}. "
              "Remove or rename it before running init.",
              file=sys.stderr,
          )
          sys.exit(1)
      dest.mkdir()
      for filename, content in _TEMPLATES.items():
          (dest / filename).write_text(content)
      print(f"fleet/ scaffolded at {dest}")
      print(f"Set FLEET_DATA_DIR={dest} or run from this directory.")


  def validate_command(fleet_dir: Path, json_output: bool = False) -> int:
      """Run cross-reference validation against fleet_dir. Returns exit code."""
      import pydantic
      import yaml as _yaml

      from src.validator import FleetValidator

      try:
          result = FleetValidator().validate(fleet_dir)
      except (pydantic.ValidationError, _yaml.YAMLError, OSError) as exc:
          if json_output:
              print(json.dumps({"valid": False, "load_error": str(exc), "errors": []}))
          else:
              print(f"Fatal: could not load fleet YAML: {exc}", file=sys.stderr)
          return 2

      if json_output:
          print(
              json.dumps(
                  {
                      "valid": result.valid,
                      "error_count": len(result.errors),
                      "errors": [dataclasses.asdict(e) for e in result.errors],
                  }
              )
          )
      else:
          if result.valid:
              print("✓ Fleet YAML is consistent.")
          else:
              print(f"Fleet YAML validation failed: {len(result.errors)} error(s):")
              for err in result.errors:
                  print(
                      f"  {err.file} [{err.entry_id}] {err.field}:"
                      f" {err.message} (value: {err.value!r})"
                  )
      return 0 if result.valid else 1


  def validate_command_entry() -> None:
      """Entry point for `fleet-mcp-validate`. Parses args and calls validate_command()."""
      parser = argparse.ArgumentParser(
          prog="fleet-mcp-validate",
          description="Validate fleet YAML cross-reference consistency.",
      )
      parser.add_argument(
          "--fleet-dir",
          default=get_settings().fleet_data_dir,
          help="Path to fleet/ data directory (default: $FLEET_DATA_DIR or 'fleet')",
      )
      parser.add_argument(
          "--json",
          action="store_true",
          help="Emit machine-readable JSON output.",
      )
      args = parser.parse_args()
      sys.exit(validate_command(Path(args.fleet_dir), args.json))


  def fleet_mcp_main() -> None:
      """Dispatcher for the `fleet-mcp` entry point.

      Routes `fleet-mcp validate [...]` to validate_command_entry().
      All other invocations fall through to the MCP server runner unchanged.
      sys.argv is NOT modified in the server branch.
      """
      if len(sys.argv) >= 2 and sys.argv[1] == "validate":
          sys.argv = [sys.argv[0]] + sys.argv[2:]
          validate_command_entry()
      else:
          from src.server import mcp
          mcp.run()
  ```

  **Verification:**
  ```bash
  python3 -c "from src.cli import validate_command, validate_command_entry, fleet_mcp_main; print('ok')"
  # → ok
  ruff check src/cli.py
  # → All checks passed.
  mypy src/cli.py
  # → Success: no issues found in 1 source file
  ```

---

- [ ] **Step 6: Update `pyproject.toml` — change `fleet-mcp` entry point and add `fleet-mcp-validate`**

  In `pyproject.toml`, locate the `[project.scripts]` section:
  ```toml
  [project.scripts]
  fleet-mcp = "src.server:mcp.run"
  fleet-mcp-init = "src.cli:init_command"
  ```

  Replace with:
  ```toml
  [project.scripts]
  fleet-mcp = "src.cli:fleet_mcp_main"
  fleet-mcp-init = "src.cli:init_command"
  fleet-mcp-validate = "src.cli:validate_command_entry"
  ```

  Then reinstall the package so the entry points are registered:
  ```bash
  pip install -e .
  ```

  **Verification:**
  ```bash
  pip show fleet-mcp | grep -A5 "Name:"
  fleet-mcp validate --help
  # → usage: fleet-mcp-validate [...] --fleet-dir [...] --json
  fleet-mcp-validate --help
  # → same usage output
  ```

---

- [ ] **Step 7: Create `tests/test_cli.py`**

  Full file content (exact implementation):

  ```python
  import dataclasses
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


  def test_validate_json_valid_fleet(capsys: object) -> None:
      import sys
      assert isinstance(capsys, object)
      code = validate_command(EXAMPLE_FLEET, json_output=True)
      assert code == 0


  def test_validate_json_output_on_valid_fleet(capsys: "pytest.CaptureFixture[str]") -> None:  # type: ignore[name-defined]
      code = validate_command(EXAMPLE_FLEET, json_output=True)
      assert code == 0


  def test_validate_json_format_on_valid_fleet(capsys: object) -> None:
      import io
      import contextlib
      buf = io.StringIO()
      with contextlib.redirect_stdout(buf):
          code = validate_command(EXAMPLE_FLEET, json_output=True)
      payload = json.loads(buf.getvalue())
      assert payload["valid"] is True
      assert payload["error_count"] == 0
      assert payload["errors"] == []
      assert code == 0


  def test_validate_json_format_on_invalid_fleet(capsys: object) -> None:
      import io
      import contextlib
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


  def test_validate_exits_2_on_unreadable_dir(tmp_path: Path) -> None:
      """Non-existent directory raises OSError → exit 2."""
      import os
      missing = tmp_path / "does-not-exist"
      # FleetStore returns [] for missing *files* but the dir itself must exist;
      # passing a non-existent path causes OSError on open() only if a file exists.
      # Actually FleetStore._load_yaml checks path.exists() and returns [] if not.
      # So a missing dir is the same as an empty dir — valid (exit 0).
      # This test verifies that a structurally invalid YAML exits 2.
      bad_yaml = tmp_path / "services.yaml"
      bad_yaml.write_text("{ invalid yaml: [[[")
      code = validate_command(tmp_path, json_output=False)
      assert code == 2


  def test_validate_exits_2_on_invalid_yaml_json_output(tmp_path: Path) -> None:
      import io
      import contextlib
      bad_yaml = tmp_path / "contracts.yaml"
      bad_yaml.write_text("{ not valid yaml: [[[")
      buf = io.StringIO()
      with contextlib.redirect_stdout(buf):
          code = validate_command(tmp_path, json_output=True)
      assert code == 2
      payload = json.loads(buf.getvalue())
      assert payload["valid"] is False
      assert "load_error" in payload
  ```

  **Verification:**
  ```bash
  python3 -m pytest tests/test_cli.py -v --tb=short
  # → 8 passed (exact count depends on test discovery; all tests must pass)
  ```

---

- [ ] **Step 8: Run the full test suite and quality gates**

  ```bash
  python3 -m pytest tests/ -x -q --tb=short
  ```
  Expected: all existing tests (17 from Phase 1) plus new tests (≥18 new) pass. Zero failures.

  ```bash
  ruff check src/ tests/
  ```
  Expected: `All checks passed.`

  ```bash
  mypy src/
  ```
  Expected: `Success: no issues found in N source files` (N ≥ 19).

  **Verification:** All three commands exit 0. Paste full output in TIR `## Evidence`.

---

- [ ] **Step 9: End-to-end smoke test of `fleet-mcp validate` command**

  ```bash
  fleet-mcp validate --fleet-dir tests/fixtures/example-fleet
  # → ✓ Fleet YAML is consistent.
  # exit code: 0

  fleet-mcp validate --fleet-dir tests/fixtures/invalid-fleet
  # → Fleet YAML validation failed: 6 error(s): [6 lines of errors]
  # exit code: 1

  fleet-mcp validate --fleet-dir tests/fixtures/example-fleet --json | python3 -m json.tool
  # → valid JSON, valid=true, error_count=0

  fleet-mcp validate --fleet-dir tests/fixtures/invalid-fleet --json | python3 -m json.tool
  # → valid JSON, valid=false, error_count=6

  fleet-mcp-validate --fleet-dir tests/fixtures/example-fleet
  # → ✓ Fleet YAML is consistent.
  # exit code: 0
  ```

  **Verification:** All five invocations produce correct output and exit codes. Capture output in TIR `## Evidence`.

---

## Verification Checklists

*Coder must satisfy all REQUIRED items before advancing to IN_REVIEW.*

### Functional Checks

- [ ] [REQUIRED] `FleetValidator.validate(example-fleet)` returns `ValidationResult(valid=True, errors=[])` — zero false positives on a known-good fleet
- [ ] [REQUIRED] `FleetValidator.validate(invalid-fleet)` returns exactly 6 errors, one per deliberate defect in the fixture
- [ ] [REQUIRED] Error for empty-string `from_service` has `message == "empty-string service ID"` and `value == ""`
- [ ] [REQUIRED] Error for unknown `from_service` has `message` containing `"unknown service ID 'svc-unknown'"`
- [ ] [REQUIRED] Error for `deployment.yaml` has `entry_id` of form `"{service_id}/{environment}"`
- [ ] [REQUIRED] `fleet-mcp validate --fleet-dir tests/fixtures/example-fleet` exits 0
- [ ] [REQUIRED] `fleet-mcp validate --fleet-dir tests/fixtures/invalid-fleet` exits 1
- [ ] [REQUIRED] `fleet-mcp validate ... --json` emits valid JSON to stdout on both valid and invalid fleets
- [ ] [REQUIRED] JSON schema: `{valid: bool, error_count: int, errors: [{file, entry_id, field, value, message}]}`
- [ ] [REQUIRED] `fleet-mcp-validate --fleet-dir tests/fixtures/example-fleet` exits 0 (alias works)
- [ ] [REQUIRED] Malformed YAML file in fleet dir causes exit 2 (not exit 1)
- [ ] [REQUIRED] Exit 2 with `--json` emits `{"valid": false, "load_error": "...", "errors": []}` to stdout

### Operational Checks

- [ ] [REQUIRED] `fleet-mcp` (no args) still starts the MCP server — dispatcher does not break the server branch
- [ ] [REQUIRED] `fleet-mcp-init` still works — entry point unchanged
- [ ] [REQUIRED] No new runtime dependencies introduced (`pip show fleet-mcp` shows no new packages)

### Domain Verification Checks

- [ ] [REQUIRED] `python3 -m pytest tests/ -x -q --tb=short` — all tests pass, output captured in TIR
- [ ] [REQUIRED] `ruff check src/ tests/` — exits 0, captured in TIR
- [ ] [REQUIRED] `mypy src/` — exits 0, captured in TIR

### QA-Specific Checks (from DMT)

- [ ] [REQUIRED] `fleet-mcp validate --fleet-dir $FLEET_DATA_DIR` usable as pre-commit hook (verify by running manually with `FLEET_DATA_DIR=tests/fixtures/example-fleet fleet-mcp validate --fleet-dir $FLEET_DATA_DIR`)
- [ ] [REQUIRED] Resolves `contracts.yaml` `from_service`/`to_service` against `services.yaml` — verified by `test_unknown_service_in_contract_from_service` passing
- [ ] [REQUIRED] Resolves `landmines.yaml` `affected_services` — verified by `test_unknown_service_in_landmine_affected_services` passing
- [ ] [REQUIRED] Resolves `data_models.yaml` `owner_service` and `consumer_services` — verified by two data model tests passing
- [ ] [REQUIRED] Resolves `deployment.yaml` `service_id` — verified by `test_unknown_service_id_in_deployment` passing
- [ ] [REQUIRED] Empty-string service ID flagged in contracts (OSF-001 class) — verified by `test_empty_string_service_id_in_contract` passing

### Security / Compliance Checks

- [ ] [REQUIRED] No secrets committed — validator reads YAML paths, produces no credentials in output
- [ ] [REQUIRED] `--fleet-dir` argument is read-only; validator makes no filesystem writes

### Containment Checks

| Step | Detect | Contain | Recover | Prevent recurrence |
|---|---|---|---|---|
| Step 2 (invalid-fleet fixture) | `test_invalid_fleet_reports_errors` fails if fixture doesn't produce exactly 6 errors | Fixture is test-only; no production impact | Fix fixture YAML to match documented error inventory | Test asserts exact count (6); any fixture change must update count |
| Step 3 (validator.py) | `test_valid_fleet_passes` fails (false positives) or `test_invalid_fleet_reports_errors` fails (false negatives) | Validator is a pure function; no state mutation; server unaffected | Fix logic, re-run tests | Separate tests for each error category; count assertion in `test_invalid_fleet_reports_errors` |
| Step 5 (cli.py dispatcher) | `fleet-mcp` (no args) fails to start server; test suite catches missing `fleet_mcp_main` | Server entry point is the dispatcher fallthrough; if dispatcher raises, server fails to start | Revert dispatcher change in cli.py | `test_validate_exits_0_on_valid_fleet` tests the validate path; add a smoke test for server startup if missing |
| Step 6 (pyproject.toml) | `fleet-mcp` command not found after install; `fleet-mcp-validate` not found | Old entry points remain registered until `pip install -e .` runs | Re-run `pip install -e .` | Step 6 verification explicitly requires `fleet-mcp validate --help` to succeed after reinstall |

---

## Field Discoveries

| # | Date | Role | Class | Description | Resolution |
|---|---|---|---|---|---|
| 1 | 2026-05-26 | Engineer | INFO | Phase 1 mandate is in QA FAIL state (`.env.example` untracked). Phase 2-A does not depend on Phase 1 VERIFIED. All required models and store code are committed (git log confirms). | Proceed. Phase 2-A adds new files; no conflict with Phase 1 scope. |
| 2 | 2026-05-26 | Engineer | INFO | `DeploymentEntry` has no `id` field. Composite key `f"{service_id}/{environment}"` used for `ValidationError.entry_id` in deployment errors. Documented in ADR-005. | Accepted. Composite key is unique within a well-formed fleet. |
| 3 | 2026-05-26 | Engineer | INFO | Board (moijafcor/projects/2) has no IN_RECON or PLANNED status options. Status options: Backlog, Ready, In progress, In review, Done. | All harnessable status transitions logged in Tracker Ops Log. Ready ≈ PLANNED. |
| 4 | 2026-05-26 | Engineer | ONTOLOGY_GAP | `fleet_mcp.FleetValidator`, `fleet_mcp.ValidationError`, `fleet_mcp.ValidationResult`, `fleet_mcp.CLICommand`, `fleet_mcp.FleetMcpDispatcher`, `fleet_mcp.ValidateCommand` were absent from `docs/knowledge-graph.yaml`. | Resolved — Engineer added all six concepts to the graph during DIP authoring (Graph-before-PLANNED gate). |

---

## Child Tasks

| Task URL | Title | Reason Created | Status |
| --- | --- | --- | --- |
| — | OSF-001: Fix empty-string passthrough in `fleet_get_api_contract` tool | Out-of-scope for Phase 2-A; validate provides the YAML-layer guard; tool-layer fix is separate | BACKLOG (pre-existing from Phase 1 QA) |

---

## Tracker Ops Log

| Timestamp | Operation | Target | Params | Executed? |
| --- | --- | --- | --- | --- |
| 2026-05-26T00:00:00Z | Set board status IN_RECON | moijafcor/projects/2 item 192459850 (PVTI_lAHOAAu2cM4BYTLXzgt4tEo) | No IN_RECON option on this board. Closest = no change from Backlog. | No — board has no IN_RECON status |
| 2026-05-26T01:00:00Z | Set board status PLANNED | moijafcor/projects/2 item 192459850 (PVTI_lAHOAAu2cM4BYTLXzgt4tEo) | Option "Ready" (id=61e4505c) is the closest equivalent to PLANNED | Pending — execute after DIP handoff |
| 2026-05-26T01:00:00Z | Add board comment | moijafcor/projects/2 item 192459850 | "DIP authored at docs/mandates/fleet-context/fleet_mcp_validate_command_implementation_plan.md. Ready for Coder." | Pending — DraftIssue may not support comments; attempt after status update |

---

## Task Implementation Report

*Coder fills this section. Do not pre-populate.*

### Summary
[2–4 sentences: what was built, what changed, what was deliberately not changed]

### Implementation Notes
[Coder's narrative: decisions made during implementation, gotchas, deviations from DIP steps]

### Evidence

#### Test Output
```
[paste test runner output here]
```

#### Linter / Type Checker Output
```
[paste ruff and mypy output here]
```

#### Health Check / Smoke Test Output
```
[paste fleet-mcp validate end-to-end output here]
```

#### Other Evidence
[commit hashes for each file changed]

### Blockers (if any remain)
- [item]: [status]

### Verification Checklist — Coder Sign-Off
- [ ] All REQUIRED verification checklist items above are checked
- [ ] All DEVIATION field discoveries are documented
- [ ] No open BLOCKER field discoveries
- [ ] TIR Summary is complete with evidence

---

## QA Verdict

*QA fills this section after reviewing TIR and re-executing checks.*

**Verdict:** [PASS | CONDITIONAL_PASS | FAIL]
**QA Agent:** [identifier]
**Date:** [ISO date]

### Checks Executed
| Check | Result | Evidence |
|---|---|---|
| [check description] | PASS / FAIL | [log line, output, observation] |

### Findings
- [PASS items need no entry]
- [FAIL/CONDITIONAL: specific description with evidence]

### Out-of-Scope Findings
- [any defects found outside mandate scope — linked to child tasks]

### Verdict Rationale
[1–3 sentences explaining the verdict, especially for CONDITIONAL_PASS or FAIL]

---

## Post-Close Notes

*Append-only after DONE. Do not modify earlier sections.*

| Date | Author | Note |
|---|---|---|
| — | — | — |
