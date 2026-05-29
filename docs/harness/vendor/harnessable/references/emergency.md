# Emergency Response Protocol

## Overview

The emergency protocol is a two-phase process:

1. **Emergency session** — fix concurrent with minimum viable trail
2. **Retroactive pass** — complete the full protocol after the crisis

Neither phase is optional. A fix with no trail is an undocumented system state
change: the system is now different and nobody knows why, under what conditions,
or with what side effects. A trail with no fix is a failed emergency response.
Both must complete before the mandate can reach `DONE`.

The emergency protocol does not suspend any other framework invariant. The Safety
Floor defined in `AGENTS.md`, the prohibition on self-QA, and the requirement for
verification output all apply without modification. The emergency designation
changes the sequence — fix before DIP — but it does not relax the standards.

---

## Phase 1 — Emergency session

### The board item as primary instrument

The Emergency Responder's first act, before touching any file, is to create a
board item. The board item is not documentation of work that has already
happened — it is the instrument through which the session is conducted. Every
command run, every finding, every changed file is appended to it in real time.
The item is never edited retroactively. Once a line is written, it stands as the
record of what was known at that moment.

If the board integration is unavailable, the Emergency Responder creates a local
file at `docs/mandates/emergency/{YYYY-MM-DD}_{slug}_eir.md` and commits it as
the first commit of the session. The local file carries identical authority to a
board item. All subsequent appends go to it.

The structure of the item at creation:

```text
Title:  [EMERGENCY] {one-line description of what broke}
Status: IN_PROGRESS
Body:
  Symptom:    {what the system is doing / not doing}
  Hypothesis: {what you think is wrong}
  Approach:   {what you are going to try}
```

The hypothesis and approach are provisional. They will be updated — by appending,
not by editing — as the session progresses. Appends are the medium; the original
text is the baseline against which the root cause analysis becomes legible.

### Minimum viable trail

The session is not complete until all of the following conditions hold:

- The board item exists and states the root cause. Not the symptom. Not a
  hypothesis that turned out to be wrong. The actual root cause, identified
  during the session.
- Every file changed during the session is listed in the board item with a
  one-line rationale. "Updated config" is not a rationale. "Disabled rate
  limiter on `/auth/token` — this was the proximate cause of the 502s" is.
- Every finding beyond the immediate bug is filed as a `DISCOVERY` with its
  class, before the session ends. Findings left as prose in the notes section
  are a protocol violation.
- Verification output is pasted verbatim into the board item. The fix is not
  verified until the output that demonstrates it is in the record.
- The board item is appended with the retroactive pass declaration and status
  is set to `NEEDS_REVISION`.

A session that exits without all five conditions satisfied is incomplete. The
Emergency Responder must not end the session to hand off to a retroactive pass
that has no trail to work from.

### DISCOVERY entries during the session

Every finding beyond the immediate bug — a config gap, a missing guard, an
undeclared concept in the knowledge graph, a structural problem in a related
system — must be classified before work continues. The classification goes into
the board item inline:

```text
DISCOVERY: {CLASS} — {one-line description}
```

Valid classes: `INFO`, `DEVIATION`, `BLOCKER`, `HARNESS_IMPROVEMENT`,
`ONTOLOGY_GAP`.

DISCOVERY entries are filed during the session. Child mandates are not created
during the session. The distinction is deliberate. The emergency session is not
the right context for mandate scoping: the Emergency Responder is operating under
time pressure, with incomplete information, and without the full architectural
context that mandate authoring requires. Filing a DISCOVERY takes one line.
Scoping a mandate requires judgment the session cannot afford. The retroactive
pass creates the mandates from the filed discoveries.

### The 24-hour window

The board item's final append, before status is set to `NEEDS_REVISION`, declares
the 24-hour deadline:

```text
## Retroactive pass required
DIP and QA verification required within 24 hours.
Architectural findings above require child mandates.
Engineer: read this board item and author a retroactive DIP.
```

This is not a target. It is a constraint. A mandate at `NEEDS_REVISION` without
a retroactive DIP authoring begun within 24 hours is a protocol violation. The
clock starts when the board item is appended with this note.

---

## Phase 2 — Retroactive pass

### Engineer: retroactive DIP

The Engineer reads the board item and the git diff, then authors a retroactive
DIP. The DIP describes what was done and why — not what was planned. The
Implementation Steps section describes actual steps taken, in sequence, as
derived from the board item's append history. The Recon Findings section captures
the root cause analysis conducted during the session, including the dead ends and
revised hypotheses.

A retroactive DIP is not a sanitised narrative. It is a structured account of
what the Emergency Responder found, what they tried, and what fixed it. The
Engineering Model of `what was decided and why` applies — but the decisions are
past tense.

The Engineer sets the board status to `IN_RECON` when beginning the retroactive
DIP. This is the point at which the mandate formally re-enters Track 1.

### Coder: TIR from session notes

The Coder files a proper Task Implementation Report from the emergency session's
raw notes. The primary evidence source is the verification output pasted during
the session. The Coder does not write new code during the retroactive pass — the
fix is already in place. The TIR attests that the fix is in the codebase, that
the evidence is real, and that the implementation report is complete.

### QA: independent verification

QA verifies that the fix is actually correct — not merely that it was applied.
The Emergency Responder's verification output pasted during the session is not
sufficient for QA purposes. QA re-executes the checks themselves, independently,
against the system as it stands after the fix. This is the same standard applied
to any `IN_REVIEW` mandate. The emergency designation does not lower the bar.

### Child mandates from DISCOVERY entries

Every DISCOVERY filed during the emergency session generates a child mandate in
the retroactive pass. The Engineer or Architect scopes each mandate from the
one-line description filed during the session, adding the context and constraints
that the session could not afford to develop. Architectural findings classified as
`HARNESS_IMPROVEMENT` or `BLOCKER` receive the same mandate scoping treatment as
any other discovery of those classes: they enter the core pipeline at `BACKLOG`
and are prioritised by the Architect.

---

## Board status path

The emergency mandate traverses a reduced path before re-entering the standard
pipeline:

| Status | Set by | Trigger |
| --- | --- | --- |
| `IN_PROGRESS` | Emergency Responder | EIR board item created; no prior board state required |
| `NEEDS_REVISION` | Emergency Responder | Exit gate satisfied: root cause stated, all findings classified, verification output pasted, retroactive note appended |
| `IN_RECON` | Engineer | Retroactive DIP authoring begins; mandate re-enters Track 1 |
| → Track 1 from `IN_RECON` | — | Standard pipeline: `IN_RECON → PLANNED → IN_PROGRESS → IN_REVIEW → VERIFIED → DONE` |

```text
  (incident occurs)
        │
        ▼ Emergency Responder opens EIR board item
  ┌─────────────┐
  │ IN_PROGRESS │
  └──────┬──────┘
         │ Exit gate reached
         │ (root cause stated, all findings classified,
         │  verification output pasted, retroactive note appended)
  ┌──────▼──────────┐
  │ NEEDS_REVISION  │ ← "retroactive DIP and QA required within 24h"
  └──────┬──────────┘
         │ Engineer begins retroactive DIP (within 24h)
         ▼
    Track 1 re-entry at IN_RECON
    (standard pipeline from here)
```

`NEEDS_REVISION` in the emergency context does not mean the fix failed. It means
the mandate is not yet fully governed: the EIR exists, the fix is in production,
but the DIP, TIR, and QA Verdict are still outstanding. The status signals that
obligation explicitly. A mandate that exits `NEEDS_REVISION` prematurely — without
a complete retroactive pass — has bypassed QA and cannot reach `DONE`.

The mandate reaches `DONE` only when the Architect accepts the QA Verdict after
the full retroactive pass completes. Every DISCOVERY filed during the emergency
session must have a corresponding child mandate before the Architect may set
`DONE`. An emergency mandate with unresolved DISCOVERY entries is not closeable.

See `framework/vendor/harnessable/references/state-machine.md` — Track 3 for the
complete Break-Glass state machine, invariants 17–22, and illegal transitions.
