# design_world_model.md
#
# Design domain world model.
# Records design decisions, brand tokens, study DNA
# extractions, and Hallmark session history for
# this project.
#
# Populated by Designer sessions using Hallmark.
# Read by the Dreamer as design-domain corpus.
# Complements .hallmark/log.json (Hallmark's own memory).

---

## Brand system

# REPLACE: core brand decisions — fill after first
# /hallmark-study or after design.md is locked

# typography:
#   body:        REPLACE (e.g. Geist, Inter, system-ui)
#   display:     REPLACE (e.g. Fraunces, Playfair)
#   mono:        REPLACE (e.g. Geist Mono)
#   wordmark:    REPLACE (may differ from body)
#
# colour:
#   primary:     REPLACE (hex)
#   accent:      REPLACE (hex)
#   background:  REPLACE (hex)
#   ink:         REPLACE (hex)
#   genre:       REPLACE (editorial | modern-minimal |
#                          atmospheric | playful)
#
# design_system: REPLACE (path to design.md or 'none')

---

## Macrostructure history

# Hallmark picks a macrostructure per build.
# Record here to track what has been used.
# The Dreamer reads this to surface repetition.
#
# Format:
# - date: YYYY-MM-DD
#   mandate: path/to/dip.md
#   macrostructure: REPLACE (e.g. Bento Grid)
#   theme: REPLACE (e.g. Studio)
#   genre: REPLACE

---

## Study DNA extractions

# DNA extracted by /hallmark-study from reference designs.
# Each entry records what was learned.
#
# ### Study: {short name}
#   Date:          YYYY-MM-DD
#   Source:        {URL or screenshot path}
#   Macrostructure: REPLACE
#   Type roles:    REPLACE (body, display, mono)
#   Colour anchor: REPLACE
#   Layout notes:  REPLACE
#   Locked to design.md: YES / NO
#   Mandate:       path/to/dip.md

---

## Known design edge cases

# Non-obvious design facts for this project.
# e.g. "wordmark must never use the body typeface"
# e.g. "dark mode inverts the accent, not the primary"

---

## Related world models

# → world_models/fleet_world_model.md
# → world_models/vendor_world_model.md
