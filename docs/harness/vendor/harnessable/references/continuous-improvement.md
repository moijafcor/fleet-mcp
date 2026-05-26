# Continuous Improvement Protocol

## Core Principle

Every failure in the mandate pipeline is evidence of a missing control.
The failure itself is not the problem — the absence of the control that
should have caught it earlier is the problem.

```
Failure occurs
      ↓
Root Cause Analysis (what happened?)
      ↓
Control Gap Identification (what was missing?)
      ↓
Harness Improvement (add the missing control)
      ↓
Prevention (future mandates are protected)
```

This protocol applies to **any** failure: a Coder hook that failed, a QA FAIL
verdict, a BLOCKER field discovery, an Error Mode that fired, or a post-DONE
production incident traceable to a mandate.

---

## Root Cause Analysis — Required Questions

For every failure, the acting agent must answer:

| Question | Example answers |
|---|---|
| What control was missing? | Missing validation, missing permission check, missing test, missing approval step, missing monitoring, missing retry policy |
| At which pipeline stage should it have been caught? | DMT authoring, DIP recon, DIP verification checklist, Coder hook, QA verification, post-deploy monitoring |
| Why did it reach the stage it did? | Checklist item not specific enough, hook not in suite, recon pass skipped, acceptance criteria ambiguous |
| Is this a one-off or a class of failure? | One-off → fix this instance. Class → add a systematic control |

---

## Harness Improvement Actions

Based on the control gap, the appropriate harness improvement is:

| Gap type | Improvement action | Where it lands |
|---|---|---|
| Missing validation | Add hook to Coder's pre-completion suite | `agents/coder.md` hook suite |
| Missing test | Add to DIP verification checklist template | `templates/dip.md` |
| Missing recon step | Add pass to Engineer recon protocol | `agents/engineer.md` |
| Missing approval step | Add to state machine transitions | `references/state-machine.md` |
| Missing monitoring | Add to SRE containment checklist | `agents/engineer.md` containment section |
| Missing retry policy | Add to DIP `## Architecture Decisions` prompt | `templates/dip.md` |
| Ambiguous DMT criteria | Add to Architect's DMT authoring checklist | `references/roles.md` |
| QA missed a check class | Add to QA spot check protocol | `agents/qa.md` |

---

## Filing a Harness Improvement

Any agent may file a harness improvement. It is a first-class artifact, not a comment.

### Step 1 — Create the improvement record

Append to DIP `## Field Discoveries`:
```
| N | [date] | [role] | HARNESS_IMPROVEMENT | [failure description] — [control gap identified] | [proposed improvement] |
```

### Step 2 — Create a child task

```
Title: [HARNESS] {brief description of missing control}
Body:
  Discovered during: [mandate slug] — [DIP path]
  Failure: [what happened]
  Control gap: [what was missing]
  Proposed improvement: [specific change to which skill file]
  Priority: [LOW | MEDIUM | HIGH]
```

Status: `BACKLOG` — Architect reviews and prioritises.

### Step 3 — If the improvement is trivial (< 5 min, purely additive)

Apply it directly to the skill file and note it in the child task.
Examples of trivial improvements:
- Adding a command to the Coder hook suite
- Adding a row to the QA spot check table
- Adding a recon step to Engineer Pass 6

Non-trivial improvements (change to state machine, new role, new artifact type)
require Architect review before applying.

---

## Improvement Priority Classification

| Priority | Criteria | Response time |
|---|---|---|
| `CRITICAL` | Failure reached production or caused data loss | Fix before next mandate in same domain |
| `HIGH` | Failure reached QA or caused significant rework | Fix within 3 mandates |
| `MEDIUM` | Caught at hook or DEVIATION stage but required multiple retries | Fix within 10 mandates |
| `LOW` | Minor friction, no rework needed | Batch with next skill review |

---

## Retrospective Trigger

A structured retrospective (reading all HARNESS_IMPROVEMENT discoveries across
recent mandates) should be triggered when:
- 3+ HARNESS_IMPROVEMENT entries accumulate across any domain
- A `CRITICAL` improvement is filed
- A mandate closes with `CONDITIONAL_PASS` (warning sign of systemic gap)
- Any mandate goes through `NEEDS_REVISION` more than once

In a retrospective session, the Engineer role audits the full discovery log
and proposes a batch of harness improvements as a single meta-mandate:

```
DMT title: [HARNESS] Skill improvements from {mandate-slug-1}, {mandate-slug-2}, ...
```

This meta-mandate goes through the full pipeline like any other mandate —
with its own DIP, TIR, and QA verdict. The skill files are the codebase.

The DIP for a `[HARNESS]` meta-mandate lives in the harnessable repository at
`docs/mandates/{harness-slug}_implementation_plan.md`, not in the consuming
project's `docs/mandates/harness/` directory. The framework repository is the
codebase; the DIP and TIR belong there.

---

## Failure Classes and Their Systemic Signals

| Failure class | If it recurs | Systemic signal |
|---|---|---|
| Coder hook fails 3x on same step | Add sub-agent RCA delegation | DIP step is underspecified |
| QA issues FAIL for TIR evidence gaps | Tighten TIR evidence section template | Coder doesn't know what evidence to collect |
| BLOCKER field discoveries > 2 per mandate | Tighten Engineer recon passes | Recon is insufficiently deep |
| `NEEDS_REVISION` issued twice on same mandate | Mandate scope was entangled | Architect needs stricter scope isolation at DMT time |
| Error Mode D2 fires (DIP missed intent) | Add Architect review of DIP before PLANNED | Engineer-Architect handoff has a gap |
| Sub-agent delegated but findings unused | Add synthesis requirement to delegation protocol | Delegation pattern is cargo-culted |
