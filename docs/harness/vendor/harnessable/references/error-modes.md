# Expected Error Modes

Every error mode has a classification, a trigger condition, the expected agent
response, and the board status outcome.

---

## Class A — Mandate Quality Errors
*Problems originating in the DMT itself. Architect must resolve.*

### A1: Ambiguous Acceptance Criteria
**Trigger:** Engineer cannot write a verifiable DIP verification checklist because
the DMT's success criteria are subjective or unmeasurable.
**Response:** Engineer documents specific ambiguities in DIP `## Open Questions`,
sets board to `BLOCKED`, creates child task `[CLARIFICATION] {DMT title} — acceptance criteria`.
**Board:** `IN_RECON → BLOCKED`

### A2: Scope Entanglement
**Trigger:** DMT scope overlaps with an existing `IN_PROGRESS` or `PLANNED` mandate,
creating a conflict risk.
**Response:** Engineer flags in DIP `## Field Discoveries` as `BLOCKER`, lists the
conflicting mandates, proposes scope surgery. Architect decides which mandate owns
the contested territory.
**Board:** `IN_RECON → BLOCKED`

### A3: Missing Prerequisites
**Trigger:** DMT depends on infrastructure, schema, credentials, or prior work
that doesn't exist yet.
**Response:** Engineer creates prerequisite child tasks, marks them as
dependencies in DIP `## Implementation Steps`. If critical path: `BLOCKED`.
If can work around: `DEVIATION` field discovery, proceed.
**Board:** `IN_RECON → BLOCKED` or continue with `DEVIATION` logged.

---

## Class B — Recon Errors
*Problems found during Engineer's discovery pass.*

### B1: Codebase Diverged from Assumption
**Trigger:** Actual code structure, schema, or config differs significantly from
what the DMT assumed (common after a prior mandate changed things).
**Response:** `DEVIATION` field discovery. Update DIP architecture decisions.
If deviation invalidates the entire approach: `BLOCKER`, notify Architect.
**Board:** Continue in `IN_RECON`; BLOCKER if approach invalidated.

### B2: Missing Documentation / Dark Knowledge
**Trigger:** Key decisions are embedded in undocumented code, making recon incomplete.
**Response:** Document the dark knowledge in DIP `## Recon Findings`. Create
child task `[TECH_DEBT] Document {component}`. Proceed with best available understanding,
note uncertainty level in `## Architecture Decisions`.
**Board:** Continue; child task `BACKLOG`.

### B3: Tracker Integration Unavailable During Recon
**Trigger:** The project tracker integration (MCP, API, or other) is unreachable; cannot fetch DMT or update board.
**Response:** If the DMT was provided in session: proceed with the local copy.
Log all intended tracker operations in DIP `## Tracker Ops Log`. Execute retroactively when the integration restores.
**Board:** Intended status transition logged; actual transition deferred.

### B4: DMT Was Never Created
**Trigger:** Engineer begins a session and no DMT exists in the tracker for the described work, even though the tracker is reachable. The mandate was delivered conversationally (chat message, meeting note, or verbal instruction) without being formalized as a tracker task.
**Response:** Engineer creates the DMT retroactively from the conversational mandate description before setting board status to `IN_RECON`. All tracker operations that would have referenced the DMT are logged in DIP `## Tracker Ops Log` and executed after DMT creation. The DIP header marks the DMT field as `(Conversational mandate — DMT created retroactively)`.
**Board:** Set to `IN_RECON` only after the DMT exists in the tracker.

---

## Class C — Implementation Errors
*Problems that emerge during Coder's execution.*

### C1: DIP Step Is Unimplementable As Written
**Trigger:** A DIP step assumes a capability, API surface, or configuration
that doesn't work as described.
**Response:** `DEVIATION` field discovery with specific failure details.
Do not modify DIP steps directly — append `[DEVIATION]` note inline.
Implement the closest valid equivalent. If no valid equivalent exists: `BLOCKER`.
**Board:** Continue in `IN_PROGRESS`; BLOCKER if no path forward.

### C2: Verification Gate Failure
**Trigger:** A DIP verification checklist item fails (a domain check, validation step, health probe, or completion gate command exits non-zero).
**Response:** Do not advance board. Document failure in TIR `## Blockers`.
Diagnose and fix within mandate scope. If fix requires scope expansion:
`DEVIATION` or new child task.
**Board:** Remain `IN_PROGRESS`.

### C3: Unintended Side Effect Discovered
**Trigger:** Implementation change causes unexpected behaviour in an unrelated component.
**Response:** Stop. Assess severity:
- Minor (no functional regression): log in TIR, create `[TECH_DEBT]` child task.
- Significant (functional regression): roll back the specific change, file `BLOCKER`.
**Board:** `IN_PROGRESS → BLOCKED` if significant regression.

### C4: Implementation Reveals Scope Expansion
**Trigger:** Doing the work correctly requires changes larger than the DIP describes.
**Response:** Do not silently expand scope. File `DEVIATION`, document the
discovered scope delta. If expansion is small and low-risk: proceed with Deviation logged.
If large: create child task for the expanded work, implement only original scope.
**Board:** Continue with logged DEVIATION; child task `BACKLOG`.

---

## Class D — QA Errors
*Problems found during verification.*

### D1: TIR Evidence Is Insufficient
**Trigger:** QA cannot verify a claim in the TIR because evidence (test output,
log snippet, screenshot, metric) is missing.
**Response:** QA files `FAIL` verdict with specific evidence gaps listed.
Do not guess or assume. Coder must supply missing evidence.
**Board:** `IN_REVIEW → NEEDS_REVISION`

### D2: Implementation Passes TIR Claims But Fails DMT Acceptance Criteria
**Trigger:** Coder implemented what the DIP said, but the DIP was under-specified
relative to what the Architect actually wanted.
**Response:** QA verdict `FAIL`. In verdict, distinguish clearly:
"Implementation matches DIP (Coder did their job) but DIP did not capture
Architect intent (Engineer error)." Create child task for DIP correction.
**Board:** `IN_REVIEW → NEEDS_REVISION`

### D3: Regression Found Outside Mandate Scope
**Trigger:** QA spot-check finds a defect in code/infra not touched by this mandate.
**Response:** Document in QA verdict as `OUT_OF_SCOPE_FINDING`. Create child task.
Do not fail the current mandate for it unless it's critical path for the feature.
**Board:** `VERIFIED` (with child task created) or `FAIL` if critical.

---

## Class E — Operational Errors
*Process and tooling failures.*

### E1: Board Status Gets Out of Sync
**Trigger:** Agent advanced work without updating the board (common when the tracker integration was unavailable).
**Response:** On the next session with integration access, reconstruct the correct current status from the DIP changelog. Execute all pending transitions in order.
Log reconciliation in DIP `## Tracker Ops Log`.

### E2: DIP File Missing at Coding Start
**Trigger:** Coder begins a session with a DMT in `IN_PROGRESS` but no DIP exists.
**Response:** Full stop. Set board to `BLOCKED`. Create child task for Engineer
to produce DIP retroactively. Do not proceed without it.
**Board:** `IN_PROGRESS → BLOCKED`

### E3: Role Collapse
**Trigger:** A single agent implements work AND issues the QA verdict.
**Response:** Flag in DIP as a process violation. Mark QA verdict as
`UNVERIFIED (self-review)`. Architect must conduct a manual review before
advancing to `DONE`.
**Board:** `VERIFIED` blocked until Architect signs off manually.

### E4: Child Task Orphaned
**Trigger:** A child task is created but not linked to the parent DMT or DIP.
**Response:** Any agent noticing an orphaned task should link it retroactively.
Add a row to the parent DIP `## Child Tasks` section.
