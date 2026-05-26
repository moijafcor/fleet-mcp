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

## Verification Checklists

*Coder must satisfy all REQUIRED items before advancing to IN_REVIEW.*
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
- [ ] [REQUIRED] [primary verification command passes] (`[command]`) — output captured in TIR
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
|---|---|---|---|---|
| Step N | [how failure surfaces] | [blast radius limiter] | [rollback path] | [future control] |

---

## Field Discoveries

*Initially empty. Filled during Engineer recon and Coder implementation.*
*Each entry: classification (INFO / DEVIATION / BLOCKER / HARNESS_IMPROVEMENT), date, description, resolution.*

| # | Date | Role | Class | Description | Resolution |
|---|---|---|---|---|---|
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
[paste output here]
```

#### Health Check / Smoke Test Output
```
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
