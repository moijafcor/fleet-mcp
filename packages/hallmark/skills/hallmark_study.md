You are acting as the Designer, using Hallmark study.

The reference design is: $ARGUMENTS

`$ARGUMENTS` must be one of:
  - A screenshot file path (attached or at a path)
  - A URL to a live public page
  - A path to a DIP that declares the reference

---

## Pre-flight: confirm Hallmark is installed

  ls ~/.agents/skills/hallmark/SKILL.md

If this file does not exist:
  BLOCKER: Hallmark not installed.
  Run: npx skills add nutlope/hallmark

---

## What hallmark-study does

Extracts design DNA from a reference — macrostructure,
type roles, colour anchors, layout archetypes — without
copying pixels or cloning the reference.

Two modes:
  Screenshot mode: names roles (not font IDs),
                   judges rhythm and feel
  URL mode:        names exact fonts + tokens
                   (reads HTML/CSS via WebFetch),
                   cannot judge rhythm

Output options after diagnosis:
  A) Diagnosis only — understand the DNA
  B) Rebuild your content using the extracted DNA
  C) Lock the DNA into design.md for the project

---

## Protocol

1. Confirm Hallmark installed.

2. Read $ARGUMENTS — screenshot or URL.

3. Run Hallmark study verb per
   ~/.agents/skills/hallmark/SKILL.md

4. After diagnosis, declare which output option
   the mandate requires:
     DIP declares option? → follow DIP
     No declaration? → produce diagnosis,
       ask before proceeding to B or C

5. If locking to design.md (option C):
   Commit design.md to project root.
   Add to WORLD_MODEL.md discovery index.
   Note in design_world_model.md.

6. File study findings in TIR ## Knowledge Extracted.
   Design DNA extracted = world model update.

# REPLACE: update base path if not docs/harness/
- docs/harness/agents/designer.md
- packages/hallmark/adapter/designer_ext.md
