# Board State Machine

## Architecture Overview

The harnessable framework operates two distinct state machines on two separate
tracks. **Track 1 — Core Pipeline** is synchronous and gate-based: each role
blocks progression to the next stage until its artifact is complete and
accepted. **Track 2 — Quality Lifecycle** is asynchronous and
investment-based: the Reviewer and Inspector operate on a separate clock,
produce findings and child mandates rather than verdicts, and do not gate any
core pipeline stage in any status. See the [Track Interaction](#track-interaction)
section for how discoveries flow between tracks.

---

## Track 1 — Core Pipeline State Machine

### Status Definitions — Track 1 — Core Pipeline (synchronous, gate-based)

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

### Legal Transitions

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

### Illegal Transitions (invariants)

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

### Local Track (no board item)

A mandate sourced from a local file or inline description has no `BACKLOG` or `MANDATED` state. The first state in the mandate lifecycle is `IN_RECON`.

`AUTHORED` is a logical marker — **not a board status**. It names the entry condition: a local DMT file exists or an inline description was given. It does not appear on the board and must not be used as a board status.

```text
LOCAL TRACK (no board item)

AUTHORED  →  IN_RECON     (Engineer reads local DMT; begins recon — board step skipped)
IN_RECON  →  PLANNED      (DIP complete; board update skipped or recorded in Tracker Ops Log)
PLANNED   →  IN_PROGRESS  (Coder or SRE begins; from here, standard track applies)
```

### State Invariants

These conditions must hold at all times:

1. **DIP-before-code:** A DMT in `IN_PROGRESS` or later MUST have a corresponding DIP file.
2. **Report-before-QA:** A DMT in `IN_REVIEW` MUST have a `## Task Implementation Report` section in its DIP (code mandates) or a `## SRE Implementation Report` section (infrastructure mandates).
3. **No self-QA:** The agent that set status to `IN_REVIEW` must not also set `VERIFIED`.
4. **BLOCKER accountability:** A DMT in `BLOCKED` must have a child task or DIP entry explaining the reason.
5. **Gate enforcement:** Transition to `IN_REVIEW` requires all DIP verification checklist items checked. *(Applies to core pipeline mandates only — quality lifecycle mandates have no IN_REVIEW state; see Invariant 12.)*
6. **Closed mandates are immutable:** A DMT in `DONE` must not have its DIP modified (append-only via `## Post-Close Notes`).
7. **Local track quality gates:** A mandate on the local track must still satisfy DIP-before-code and Report-before-QA invariants. The absence of a board item does not relax any quality gate.
8. **Graph-before-PLANNED:** All concepts introduced in the DIP must exist in `docs/knowledge-graph.yaml`. DIP concepts that cannot be resolved to a namespaced graph entry block the PLANNED transition.
9. **Graph-before-DONE:** The Architect must confirm the knowledge graph was enriched with all concepts surfaced during this mandate before setting DONE. Unresolved `ONTOLOGY_GAP` discoveries block the DONE transition.
10. **Security-gate-before-DONE:** A mandate with `security_review_required: true` in the DMT cannot transition to DONE without a Security Review Report carrying `SECURE_PASS` or `CONDITIONAL_PASS`. A Security `FAIL` moves the mandate to `NEEDS_REVISION` regardless of QA verdict.
11. **Git-clean-before-IN_REVIEW:** The working directory must be clean in every codebase touched by the mandate (`git status` shows nothing to commit) before transitioning to `IN_REVIEW`. All mandate work must be committed with accurate commit messages. No staged or unstaged changes may remain. Cross-codebase mandates must have at least one commit per codebase. For SRE mandates, all IaC changes must have been committed before they were applied. A Coder or SRE who sets `IN_REVIEW` with uncommitted changes has not completed the mandate. QA must run `git status` and `git log` as part of verification.

### State Diagram (ASCII)

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

---

## Track 2 — Quality Lifecycle State Machine

### Status Definitions — Track 2 — Quality Lifecycle (asynchronous, investment-based)

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `BACKLOG` | [REVIEW]/[INSPECT] mandate not yet prioritised | Architect |
| `MANDATED` | Scope, time budget, and threshold declared; ready | Architect |
| `IN_PROGRESS` | Reviewer or Inspector is actively running | Reviewer / Inspector |
| `DONE` | Report filed, child mandates created | Reviewer / Inspector |
| `BLOCKED` | Access unavailable (Inspector only) | Inspector |

### Legal Transitions — Quality Lifecycle

```text
BACKLOG       → MANDATED      (Architect scopes and prioritises)
MANDATED      → IN_PROGRESS   (Reviewer/Inspector begins)
IN_PROGRESS   → DONE          (report filed, child mandates created)
IN_PROGRESS   → BLOCKED       (Inspector: live system unavailable)
BLOCKED       → IN_PROGRESS   (access restored)
```

### Illegal Transitions — Quality Lifecycle

```text
MANDATED      → DONE           (work was not done; filing an empty report)
IN_PROGRESS   → VERIFIED       (quality lifecycle has no VERIFIED state)
ANY           → NEEDS_REVISION (if review was inadequate, a new mandate is
                                created; the original is not revised)
ANY           → DONE set by Architect  (Reviewer/Inspector self-closes;
                                        no Architect acceptance gate)
```

### Quality Lifecycle Invariants

Continuing the numbering from core pipeline invariants (1–11):

**12. No pipeline gate:** A quality lifecycle mandate in any status does not block any core pipeline mandate from progressing.

**13. Self-terminating:** The Reviewer or Inspector sets DONE. No Architect acceptance required.

**14. DMT is the plan:** No PLANNED status; the [REVIEW] or [INSPECT] DMT declares scope, depth, and time budget.

**15. Output is mandates:** The terminal artifact is a CRR or PIR plus child mandates. No verdict is issued.

**16. Compute scheduling:** [REVIEW] mandates may be set IN_PROGRESS during idle compute — when no core mandates are IN_PROGRESS or IN_REVIEW.

### State Diagram (ASCII) — Quality Lifecycle

```text
  ┌─────────┐
  │ BACKLOG │
  └────┬────┘
       │ Architect (scopes and prioritises)
  ┌────▼────┐
  │MANDATED │
  └────┬────┘
       │ Reviewer / Inspector
  ┌────▼──────┐
  │IN_PROGRESS│◄──────────────────┐
  └─────┬─────┘                   │ access restored
        │                    ┌────┴───────┐
        ├───────────────────►│  BLOCKED   │ (Inspector only)
        │ system unavailable └────────────┘
        │ report filed
  ┌─────▼────┐
  │   DONE   │
  └──────────┘
       │
       └──► child mandates → Core Pipeline BACKLOG → Architect prioritises
```

---

## Track Interaction

### Core Pipeline → Quality Lifecycle

The Architect observes DONE on a core mandate and decides to invest in quality
review. The Architect creates a [REVIEW] or [INSPECT] mandate. This is not
automatic. It is not required. It is Architect-discretionary — a deliberate
investment decision independent of any specific core mandate.

### Quality Lifecycle → Core Pipeline

The Reviewer or Inspector produces child mandates at DONE. Child mandates enter
the core pipeline at BACKLOG. The Architect prioritises them like any other
BACKLOG item. The gap between a finding and its remediation is explicit —
measured in mandate cycles, not hours.

### Feedback Loop

```text
Core Pipeline                          Quality Lifecycle
─────────────────────────────────────────────────────────────────
BACKLOG → ... → DONE ──────────────►  [REVIEW]/[INSPECT] mandate
                  ▲                         │
                  │                         ▼
                  │                    IN_PROGRESS
                  │                         │
                  │                         ▼
                  │                       DONE
                  │                    (CRR / PIR)
                  │                         │
                  │                   child mandates
                  │                         │
                  └─────────── BACKLOG ◄─────┘
                               (Architect prioritises)
```

---

---

## Track 3 — Break-Glass State Machine

### Overview

The break-glass track is a single-role, single-artifact track. It is not
gate-based and does not follow the BACKLOG → MANDATED → IN_RECON sequence.
It exists for production incidents where delay is unacceptable. The output
is an EIR that becomes the input for a mandatory retroactive pipeline pass
on Track 1.

### Status Definitions — Track 3 — Break-Glass

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `IN_PROGRESS` | Emergency Responder is actively fixing | Emergency Responder |
| `NEEDS_REVISION` | Fix complete; retroactive DIP and QA required | Emergency Responder |

### Legal Transitions — Break-Glass

```text
(none)          → IN_PROGRESS    (Emergency Responder opens EIR; no prior state required)
IN_PROGRESS     → NEEDS_REVISION (Emergency Responder reaches exit gate)
NEEDS_REVISION  → IN_RECON       (Engineer begins retroactive DIP; mandate joins Track 1)
```

### Illegal Transitions — Break-Glass

```text
IN_PROGRESS     → DONE           (no retroactive pass = mandate not governed)
IN_PROGRESS     → VERIFIED       (no QA has run)
NEEDS_REVISION  → DONE           (retroactive DIP and QA must complete first)
```

### Break-Glass Invariants

Continuing the numbering from quality lifecycle invariants (1–16):

**17. EIR-before-close:** The Emergency Responder must not end the session
without an EIR board item or local file at
`docs/mandates/emergency/{date}_{slug}_eir.md`.

**18. Verification-output-required:** The EIR must contain verbatim
verification output before the board status is set to `NEEDS_REVISION`.

**19. Discovery-classification-required:** Every finding beyond the
immediate bug must be classified as a DISCOVERY (with class) in the EIR
before the session ends. Unclassified findings in prose are a protocol
violation.

**20. Retroactive-pass-within-24h:** Within 24 hours of the emergency
session ending, the Engineer must author a DIP from the EIR, QA must
verify the fix, and child mandates must be created for every DISCOVERY
filed. The mandate cannot reach DONE without this.

**21. Safety Floor persists:** The Emergency Responder operates under the
AGENTS.md Safety Floor at all times. The break-glass designation does not
suspend any safety constraint.

**22. Retroactive re-entry is Track 1:** Once the Engineer begins the
retroactive DIP (`NEEDS_REVISION → IN_RECON`), the mandate follows the
standard Track 1 state machine from `IN_RECON` onward.

### State Diagram (ASCII) — Break-Glass

```text
  (incident occurs)
        │
        ▼ Emergency Responder opens EIR
  ┌─────────────┐
  │ IN_PROGRESS │
  └──────┬──────┘
         │ Exit gate reached
         │ (EIR complete, fix verified,
         │  status note appended)
  ┌──────▼──────────┐
  │ NEEDS_REVISION  │ ←── "retroactive DIP and QA required"
  └──────┬──────────┘
         │ Engineer begins retroactive DIP
         ▼
  Track 1 re-entry at IN_RECON
  (normal pipeline from here)
```

---

## Asynchronous Properties

**Timing asynchrony:** [REVIEW] and [INSPECT] mandates are not attached to
specific core mandate board items. They target components, service boundaries,
or traffic surfaces — independently of what is currently IN_PROGRESS or
IN_REVIEW on the core pipeline.

**Compute asynchrony:** Reviewer mandates may be scheduled during idle compute
without competing with active development work. Invariant 16 formalises this: a
[REVIEW] mandate may begin when no core mandates are IN_PROGRESS or IN_REVIEW.

**Output asynchrony:** Findings re-enter the core pipeline at BACKLOG. The
Architect determines when they are scheduled. There is no direct connection
between a quality lifecycle finding and the next sprint — the gap is
intentional, explicit, and Architect-controlled.
