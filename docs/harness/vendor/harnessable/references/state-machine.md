# Board State Machine

## Status Definitions

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `BACKLOG` | Not yet actionable; awaiting Architect prioritization | Architect / any (for child tasks) |
| `MANDATED` | DMT is complete and approved for execution | Architect |
| `IN_RECON` | Engineer is running discovery and recon passes | Engineer |
| `PLANNED` | DIP is complete; ready for Coder or SRE | Engineer |
| `IN_PROGRESS` | Coder or SRE is actively implementing | Coder / SRE |
| `IN_REVIEW` | Implementation complete; awaiting QA | Coder / SRE |
| `BLOCKED` | Work halted; requires Architect or external resolution | Any |
| `NEEDS_REVISION` | QA verdict was FAIL; Coder or SRE must address findings | QA |
| `VERIFIED` | QA verdict was PASS or CONDITIONAL_PASS; Security review (if required) completed | QA / Security |
| `DONE` | Architect accepted verdict; mandate closed | Architect |

---

## Legal Transitions

```text
BACKLOG         → MANDATED         (Architect prioritises)
MANDATED        → IN_RECON         (Engineer begins recon)
IN_RECON        → PLANNED          (Engineer completes DIP)
IN_RECON        → BLOCKED          (Architect input required before plan can be written)
PLANNED         → IN_PROGRESS      (Coder or SRE begins implementation)
PLANNED         → IN_RECON         (Engineer must revise DIP — e.g., scope clarification needed)
IN_PROGRESS     → IN_REVIEW        (Coder or SRE complete, all gates passed)
IN_PROGRESS     → BLOCKED          (Blocker field discovery; child task created)
IN_REVIEW       → VERIFIED         (QA: PASS or CONDITIONAL_PASS)
IN_REVIEW       → NEEDS_REVISION   (QA: FAIL)
NEEDS_REVISION  → IN_PROGRESS      (Coder or SRE resumes after addressing QA findings)
NEEDS_REVISION  → IN_RECON         (Findings require DIP revision before reimplementation)
BLOCKED         → [prior status]   (Blocker resolved; Architect unblocks)
VERIFIED        → NEEDS_REVISION   (Security: FAIL — mandate flagged for Security review)
VERIFIED        → DONE             (Architect accepts; Security SECURE_PASS or CONDITIONAL_PASS
                                    required first when mandate is flagged for Security review)
VERIFIED        → NEEDS_REVISION   (Architect rejects despite QA pass — rare)
```

## Illegal Transitions (invariants)

These must never occur. If an agent is tempted to make one, stop and raise a BLOCKER.

```text
MANDATED        → IN_PROGRESS      (no DIP = no implementation)
MANDATED        → DONE             (skipping all execution)
PLANNED         → IN_REVIEW        (no TIR or SIR = no QA)
PLANNED         → VERIFIED         (skipping implementation and QA)
IN_PROGRESS     → DONE             (skipping QA)
IN_PROGRESS     → VERIFIED         (self-QA is prohibited)
ANY             → DONE             (only Architect closes)
```

---

## Local Track (no board item)

A mandate sourced from a local file or inline description has no `BACKLOG` or `MANDATED` state. The first state in the mandate lifecycle is `IN_RECON`.

`AUTHORED` is a logical marker — **not a board status**. It names the entry condition: a local DMT file exists or an inline description was given. It does not appear on the board and must not be used as a board status.

```text
LOCAL TRACK (no board item)

AUTHORED  →  IN_RECON     (Engineer reads local DMT; begins recon — board step skipped)
IN_RECON  →  PLANNED      (DIP complete; board update skipped or recorded in Tracker Ops Log)
PLANNED   →  IN_PROGRESS  (Coder or SRE begins; from here, standard track applies)
```

---

## State Invariants

These conditions must hold at all times:

1. **DIP-before-code:** A DMT in `IN_PROGRESS` or later MUST have a corresponding DIP file.
2. **Report-before-QA:** A DMT in `IN_REVIEW` MUST have a `## Task Implementation Report` section in its DIP (code mandates) or a `## SRE Implementation Report` section (infrastructure mandates).
3. **No self-QA:** The agent that set status to `IN_REVIEW` must not also set `VERIFIED`.
4. **BLOCKER accountability:** A DMT in `BLOCKED` must have a child task or DIP entry explaining the reason.
5. **Gate enforcement:** Transition to `IN_REVIEW` requires all DIP verification checklist items checked.
6. **Closed mandates are immutable:** A DMT in `DONE` must not have its DIP modified (append-only via `## Post-Close Notes`).
7. **Local track quality gates:** A mandate on the local track must still satisfy DIP-before-code and Report-before-QA invariants. The absence of a board item does not relax any quality gate.
8. **Graph-before-PLANNED:** All concepts introduced in the DIP must exist in `docs/knowledge-graph.yaml`. DIP concepts that cannot be resolved to a namespaced graph entry block the PLANNED transition.
9. **Graph-before-DONE:** The Architect must confirm the knowledge graph was enriched with all concepts surfaced during this mandate before setting DONE. Unresolved `ONTOLOGY_GAP` discoveries block the DONE transition.
10. **Security-gate-before-DONE:** A mandate with `security_review_required: true` in the DMT cannot transition to DONE without a Security Review Report carrying `SECURE_PASS` or `CONDITIONAL_PASS`. A Security `FAIL` moves the mandate to `NEEDS_REVISION` regardless of QA verdict.
11. **Git-clean-before-IN_REVIEW:** The working directory must be clean in every codebase touched by the mandate (`git status` shows nothing to commit) before transitioning to `IN_REVIEW`. All mandate work must be committed with accurate commit messages. No staged or unstaged changes may remain. Cross-codebase mandates must have at least one commit per codebase. For SRE mandates, all IaC changes must have been committed before they were applied. A Coder or SRE who sets `IN_REVIEW` with uncommitted changes has not completed the mandate. QA must run `git status` and `git log` as part of verification.

---

## State Diagram (ASCII)

```text
  ╔══════════╗    ┌──────────┐
  ║ AUTHORED ║    │ BACKLOG  │
  ║(no board)║    └────┬─────┘
  ╚═════╤════╝         │ Architect
        │         ┌────▼─────┐
        │         │ MANDATED │
        │         └────┬─────┘
        │ Engineer      │ Engineer
        │ reads         │
        └─ ─ ─ ─ ─►┌────▼───────┐
              ┌─────│  IN_RECON  │◄─────────────────┐
              │     └─────┬──────┘                  │
              │           │ Engineer (DIP complete)  │
              │     ┌─────▼──────┐                  │
              │     │  PLANNED   │──────────────────►│ (revision needed)
              │     └─────┬──────┘
              │           │ Coder / SRE
              │    ┌──────▼───────┐
              │ ┌──│ IN_PROGRESS  │◄─────────────────┐
              │ │  └──────┬───────┘                  │
              │ │         │ Coder / SRE (all gates pass)
              │ │  ┌──────▼───────┐                  │
              │ │  │  IN_REVIEW   │                  │
              │ │  └──┬──────┬────┘                  │
              │ │PASS │      │ FAIL                  │
              │ │┌────▼──┐ ┌─▼────────────┐          │
              │ ││VERIF. │ │NEEDS_REVISION│──────────┘
              │ │└───┬───┘ └─────────────┘
              │ │    │ Architect
              │ │┌───▼───┐
              │ ││ DONE  │
              │ │└───────┘
              │ │
              └─┴──►BLOCKED◄──── (any state, any role)
                        │
                        └────────► [prior status] (Architect unblocks)

  ╔═══════════════════════════════════════════════════════════╗
  ║ AUTHORED: logical marker only — not a board status.       ║
  ║ Dashed line (─ ─ ►) = local track path (no board ops).   ║
  ╚═══════════════════════════════════════════════════════════╝
```
