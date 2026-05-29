# Design Implementation Plan

<!-- HEADER — fill before saving -->
**DMT:** [URL to board task | path to local DMT file | (inline — no persistent source)]
**Title:** [Exact title from DMT]
**Slug:** [filename slug used for this file]
**Bucket:** [new | existing]
**Engineer:** [agent session / human identifier]
**DIP Created:** [ISO date]
**DIP Last Updated:** [ISO date]
**Board Status:** [current status | N/A — no board item]
**Board Status History:**
<!-- Board-tracked mandates start with MANDATED.
     Locally-authored mandates start with IN_RECON (first DIP-authoring session). -->

- [ISO datetime] [MANDATED — Architect created DMT | IN_RECON — local DMT, no board item]
- [ISO datetime] IN_RECON — Engineer session started

---

## Mandate Reference

**Architect's Intent (summary):**
> [2–4 sentence distillation of what the Architect wants achieved and why]

**DMT Acceptance Criteria (copied from issue):**

- [ ] [criterion 1]
- [ ] [criterion 2]

**Constraints (from DMT):**

- [tech constraint, compat requirement, time box, compliance requirement]

**Explicitly Out of Scope (from DMT):**

- [item 1]

---

## Scope

**In Scope:**

- [specific deliverable 1]
- [specific deliverable 2]

**Out of Scope (Engineer-added, beyond DMT):**

- [item discovered during recon that could be misread as in-scope]

**Scope Risk:**

- [anything that could expand unexpectedly during implementation]

---

## Recon Findings

*Engineer documents everything discovered during the investigation pass.*

### Codebase / Infrastructure State

- [file/module/component]: [relevant finding]

### Related Prior Mandates

- [path/to/prior_dip.md]: [how it relates]

### External Dependencies

- [API / SDK / service]: [version, status, relevant constraints]

### Relevant Memory / Session Context

- [summary of past session findings relevant to this mandate]

### Open Questions (pre-DIP; must be resolved before PLANNED)

- [ ] [question 1 — tag with @Architect if needs their input]
- [ ] [question 2]

---

## Architecture Decisions

*One entry per non-obvious choice. Format: decision → rationale → alternatives considered.*

### ADR-001: [Decision Title]

**Decision:** [What was decided]
**Rationale:** [Why this approach over alternatives]
**Alternatives Considered:** [What else was evaluated and why rejected]
**Consequences:** [What this decision locks in or forecloses]

---

## Implementation Steps

*Ordered. Each step must be independently verifiable. Check off as completed.*

- [ ] **Step 1:** [action — specific enough that another agent could execute it]
  - Verification: [how to confirm this step is complete]
- [ ] **Step 2:** [action]
  - Verification: [how to confirm]
- [ ] **Step 3:** [action]
  - Verification: [how to confirm]

<!-- DEVIATION notes go inline with affected steps:
[DEVIATION 001] Original: X. Actual: Y. Reason: Z. See Field Discoveries.
-->

---

## Rollback Procedure

*Required for all SRE mandates. Recommended for code mandates with destructive steps.*
*SRE entry gate: if this section is absent, SRE must file BLOCKER before proceeding.*

[Step-by-step instructions to return all affected systems to their pre-change state.
Include: exact commands, expected verification output after rollback, and any steps
that cannot be reversed (declare explicitly).]

---

## Instrumentation

*Engineer declares during DIP authoring. Coder implements.
QA verifies in Phase 4. Reviewer audits in Pass 4.
Inspector verifies in Pass 6.*

### Structural logs

What must this implementation log, at what level, and with what
context fields?

| Event | Level | Context fields required |
| --- | --- | --- |
| [error condition] | ERROR | [fields] |
| [state transition] | INFO | [fields] |

### Distributed traces

Does this implementation participate in distributed tracing?

- Trace propagation: [yes / no — if yes, which headers?]
- New spans created: [list]

### Operational telemetry

What metrics must this implementation emit?

| Metric | Type | Unit | Labels |
| --- | --- | --- | --- |
| [name] | counter/gauge/histogram | [unit] | [labels] |

### Business instrumentation

What business events must this implementation emit?

| Event name | Trigger | Required properties |
| --- | --- | --- |
| [event] | [when fired] | [properties] |

If this mandate introduces no instrumentation requirements:
state "None — this mandate does not introduce observable events."
Do not leave this section blank.

---

## Verification Checklists

*Coder or SRE must satisfy all REQUIRED items before advancing to IN_REVIEW.*
*QA uses these as the primary test matrix.*

### Functional Checks

- [ ] [REQUIRED] [specific behaviour assertion]
- [ ] [REQUIRED] [specific behaviour assertion]
- [ ] [OPTIONAL] [nice-to-have assertion]

### Operational Checks

- [ ] [REQUIRED] No new errors or anomalies after execution
- [ ] [REQUIRED] [health probe / smoke check passes]
- [ ] [REQUIRED] [relevant metric or signal within acceptable range]

### Domain Verification Checks

- [ ] [REQUIRED] [primary verification command passes] (`[command]`) — output captured in report
- [ ] [REQUIRED] [secondary check passes] (`[command]`)
- [ ] [REQUIRED] [domain-specific validator passes] (`[command]`)

### QA-Specific Checks (from DMT)

- [ ] [REQUIRED] [acceptance criterion mapped to a specific verification action]
- [ ] [REQUIRED] [acceptance criterion mapped to a specific verification action]

### Security / Compliance Checks (if applicable)

- [ ] [REQUIRED] No secrets committed
- [ ] [REQUIRED] [auth/authz behaviour verified]

### Containment Checks

*Engineer fills during DIP authoring. For each non-trivial implementation step:*

| Step | Detect | Contain | Recover | Prevent recurrence |
| --- | --- | --- | --- | --- |
| Step N | [how failure surfaces] | [blast radius limiter] | [rollback path] | [future control] |

---

## Field Discoveries

*Initially empty. Filled during Engineer recon and Coder/SRE implementation.*
*Each entry: classification (INFO / DEVIATION / BLOCKER / HARNESS_IMPROVEMENT), date, description, resolution.*

| # | Date | Role | Class | Description | Resolution |
| --- | --- | --- | --- | --- | --- |
| — | — | — | — | *none yet* | — |

*HARNESS_IMPROVEMENT entries must also generate a child task — see `vendor/harnessable/references/continuous-improvement.md`.*

---

## Child Tasks

*Initially empty. Filled as child/root tasks are created.*

| Task URL | Title | Reason Created | Status |
| --- | --- | --- | --- |
| — | — | — | — |

---

## Tracker Ops Log

*Record intended tracker operations here when the integration is unavailable. Execute retroactively.*

| Timestamp | Operation | Target | Params | Executed? |
| --- | --- | --- | --- | --- |
| — | — | — | — | — |

---

## Task Implementation Report

*Coder fills this section for **code mandates**. Do not pre-populate.*
*For infrastructure mandates, use **SRE Implementation Report** below instead.*

### Summary

[2–4 sentences: what was built, what changed, what was deliberately not changed]

### Implementation Notes

[Coder's narrative: decisions made during implementation, gotchas, deviations from DIP steps]

### Evidence

#### Test Output

```text
[paste test runner output here]
```

#### Linter / Type Checker Output

```text
[paste output here]
```

#### Health Check / Smoke Test Output

```text
[paste output here]
```

#### Other Evidence

[links to logs, metrics, screenshots, or commit hashes]

### Blockers (if any remain)

- [item]: [status]

### Verification Checklist — Coder Sign-Off

- [ ] All REQUIRED verification checklist items above are checked
- [ ] All DEVIATION field discoveries are documented
- [ ] No open BLOCKER field discoveries
- [ ] TIR Summary is complete with evidence

---

## SRE Implementation Report

*SRE fills this section for **infrastructure mandates**. Do not pre-populate.*
*For code mandates, use **Task Implementation Report** above instead.*

### Summary

[2–4 sentences: what changed, what systems were touched, current health status]

### Pre-Change Baseline

[Actual command output from Step 0 captured before any system was touched]

```text
[paste health check and state capture output here]
```

### Change Execution Log

[Step-by-step: exact commands run and their actual output, in sequence, pasted in real time]

```text
[paste command output here — do not reconstruct from memory]
```

### Incident Notes

[If any: what went wrong, what the decision was (roll forward / roll back), what action was
taken, and what the outcome was. Leave blank if no incident occurred.]

### Observation Window

[Log lines and metric readings from Phase 3. Timestamp range covered. Explicit "no anomalies
observed" if the window was clean.]

```text
[paste relevant log lines and metric readings here]
```

### Rollback Status

[One of: **still viable** / **not viable** — [reason] / **was executed** — [outcome]]

### Verification Checklist — SRE Sign-Off

- [ ] All REQUIRED verification checklist items above are checked
- [ ] Pre-Change Baseline captured with actual output
- [ ] All change steps logged with actual command output
- [ ] Observation window completed and minimum duration met
- [ ] Rollback viability confirmed and status recorded
- [ ] All DEVIATION field discoveries are documented
- [ ] No open BLOCKER field discoveries
- [ ] All IaC changes committed before they were applied
- [ ] `git status` clean in all touched repositories

---

## QA Verdict

*QA fills this section after reviewing TIR or SIR and re-executing checks.*

**Verdict:** [PASS | CONDITIONAL_PASS | FAIL]
**QA Agent:** [identifier]
**Date:** [ISO date]

### Checks Executed

| Check | Result | Evidence |
| --- | --- | --- |
| [check description] | PASS / FAIL | [log line, output, observation] |

### Findings

- [PASS items need no entry]
- [FAIL/CONDITIONAL: specific description with evidence]

### Out-of-Scope Findings

- [any defects found outside mandate scope — linked to child tasks]

### Verdict Rationale

[1–3 sentences explaining the verdict, especially for CONDITIONAL_PASS or FAIL]

---

## Security Review Report

*Security fills this section only when the Architect flagged the mandate for Security review.*
*Leave this section absent if Security review was not required.*

**Verdict:** [SECURE_PASS | CONDITIONAL_PASS | FAIL]
**Security Agent:** [identifier]
**Date:** [ISO date]

### Threat Surface Map

[Phase 1 output: what new inputs and outputs does this change introduce, what trust
boundaries does it cross, and what assumptions about callers could a motivated adversary
violate? This section must be complete before any technical checks begin.]

### Security Findings

| ID | Phase | Severity | Description | Evidence | Remediation |
| --- | --- | --- | --- | --- | --- |
| — | — | — | *none* | — | — |

### Child Tasks Created

- [MEDIUM, LOW, and INFO findings require child tasks before SECURE_PASS or CONDITIONAL_PASS]

### Framework Observation

[Phase 8 output — gap filed as HARNESS_IMPROVEMENT, or "no gaps identified this session"]

### Security Verdict Rationale

[1–3 sentences explaining the verdict]

---

## Post-Close Notes

*Append-only after DONE. Do not modify earlier sections.*

| Date | Author | Note |
| --- | --- | --- |
| — | — | — |
