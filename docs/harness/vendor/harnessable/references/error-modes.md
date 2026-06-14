# Error Modes — Classifier Knowledge Base

This document is the classifier's decision instrument.
When an acting agent fails, a classifier — human, QA role,
or observer session — reads this document to identify the
failure mode, determine whether retry is appropriate, and
route to the prescribed response.

The classifier must hold a fresh context with no shared
contamination from the acting agent's session. An agent
that has been looping cannot classify its own failure
reliably — its context is the evidence.

## Principle: failure is information

Failure is not always a symptom of insufficient
intelligence or missing context. Failure can be a signal
from the current state of the world. Looping without
classification is brute forcing. The correct response to
any failure is first to classify it, then to act.

No autonomous loop is permitted without a structurally
separate observer that holds stop authority.

---

## Classification protocol

1. Collect all observable signals at the agent's layer
2. Match against the mode entries below
3. If match: apply prescribed response
4. If no match: treat as UNRECOGNIZED_PATTERN
5. Never retry before classifying

---

## Failure Modes

---

### IMPLEMENTATION_ERROR

Definition:
  The agent's logic, code, or approach is wrong.
  The world state is correct. Retrying with correction
  is likely to converge.

Observable signals:
  - Test suite fails with assertion errors
  - Syntax or type errors in produced code
  - Logic produces wrong output, not no output
  - The failure is deterministic and reproducible

Layer:   Application / Code
Cause:   Agent error, not world state

Prescribed response:
  Retry permitted — limited.
  Inject per-criterion feedback (NEEDS_REVISION).
  Maximum 3 iterations before escalating to Architect.
  Each retry must target specific failing criteria.

Back-off strategy:
  None required — cause is internal to agent.

Loop permitted: YES (with iteration cap and feedback)

---

### ENVIRONMENT_FAILURE

Definition:
  The world state has changed or is incorrect.
  The agent's logic may be sound but the environment
  cannot fulfil the operation. Retrying without
  changing the environment will not converge.

Observable signals:
  - Service unreachable, connection refused
  - Dependency unavailable (database, API, file)
  - Infrastructure state diverged from expected
  - Operation fails identically across multiple attempts
    with no variation in error

Layer:   Infrastructure / Network / External service
Cause:   World state, not agent error

Prescribed response:
  BLOCKER immediately.
  Do not retry. Package observable state.
  Escalate with: symptoms, last known good state,
  all attempted actions, what access is needed.

Back-off strategy:
  Stop. Environment does not heal through retries.

Loop permitted: NO

---

### SPECIFICATION_CONFLICT

Definition:
  The acceptance criteria are internally contradictory,
  impossible to satisfy simultaneously, or conflict with
  a real-world constraint the Architect did not anticipate.

Observable signals:
  - Satisfying criterion A makes criterion B impossible
  - Implementation is blocked by a constraint not in spec
  - Multiple interpretations of spec lead to different
    and incompatible implementations

Layer:   Requirements / Mandate
Cause:   Specification error, not agent error

Prescribed response:
  BLOCKER immediately. Return to Architect.
  Do not attempt to resolve the conflict by choosing.
  Document both interpretations and the contradiction.

Back-off strategy:
  Stop. Retrying against contradictory requirements
  does not resolve the contradiction.

Loop permitted: NO

---

### BELOW_HORIZON

Definition:
  The failure cause exists at a layer the agent cannot
  observe or access from its current position.
  The agent's observable layer shows symptoms but the
  cause is below its visibility horizon.

  NOTE: Agent capability is not the limitation.
  A CC session can navigate KVM consoles, interpret
  boot output, recompile bootloaders. The limitation is
  pattern recognition — the agent does not know to look
  at a lower layer because the symptom pattern has not
  been matched to its cause layer.

  If the pattern exists in a relevant
  world_models/*_world_model.md file, the agent CAN
  execute the recovery autonomously. If not, the agent
  cannot know what it doesn't know.

Observable signals:
  - Persistent failure at the observable layer
    with no apparent cause at that layer
  - All observable explanations exhausted
  - Timing correlation with hardware or
    infrastructure events

Layer:   Below the agent's visibility horizon
         (Hardware → Boot → OS is below SSH → Service)
Cause:   Unknown from agent's position

Prescribed response:
  Package observable state and escalate.
  Escalation package must include:
    Observable symptoms (exact)
    Last known good state (timestamp)
    All attempted actions (what, when, result)
    Exhaustion evidence ("no layer N cause found")
    Access request (KVM, IPMI, rescue mode,
    provider console, physical access)
  Stop all action until lower-layer access granted.

  First search world_models/ for a matching symptom
  pattern before escalating.
  If match found: execute the documented recovery path.
  If no match: escalate, then encode discovery on resolution.

Back-off strategy:
  Stop. Lower-layer access is required before any
  further action is meaningful.

Loop permitted: NO

---

### OSCILLATION

Definition:
  The agent alternates between two or more wrong states
  without converging. Each iteration undoes or contradicts
  the prior iteration.

Observable signals:
  - Output of iteration N conflicts with iteration N-2
  - The same files are created, modified, and reverted
    across multiple iterations
  - Test results alternate between passing and failing
    on the same criteria across iterations
  - Agent references its own prior wrong output as
    justification for current action

Layer:   Agent reasoning / Context
Cause:   Missing forcing constraint or contradictory
         signals in context

Prescribed response:
  Stop immediately. Do not permit another iteration.
  Inject a forcing constraint before any retry:
    "Do X. Do not do Y. The conflict is Z."
  If oscillation persists after forcing constraint:
    discard context, fresh session, new framing.

Back-off strategy:
  Hard stop. Each oscillation iteration deepens
  context contamination.

Loop permitted: NO

---

### REGRESSION

Definition:
  Each iteration causes previously passing criteria
  to fail. The agent is making changes that break
  established functionality while attempting to fix
  the failing criteria.

Observable signals:
  - Completion Gate passes that passed before
    now fail after the latest changes
  - Test count passing decreases across iterations
  - Agent introduces changes to files unrelated to
    the failing criterion

Layer:   Agent reasoning / Code
Cause:   Scope creep in changes, missing isolation

Prescribed response:
  Stop. Rollback to the last state where all previously
  passing criteria still passed.
  File a new DIP with explicit constraint:
  "Do not modify X, Y, Z — they are currently passing."

Back-off strategy:
  Rollback first. Retry only from a clean baseline.

Loop permitted: NO

---

### CONTEXT_CORRUPTION

Definition:
  The agent's accumulated context has degraded its
  reasoning quality. It may reference prior wrong outputs
  as valid, repeat the same approach despite evidence
  it failed, or show increasing incoherence across turns.

Observable signals:
  - Agent cites its own prior incorrect reasoning
    as justification
  - The same approach is attempted a third time
    without meaningful variation
  - Agent output quality visibly degrades across turns
  - Back-pressure signals present: increasing hedging,
    unsolicited warnings, qualification density rising
  - Model jail time: refusals on previously executed
    actions, conservative scope interpretation

Layer:   Model reasoning / Context window
Cause:   Context accumulation, back-pressure cascade

Prescribed response:
  Discard the acting agent's context entirely.
  Do not inject more instructions into the
  contaminated session — this deepens corruption.
  Package: last clean state + observable symptoms.
  Start a fresh session with clean context.
  The classifier's fresh read IS the treatment.

Back-off strategy:
  Context discard. Exponential context growth
  does not resolve contamination.

Loop permitted: NO

---

### MISSING_PREREQUISITE

Definition:
  The task requires prior work that was not completed,
  a dependency that was not provisioned, or a state
  that was assumed present but is not.

Observable signals:
  - Task references a resource, file, or state
    that does not exist
  - A prior mandate was assumed DONE but is not
  - A dependency tool or service is not installed
    or not running

Layer:   Sequencing / Dependencies
Cause:   Planning error or incomplete prior work

Prescribed response:
  Stop. File the missing prerequisite as a blocker.
  Do not attempt to resolve the prerequisite inline —
  file a separate mandate or DIP for it.
  The current mandate resumes after the prerequisite
  is satisfied.

Back-off strategy:
  Stop. The prerequisite must exist before this
  task can proceed.

Loop permitted: NO

---

### SCOPE_OVERFLOW

Definition:
  The task has grown beyond the boundaries of the
  original mandate. The agent is attempting work that
  was not commissioned and may not be wanted.

Observable signals:
  - Implementation touches systems not in the DIP
  - Agent proposes changes beyond acceptance criteria
  - TIR describes work not in the original mandate scope
  - The agent is "while I'm in here" reasoning

Layer:   Scope / Mandate boundary
Cause:   Undisciplined expansion

Prescribed response:
  Stop the overflow work immediately.
  Complete only what is in the mandate scope.
  File a new mandate for the identified additional work.
  Do not commit overflow changes.

Back-off strategy:
  Scope reset. File and defer, do not absorb.

Loop permitted: NO (on overflow work)

---

### RATE_EXHAUSTION

Definition:
  An external API, service, or resource has hit its
  rate limit or quota. The operation will succeed
  after the rate window resets.

Observable signals:
  - HTTP 429 Too Many Requests
  - API error: rate limit exceeded, quota exhausted
  - Explicit retry-after header in response

Layer:   External API / Service
Cause:   Request volume, not logic error

Prescribed response:
  Backoff with prescribed delay.
  Read retry-after header if present.
  Default delays: 60s, 300s, 1800s (exponential).
  Log the rate limit event — it may indicate a
  design problem if it recurs.

Back-off strategy:
  Exponential backoff. Retry is appropriate.
  Do not hammer the endpoint.

Loop permitted: YES (with backoff and iteration cap)

---

### UNRECOGNIZED_PATTERN

Definition:
  The failure does not match any known mode.
  The classifier cannot determine the cause layer
  or appropriate response from available signals.

Observable signals:
  - None of the above modes match
  - The failure is inconsistent or non-reproducible
  - Cause layer is indeterminate

Layer:   Unknown
Cause:   Unknown

Prescribed response:
  One retry maximum to gather additional signal.
  If failure recurs: BLOCKER, escalate to human.
  Include: all observable signals, what was attempted,
  why no known mode matched.
  After resolution: encode as a new named mode
  in this document if the pattern is likely to recur.

Back-off strategy:
  Single retry for signal gathering only.
  Do not loop on an unclassified failure.

Loop permitted: ONCE (signal gathering only)

---

## Model-Layer Signals (Back Pressure)

The model itself is an observer. Its back-pressure
signals manifest in output text before any programmatic
hook fires. A structurally separate classifier can read
these signals; the acting agent cannot — it is inside
the contaminated context.

---

### THROTTLING

Definition:
  The model is applying friction to the acting agent's
  output. Not a refusal — a deceleration signal.

Observable signals:
  - Hedging density increasing across turns
    ("this might", "you may want to consider",
    "I should note that")
  - Unsolicited warnings inserted before executing
  - Confirmation requests the task did not require
  - Output quality declining relative to prior turns
  - Caveat-to-content ratio rising

What it means:
  The model has detected something in the context that
  makes it cautious. The cause may be context
  contamination, an approaching capability boundary,
  or accumulated failure signals.

Prescribed response:
  Treat as an early CONTEXT_CORRUPTION signal.
  Reduce scope. Simplify the next instruction.
  If throttling persists: consider context discard.

---

### JAIL_TIME

Definition:
  The model is refusing actions it previously executed.
  Context contamination has crossed a threshold —
  the model is applying broad caution to the session.

Observable signals:
  - Refusals on actions that succeeded in prior turns
  - Increasingly conservative scope interpretation
  - The Auto mode block pattern: benign subsequent
    actions refused because of earlier context
    (e.g. diagnostic command blocked after
    credential-adjacent sequence)
  - Agent output becomes generic and non-specific

Cascade property:
  Jail time is not isolated to the refused action.
  The model's caution spreads to adjacent actions.
  The contaminated context degrades ALL reasoning
  in the session, not just the specific refused action.

Prescribed response:
  Discard context. Do not attempt to reason the model
  out of jail time within the same session — this
  deepens the contamination.
  Start a fresh session.
  Package last clean state before discarding.

---

## Classification quick reference

| Mode                  | Layer              | Retry | Response        |
|-----------------------|--------------------|-------|-----------------|
| IMPLEMENTATION_ERROR  | Code               | YES   | Feedback + cap  |
| ENVIRONMENT_FAILURE   | Infrastructure     | NO    | BLOCKER         |
| SPECIFICATION_CONFLICT| Requirements       | NO    | Return Architect |
| BELOW_HORIZON         | Below visibility   | NO    | Escalate + KVM  |
| OSCILLATION           | Agent reasoning    | NO    | Force constraint |
| REGRESSION            | Code               | NO    | Rollback        |
| CONTEXT_CORRUPTION    | Context window     | NO    | Discard context |
| MISSING_PREREQUISITE  | Sequencing         | NO    | BLOCKER         |
| SCOPE_OVERFLOW        | Mandate boundary   | NO    | File + defer    |
| RATE_EXHAUSTION       | External API       | YES   | Backoff         |
| UNRECOGNIZED_PATTERN  | Unknown            | ONCE  | Signal + BLOCKER|
| THROTTLING (model)    | Model layer        | —     | Reduce scope    |
| JAIL_TIME (model)     | Model layer        | —     | Discard context |
