# Harness Quickstart

## Overview

This document explains how to start, plan, implement, and verify changes in fleet-mcp using the Harnessable agent development pipeline. Reading this document top-to-bottom is sufficient to complete a mandate.

---

## The Three Commands

Changes in fleet-mcp flow through three sequential slash commands, each assigned to a distinct agent role.

| Command | Role | Produces | Done when |
| --- | --- | --- | --- |
| `/engineer <description or board-task-URL>` | Engineer | A DIP file under `docs/mandates/` | Board status reaches `PLANNED` |
| `/coder <path-to-DIP.md>` | Coder | Checked-off DIP steps + filled TIR | Board status reaches `IN_REVIEW` |
| `/qa <path-to-DIP.md>` | QA | QA Verdict block in DIP | Board status reaches `VERIFIED` or `NEEDS_REVISION` |

**`/engineer <description or board-task-URL>`** — The Engineer performs six recon passes against the codebase and any board item, resolves open questions, records architecture decisions, and authors the DIP. The Engineer does not write implementation code. The turn is complete when the DIP is committed with board status `PLANNED`.

**`/coder <path-to-DIP.md>`** — The Coder reads the DIP in full, executes each `## Implementation Steps` entry in order, verifies each step before advancing, streams evidence into the Task Implementation Report (TIR), and commits all changes. The turn is complete when every required checklist item passes and board status is `IN_REVIEW`.

**`/qa <path-to-DIP.md>`** — QA re-executes all verification commands independently (never re-uses Coder output), checks the TIR for completeness, and issues a `PASS`, `CONDITIONAL_PASS`, or `FAIL` verdict in the DIP. The turn is complete when the verdict is committed and the board reflects `VERIFIED` or `NEEDS_REVISION`.

**Architect's role:** (a) write the mandate description or create the board item; (b) invoke `/engineer`; (c) review and accept or reject the QA verdict, then set the board to `DONE`.

---

## Starting a Mandate

All three input forms below produce the same output: a DIP file under `docs/mandates/`.

**Form 1 — Inline description (most common for solo use):**

```text
/engineer Build a fleet_get_service_health() tool that pings each service in the fleet
```

The Engineer treats this as a Case C input. No board item is created automatically. The DIP is committed locally and all intended board operations are recorded in the DIP `## Tracker Ops Log`.

**Form 2 — Board task URL:**

```text
/engineer https://github.com/users/moijafcor/projects/2?pane=issue&itemId=192012347
```

The Engineer fetches the full board item, reads all fields and comments, then updates board status to `IN_RECON` before beginning recon. The DIP is linked back to the board item on completion.

**Form 3 — Local file path:**

```text
/engineer docs/mandates/my-feature.md
```

The Engineer reads the file as the DMT (Design Mandate Template). No board item is required. Useful for pre-authored mandates or mandates migrated from another system.

---

## Reading a DIP

A DIP (Design Implementation Plan) is the contract between the Engineer and the Coder. It is the single source of truth for mandate state. The board status reflects it, but the DIP is authoritative.

Key sections:

| Section | Contents |
| --- | --- |
| `## Mandate Reference` | What is being built, why, and the acceptance criteria from the DMT |
| `## Architecture Decisions` | ADRs explaining non-obvious design choices; Coder must not modify these |
| `## Implementation Steps` | Ordered checklist of concrete actions for the Coder |
| `## Verification Checklists` | What must be true for the mandate to pass QA; `[REQUIRED]` items are mandatory |
| `## Task Implementation Report` | Coder's evidence log — filled during `/coder`, never before |
| `## QA Verdict` | QA's final assessment — filled during `/qa`, never before |
| `## Field Discoveries` | Deviations, blockers, and harness improvements discovered mid-execution |

---

## Board Statuses

| Status | Meaning | Who sets it |
| --- | --- | --- |
| `BACKLOG` | Not yet actionable | Architect |
| `MANDATED` | DMT approved; Engineer may begin | Architect |
| `IN_RECON` | Engineer running discovery | Engineer |
| `PLANNED` | DIP complete; Coder may begin | Engineer |
| `IN_PROGRESS` | Coder implementing | Coder |
| `IN_REVIEW` | Coder done; awaiting QA | Coder |
| `NEEDS_REVISION` | QA FAIL; Coder must address findings | QA |
| `VERIFIED` | QA PASS or CONDITIONAL_PASS | QA |
| `DONE` | Architect accepted verdict; mandate closed | Architect |
| `BLOCKED` | Work halted; Architect must resolve | Any |

For inline or local-file mandates (no board item), these transitions are recorded in the DIP `## Tracker Ops Log` rather than on the board.

---

## Solo Mode

Solo mode applies when one person performs all roles (Architect, Engineer, Coder, and QA). Most mandates in fleet-mcp operate in solo mode.

Four compensating controls apply in solo mode:

1. **24-hour delay** between Coder sign-off and QA re-execution. Do not run `/qa` in the same session as `/coder`.
2. **Re-run all TIR evidence** — do not copy-paste output from the Coder session into the QA verdict. QA must independently re-execute every verification command.
3. **Explicit Architect sign-off** required for `CONDITIONAL_PASS` or `NEEDS_REVISION` verdicts before closing the mandate.
4. **Declare `Operating Mode: solo`** in the DIP header.

The controls exist to ensure QA does not rubber-stamp the Coder's own work. Skipping them is a protocol violation even under time pressure.

---

## Field Discoveries

Field Discoveries are append-only observations recorded in the DIP `## Field Discoveries` table during any agent turn. Never delete or edit a prior entry.

| Class | When to use | Required action |
| --- | --- | --- |
| `INFO` | Context only; no action required | Record and continue |
| `DEVIATION` | Implementation differs from a DIP step | Document inline with the step (`[DEVIATION 00N]` tag); note in Field Discoveries table; proceed with correct implementation |
| `BLOCKER` | Work cannot proceed | Set board to `BLOCKED`; create a child task; halt |
| `HARNESS_IMPROVEMENT` | A pipeline control is missing or incorrect | Log it; optionally create a child task; continue if possible |

**DEVIATION protocol (detailed):** Stop before implementing the alternative. Append the DEVIATION row to the table, add an inline `[DEVIATION 00N]` note to the affected step in the DIP, annotate the verification checklist item if the verification approach changes, then proceed.

**BLOCKER protocol:** A BLOCKER is not a DEVIATION. If the mandate cannot proceed without an Architect decision or an unresolved prerequisite, file the BLOCKER, set the board to `BLOCKED`, and stop. Do not work around it silently.

---

## Common Operations

**Q: How do I check if a mandate is in progress?**

Run `ls docs/mandates/` and open the relevant DIP. Check `**Board Status:**` in the DIP header and `## Implementation Steps` for checked/unchecked items. A mandate is in progress if the board status is `IN_PROGRESS` or `IN_REVIEW`.

**Q: How do I unblock a BLOCKED mandate?**

Find the `BLOCKER` entry in `## Field Discoveries`. Resolve the blocker (usually a missing prerequisite or Architect decision). Update the DIP `## Tracker Ops Log`, set the board back to the prior status (usually `IN_PROGRESS`), and re-invoke `/coder` with the DIP path.

**Q: How do I respond to a NEEDS_REVISION verdict?**

Read the `## QA Verdict` section for specific failures. Re-invoke `/coder` with the DIP path; the Coder will address QA findings and update the TIR. Then re-invoke `/qa`. The 24-hour solo-mode delay applies again between the Coder and QA turns.

**Q: How do I close a mandate (DONE)?**

After QA issues `PASS` or `CONDITIONAL_PASS`, the Architect reviews the QA Verdict and updates the board to `DONE`. Add a `## Post-Close Notes` entry with the date and rationale. The DIP is then immutable (append-only via Post-Close Notes).

**Q: What if the board integration is unavailable?**

Work proceeds locally. All intended board operations (status updates, comments) are logged in DIP `## Tracker Ops Log` and executed retroactively when the integration is restored. No mandate work is blocked by a board outage.

---

## Going Deeper

| Topic | File |
| --- | --- |
| Engineer recon protocol (all 6 passes) | `docs/harness/agents/engineer.md` |
| Coder build discipline | `docs/harness/agents/coder.md` |
| QA verification protocol | `docs/harness/agents/qa.md` |
| Architect DMT authoring | `docs/harness/agents/architect.md` |
| Full state machine and invariants | `docs/harness/vendor/harnessable/references/state-machine.md` |
| Role definitions and permissions | `docs/harness/vendor/harnessable/references/roles.md` |
| Error modes (A–E) | `docs/harness/vendor/harnessable/references/error-modes.md` |
| Continuous improvement protocol | `docs/harness/vendor/harnessable/references/continuous-improvement.md` |
| DIP template | `docs/harness/templates/dip.md` |
