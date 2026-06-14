# PACKAGE.md
#
# Harnessable package adapter manifest.
# Declares what this adapter wraps and what it
# contributes to the harnessable pipeline.
#
# This file describes the adapter — not the package.
# The package lives at install_path below.

---

name:        # REPLACE: package name (e.g. hallmark)
version:     # REPLACE: adapter version (e.g. 1.0.0)
source:      # REPLACE: upstream source (e.g. nutlope/hallmark)
install_cmd: # REPLACE: how to install the package
             # (e.g. npx skills add nutlope/hallmark)
install_path: # REPLACE: where the package lands after install
              # (e.g. ~/.agents/skills/hallmark/)
adapter_path: packages/ # REPLACE: adapter location in project
                         # (e.g. packages/hallmark/)

description: |
  # REPLACE: what this package provides and why
  # it is useful in a harnessable pipeline

capabilities:
  # REPLACE: list what the package can do
  # - design_execution
  # - slop_gate_verification
  # - design_dna_extraction

---

harnessable:

  extends_role:   # REPLACE: which harnessable role this
                  # package extends (e.g. Designer)
                  # or 'none' if standalone

  adds_skills:    # REPLACE: skill wrappers this adapter adds
                  # These appear in Engineer roster scan
    # - packages/{name}/skills/{name}.md
    # - packages/{name}/skills/{name}_{verb}.md

  adds_rubric:    # REPLACE: path to Rubric additions
                  # or 'none'
    # packages/{name}/adapter/rubric.md

  adds_world_model: # REPLACE: domain world model template
                    # or 'none'
    # packages/{name}/adapter/{domain}_world_model.md

  requires:       # REPLACE: what must be installed for
                  # this adapter to function
    # - npx skills add {source}
    # - pip install {package}

---

## Verification

# How to confirm the package is correctly installed:
#
# REPLACE: command that confirms installation
# e.g.:
#   ls ~/.agents/skills/hallmark/SKILL.md
#   npx hallmark --version

---

## Notes

# REPLACE: anything agents need to know about
# using this package within harnessable sessions
