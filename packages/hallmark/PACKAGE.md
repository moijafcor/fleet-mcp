# PACKAGE.md — hallmark adapter

name:         hallmark
version:      1.1.0
source:       nutlope/hallmark
pinned_commit: aeb42fb354ff4efa36ab475773a082315a3af2ce
install_cmd:  git clone https://github.com/nutlope/hallmark.git ~/.agents/skills/hallmark && git -C ~/.agents/skills/hallmark checkout aeb42fb354ff4efa36ab475773a082315a3af2ce
install_path: ~/.agents/skills/hallmark/
adapter_path: packages/hallmark/

description: |
  Anti-AI-slop design skill by Nutlope / Together AI.
  Provides design execution, 65-gate slop verification,
  and design DNA extraction from screenshots or URLs.
  22 themes across 4 genres, 21 named macrostructures,
  project memory via .hallmark/log.json.

capabilities:
  - design_execution
  - slop_gate_verification
  - design_dna_extraction
  - project_memory
  - portable_design_system (design.md)

---

harnessable:

  extends_role:   Designer

  adds_skills:
    - packages/hallmark/skills/hallmark.md
    - packages/hallmark/skills/hallmark_study.md

  adds_rubric:
    packages/hallmark/adapter/rubric.md

  adds_world_model:
    packages/hallmark/adapter/design_world_model.md

  requires:
    - governed: Provisioned via moilab Ansible role (roles/moilab/tasks/skills.yml)
    - pinned_commit: aeb42fb354ff4efa36ab475773a082315a3af2ce
    - verify: ls ~/.agents/skills/hallmark/SKILL.md

---

## Verification

  ls ~/.agents/skills/hallmark/SKILL.md \
    && echo "Hallmark: installed" \
    || echo "Hallmark: NOT installed"

  git -C ~/.agents/skills/hallmark log -1 --format="%H" \
    | grep -q "aeb42fb354ff4efa36ab475773a082315a3af2ce" \
    && echo "Hallmark: pinned commit confirmed" \
    || echo "Hallmark: WRONG COMMIT"

## Notes

Hallmark's project memory lives in .hallmark/log.json
at the project root. The Dreamer reads this file as a
design-domain corpus input — design decisions, themes,
macrostructures, and brief summaries accumulated across
sessions. Do not delete .hallmark/log.json between
sessions; it is the design equivalent of WORLD_MODEL.md.

The /hallmark-study verb should run BEFORE /hallmark
when executing a design mandate that has a reference
design or existing brand. Study extracts the DNA;
hallmark executes against it.

Governed installation: this skill is provisioned by the moilab Ansible role
(roles/moilab/tasks/skills.yml) at pinned commit aeb42fb. Never install via
`npx skills add` in a live agent session — the auto-mode classifier will
deny it as Self-Modification / Untrusted Code Integration.
