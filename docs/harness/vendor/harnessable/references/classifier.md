# Classifier — Architectural Pattern

The classifier is not a role. It is a pattern: a
structurally separate observer that reads failure
signals from an acting agent's session, matches them
against the error mode taxonomy, and routes to the
prescribed response.

No autonomous loop is safe without a classifier.
An acting agent in a loop cannot observe its own
state reliably. Its context is the evidence — not
a communication channel. The classifier must be
separate from that context entirely.

---

## Core principle

Failure is information. The correct response to any
failure is first to classify it, then to act.

An acting agent that retries without classification
is not intelligent — it is persistent. Persistence
against an environmental failure, a below-horizon
failure, or a context corruption event does not
converge. It accumulates damage.

The classifier is the mechanism that converts failure
signals into classified modes and routes each mode to
its prescribed response.

---

## The separation requirement

The classifier must hold a fresh context with no
shared contamination from the acting agent's session.

This is not a preference — it is structural.

An acting agent that has been looping has accumulated
context that degrades its reasoning in ways it cannot
observe or report. It may cite its own prior wrong
output as justification. It may repeat approaches
that have already failed. It may show back-pressure
signals — increasing hedging, refusals on previously
executed actions — that are invisible from inside the
contaminated context.

The classifier's fresh read IS the treatment.
Injecting more instructions into the contaminated
session deepens corruption rather than resolving it.

**Requirement:** The classifier session must be opened
fresh. It reads the acting agent's output as an
artifact — not as a conversation participant.

---

## Stop authority

The classifier holds unconditional stop authority
over the acting agent's loop.

Stop authority means:
  — The classifier can terminate the loop at any
    iteration regardless of iteration count
  — The classifier's stop decision overrides any
    instruction the acting agent has received
  — Stop is not a failure of the loop — it is often
    the correct output of a well-functioning classifier

Stop authority is what distinguishes a classifier
from a reviewer. A reviewer observes and advises.
A classifier observes, classifies, and can terminate.

Without stop authority the classifier is advisory.
Advisory is insufficient for runaway prevention.

---

## Observability layers

The classifier reads two layers of signal:

### Layer 1 — Programmatic signals

  Exit codes, test results, lint output, Completion
  Gate pass/fail, tool call results.
  Observable by hooks and automated checks.
  Fires after failure is complete.

### Layer 2 — Model behaviour signals (back pressure)

  Hedging density, refusal frequency, output quality
  trajectory, unsolicited warning insertion.
  Observable only by a fresh-context reader.
  Fires BEFORE programmatic failure — the earliest
  warning in the stack.

The acting agent cannot report its own back-pressure.
It is inside the contaminated context.
The classifier reads both layers. Programmatic signals
confirm. Model behaviour signals warn early.

**THROTTLING** — hedging rising, caveats multiplying,
unsolicited warnings, confirmation requests the task
did not require. Early signal of context contamination.
Prescribed response: reduce scope, simplify next
instruction. If throttling persists: context discard.

**JAIL_TIME** — refusals on previously executed actions,
increasingly conservative scope interpretation.
Cascade property: jail time is not isolated to the
refused action. The model's caution spreads to adjacent
actions. The contaminated context degrades ALL reasoning
in the session.
Prescribed response: discard context. Do not negotiate
the model out of jail time — this deepens contamination.

---

## Visibility horizon

Both the acting agent and the classifier have a
visibility horizon — a layer below which neither can
observe the cause of a failure.

```
Layer 0  Hardware          ← cause may live here
Layer 1  Firmware/BIOS
Layer 2  Bootloader
Layer 3  Kernel/initrd
─────────────────────────── typical visibility horizon
Layer 4  OS / systemd      ← agent operates here
Layer 5  Network stack
Layer 6  Services
Layer 7  Application
─────────────────────────── model behaviour layer
Layer 8  Model reasoning   ← back-pressure signals here
```

A BELOW_HORIZON failure produces symptoms at the
observable layer (SSH timeout, host unreachable) while
the cause exists below it (boot stack broken, disk
by-id path corrupted after hot-swap).
Critical: Agent capability is not the limitation.
A CC session can navigate KVM consoles, interpret boot
output, recompile bootloaders, and execute full recovery
at layer 2. The limitation is pattern recognition —
the agent does not know to look below its horizon
because the symptom pattern has not been matched to
its cause layer.
If the pattern exists in WORLD_MODEL.md ## Failure
Patterns, the agent can execute the recovery autonomously
once it recognises the match. If the pattern does not
exist, no amount of retrying at the observable layer
will reveal a cause that lives below it.

Classifier response to BELOW_HORIZON:
  Do not retry at the observable layer.
  Check WORLD_MODEL.md for matching pattern.
  If match: route to documented recovery path.
  If no match: package observable state and escalate.

Escalation package for BELOW_HORIZON:
  Observable symptoms (exact)
  Last known good state (timestamp)
  All attempted actions (what, when, result)
  Exhaustion evidence ("no layer N cause found")
  Access request (KVM, IPMI, rescue mode, console)
  Stop signal: no further automated action

---

## Back-off strategy

Back-off is not the same as retry.
Retry: attempt the same operation again.
Back-off: stop, assess, change approach or escalate.
The error mode taxonomy declares per mode whether
retry is permitted. Where retry is not permitted,
the correct back-off strategy is:

  Stop all action on the failing path
  Package the observable state completely
  Declare what is needed to proceed
  (lower-layer access, prerequisite, human decision)
  Do not consume further time at the wrong layer

Back-off without a package is just stopping.
Back-off with a package is actionable escalation.
The difference is whether the human who receives
the escalation can act on it immediately.

---

## Classification protocol

When the classifier observes a failure:

  Collect all observable signals at both layers
  (programmatic + model behaviour)
  Match against error-modes.md
  If match: apply prescribed response per mode
  If no match: treat as UNRECOGNIZED_PATTERN —
  one retry for signal gathering, then BLOCKER
  Declare the classification explicitly before
  routing — do not act without declaring

Classification declaration format:

  Failure mode:        {mode name}
  Signals matched:     {list of observable signals}
  Layer:               {where cause lives}
  Loop permitted:      YES / NO
  Prescribed response: {from error-modes.md}
  Action:              {what the classifier is doing}

---

## Harnessable instantiations

The classifier pattern is instantiated three ways
in harnessable, appropriate to risk level:

### QA role (Rubric loop)

Used for: implementation correctness verification.
Separation: fresh CC session, reads TIR as artifact.
Stop authority: issues FAIL / NEEDS_REVISION.
Back-pressure reading: implicit in QA evaluation.
Loop: human-gated — board state change required
to re-enter Coder/SRE session.

### Human (board gate)

Used for: all non-trivial mandate transitions.
Separation: inherent — human holds external context.
Stop authority: unconditional.
Back-pressure reading: human observes session output.
Loop: explicit human decision to re-open session.
This is not a limitation — for high-stakes production
work, the human gate IS the feature.

### Dedicated observer session (high-risk loops)

Used for: automated loops with real-world side effects
(infrastructure changes, API mutations, deployments).
Separation: fresh CC session with no shared context.
Stop authority: observer session can terminate loop
by filing BLOCKER or alerting human.
Back-pressure reading: observer reads acting agent
output across iterations for model behaviour signals.
Escalation: observer packages state and surfaces to
human when mode is Loop permitted: NO.

---

## When a loop is safe

A loop is safe when ALL of the following are true:

  A structurally separate classifier exists
  The classifier holds stop authority
  The failure mode is classified as
    Loop permitted: YES
  The classifier reads both observability layers
  An iteration cap is declared and enforced
  The world state is not degrading between
    iterations (each retry is safe to attempt)

If any of these conditions is not met, the loop
is not safe. Stop and escalate.

---

## What the classifier is not

Not a retry wrapper.
Not a reviewer that advises but cannot stop.
Not the acting agent reading its own output.
Not a programmatic hook (hooks are Layer 1 only —
they cannot read model behaviour signals).
Not optional for any loop with real-world side effects.
