# Designer role extension — Hallmark

This file extends the Designer role protocol when
the Hallmark package is installed. Read alongside
docs/harness/agents/designer.md — this extension
does not replace it.

## Extended tool surface

In addition to the Designer's base tool surface
(svgo, cairosvg, ImageMagick, Inkscape, ffmpeg):

  hallmark           design execution
                     → /hallmark {brief or DIP}

  hallmark study     DNA extraction from reference
                     → /hallmark-study {screenshot or URL}

  design.md          portable design system
                     → project root when locked

## When to use hallmark vs execute from spec

**Use /hallmark when:**
  The mandate requires a new UI component, page,
  or design artifact and the spec describes
  content + constraints (not exact visual execution)

**Use /hallmark-study first when:**
  A reference design or existing brand exists
  Study extracts the DNA → then hallmark executes
  against it

**Execute from spec (base Designer, no Hallmark) when:**
  The mandate provides exact coordinates, exact
  SVG geometry, exact pixel values
  (logomark production, favicon pipeline, icon sets)
  Hallmark's design intelligence is not needed —
  precision execution is

## Reconnaissance pass — study before building

For any mandate involving a new design direction:

  Step 0 (pre-execution):
    /hallmark-study {reference or existing brand}
    → produces diagnosis report
    → optionally locks to design.md
    → then /hallmark executes against the system

For mandates with exact specifications:
  Skip study — execute directly

## design.md as Asset Package input

When Hallmark locks a design system to design.md:
  design.md becomes an input to subsequent Designer
  sessions, not just an output
  Every /hallmark run defers to it
  The Asset Package (AP) should reference design.md
  as the brand system source of truth

## .hallmark/log.json — design memory

Hallmark writes to .hallmark/log.json after each run.
The Dreamer reads this as a design-domain corpus input.

Do not delete .hallmark/log.json.
It is the design equivalent of WORLD_MODEL.md
failure patterns — accumulated decisions that
prevent repetition and inform future sessions.

The Dreamer reads:
  .hallmark/log.json → design decisions corpus
  world_models/design_world_model.md → design patterns
