# Role Definitions

The mandate workflow is inspired by regulated engineering disciplines (civil,
structural). Roles are **functional**, not personal — a single human or agent
session may wear multiple hats, but must be explicit about which role is
active and must not violate role boundaries.

---

## Architect

**Responsibility:** Define the intent. Own the mandate. Review outcomes.

**Produces:** Design Mandate Task (DMT) — a task in the project tracker containing:

- Problem statement and motivation
- Success criteria (explicit, measurable where possible)
- Constraints (tech, time, compliance, compatibility)
- Out-of-scope declarations
- Acceptance criteria for QA
- Links to relevant prior mandates, ADRs, or context

**Permissions:**

- Create, modify, and close DMT
- Approve or reject QA verdicts
- Reassign board status at any point
- Scope-expand a mandate (via DMT edit + new `## Architect Notes` block)

**Prohibitions:**

- Must not implement work (write code, execute commands, modify non-DMT files)
- Must not approve their own QA verdict

**Handoff signal:** DMT status set to `MANDATED` = Engineer may begin.

---

## Engineer

**Responsibility:** Translate mandate intent into an implementable plan.
The Engineer is the most cognitively demanding role — a bad plan costs more
than a bad implementation.

**Produces:** Design Implementation Plan (DIP) at `docs/mandates/{bucket}/{slug}_implementation_plan.md`

**Recon Pass (mandatory before authoring DIP):**
See `agents/engineer.md` for the full recon protocol. Minimum recon:

- Read the DMT in full, including comments and linked issues
- Scan the affected domain (files, systems, schemas, processes, policies)
- Read `docs/mandates/` for related prior mandates
- Query Claude memory/past sessions for relevant context
- Check infrastructure or operational state if relevant
- Identify all external dependencies (APIs, services, integrations, stakeholders)

**Permissions:**

- Author and update DIP
- Set board to `IN_RECON`, `PLANNED`
- File field discoveries
- Create child tasks
- Comment on DMT

**Prohibitions:**

- Must not implement (no changes to the domain under mandate — code, infrastructure, documents, communications, or any other output)
- Must not advance board past `PLANNED` (Coder owns `IN_PROGRESS`)

**Handoff signal:** DIP complete, board status `PLANNED` = Coder may begin.

---

## Coder

**Responsibility:** Execute the implementation exactly as designed in the DIP.
Deviation requires a field discovery — not silent modification.

**Produces:**

- The actual implementation (code, config, infra changes, migrations)
- Task Implementation Report (TIR) — embedded as `## Task Implementation Report`
  section in the DIP

**Build discipline:**

- Work one DIP `## Implementation Steps` item at a time
- Check each step off as completed
- Run verification checks after each logical unit, not just at the end
- Stream TIR updates continuously — do not batch everything at the end

**Permissions:**

- Implement per DIP
- Update TIR section of DIP
- Set board to `IN_PROGRESS`, `IN_REVIEW`
- File field discoveries
- Create child tasks
- Request DIP clarification from Engineer (set board to `BLOCKED`, create child)

**Prohibitions:**

- Must not modify DIP `## Implementation Steps` or `## Architecture Decisions`
  (except to add field discoveries and check off completed steps)
- Must not advance board to `VERIFIED` or `DONE`
- Must not mark work complete if any verification gate fails

**Handoff signal:** TIR complete, all gates passed, board status `IN_REVIEW` = QA may begin.

---

## SRE

**Responsibility:** Execute infrastructure and operational mandates exactly as designed
in the DIP. Deviation requires a field discovery — not silent modification. Production
state exists outside git; rollback requires a runbook, not a revert.

**Produces:**

- The actual infrastructure change (config, IaC, migrations, deployments, DNS, certs)
- SRE Implementation Report (SIR) — embedded as `## SRE Implementation Report`
  section in the DIP

**Pre-change requirements:**

- Capture pre-change state before touching any system (Step 0 — mandatory)
- Confirm rollback procedure is documented and viable before proceeding
- Confirm blast radius declaration matches actual recon before proceeding
- Execute DIP steps in order; verify system health between each step
- Commit all IaC changes to git before applying them
- Stream SIR updates continuously — do not batch at the end

**Permissions:**

- Execute changes per DIP
- Update SIR section of DIP
- Set board to `IN_PROGRESS`, `IN_REVIEW`
- File field discoveries
- Create child tasks
- Request DIP clarification from Engineer (set board to `BLOCKED`, create child)

**Prohibitions:**

- Must not execute a change step without Pre-Change State Capture complete
- Must not proceed with a mandate that has no documented rollback procedure
- Must not continue applying changes when health checks are failing
- Must not self-verify (cannot be the QA for the same mandate)
- Must not apply multiple DIP steps in a single batch
- Must not advance board to `VERIFIED` or `DONE`
- Must not set `IN_REVIEW` with uncommitted IaC changes or a degraded dependent service

**Handoff signal:** SIR complete, all gates passed, board status `IN_REVIEW` = QA may begin.

---

## QA

**Responsibility:** Verify the implementation against the DIP and DMT — independently,
without assuming the Coder or SRE did it right.

**Produces:** QA Verdict block appended to the DIP implementation report section
(`## Task Implementation Report` for code mandates; `## SRE Implementation Report`
for infrastructure mandates).

**Verification approach:**

- Read the DIP `## Verification Checklists` section as the primary test matrix
- Read the DMT acceptance criteria as the secondary test matrix
- Read the TIR or SIR as evidence (but verify claims — do not take on faith)
- Execute spot-checks, automated tests, and any QA-specific checks defined in DIP
- See `agents/qa.md` for the full verification protocol

**Verdict options:**

- `PASS` — all checks satisfied, advance board to `VERIFIED`
- `CONDITIONAL_PASS` — minor issues noted, Architect may accept or reject
- `FAIL` — one or more required checks failed, board to `NEEDS_REVISION`

**Permissions:**

- Set board to `VERIFIED`, `NEEDS_REVISION`
- Create child tasks for defects
- Comment on DMT

**Prohibitions:**

- Must not fix defects themselves (creates QA / Coder or QA / SRE role collapse)
- Must not issue `PASS` with open required check failures
- Must not skip the DMT acceptance criteria review

---

## Security

**Responsibility:** Adversarial review of implementations on mandates the
Architect has explicitly flagged for Security review. Ask not "does it work?"
but "can it be made to not work, leak, or be abused?"

**Invoked by:** Architect. Not automatic. Runs after QA PASS or CONDITIONAL_PASS,
before the Architect accepts and sets DONE. See `agents/security.md` for the full
eight-phase review protocol.

**Invocation conditions** — the Architect flags the mandate when the change:

- Touches authentication, authorisation, or session management
- Accepts input from untrusted sources (user input, API payloads, file uploads, webhooks)
- Handles credentials, secrets, tokens, or encryption keys
- Exposes new external-facing surfaces (routes, APIs, webhooks, integrations)
- Changes data access patterns or adds new data exposure paths
- Modifies privilege levels or permission structures
- Introduces new dependencies or upgrades security-relevant ones

**Produces:** Security Review Report (SRR) — appended to the DIP as
`## Security Review Report`.

**Verdict options:**

- `SECURE_PASS` — no CRITICAL or HIGH findings; all MEDIUM and LOW findings have child tasks
- `CONDITIONAL_PASS` — no CRITICAL findings; HIGH findings with documented Architect risk acceptance
- `FAIL` — CRITICAL findings, or HIGH without Architect risk acceptance; blocks DONE

**Permissions:**

- Append SRR to DIP
- Set board to `NEEDS_REVISION` on FAIL
- Create child tasks for findings
- Comment on DMT

**Prohibitions:**

- Must not re-run functional tests — that is QA's role
- Must not fix vulnerabilities and then issue SECURE_PASS (role collapse)
- Must not issue SECURE_PASS without completing the threat surface map
- Must not skip phases because the mandate "looks low-risk" — the Architect decided it needs review
- Must not review a mandate without QA PASS or CONDITIONAL_PASS already issued
- Must not be the Coder, SRE, or QA for the same mandate
- Must not skip Phase 8 — a verdict without a framework observation is incomplete

**Handoff signal:** SRR appended to DIP with SECURE_PASS or CONDITIONAL_PASS =
Architect may accept and set DONE.

---

## Solo / Small-Team Operating Mode

### When It Applies

Solo mode applies when:

- One or two humans are running the entire mandate pipeline, and
- No independent agent session is available to act as QA without access to the Coder session's context and prior outputs.

This is a proactive declaration, distinct from Error Mode E3 (which detects role collapse after the fact). Declare solo mode at the start of a mandate when role separation is structurally impossible.

### Required Compensating Controls

1. **24-hour delay between Coder sign-off and QA re-execution.** The same person must re-read the work with fresh eyes. Same-day re-execution in the same session does not satisfy this control.

2. **Re-run all TIR evidence — do not copy-paste.** Evidence cited in the QA verdict must be produced by fresh command execution during the QA pass, not carried over from Coder session notes.

3. **Explicit Architect sign-off required for all `CONDITIONAL_PASS` or `NEEDS_REVISION` outcomes.** Even when the Architect is the same person, sign-off must be documented as a `## Post-Close Notes` entry with a timestamp and rationale.

4. **Declare solo mode in the DIP header.** Add an `Operating Mode:` field with value `solo` or `small-team (N humans)` so the context is visible to any reviewer reading the artifact chain.

### Relationship to E3

Error Mode E3 still applies in solo mode — the QA verdict remains `UNVERIFIED (self-review)` and Architect sign-off is required before `DONE`. The compensating controls above reduce the probability that the Architect review will surface errors that should have been caught during QA.

See: `references/error-modes.md` — E3: Role Collapse
