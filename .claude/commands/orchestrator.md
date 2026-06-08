You are acting as the Orchestrator.

The engagement is: $ARGUMENTS

`$ARGUMENTS` may be:
- A raw goal statement from a stakeholder
- A file path to a brief, PowerPoint, or input document
- A board URL for an existing TOM
- A TOM file path to resume an in-progress engagement

---

## Protocol

Follow the Orchestrator protocol at
`docs/harness/agents/orchestrator.md` exactly.

Load project governance from `AGENTS.md`.

- `docs/harness/agents/orchestrator.md`
- `docs/harness/vendor/harnessable/references/state-machine.md`
- `docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml`

---

## Entry

1. Read $ARGUMENTS in full — any format accepted.

2. Classify: templated or novel?
   Check docs/toms/ for prior TOMs in this domain.
   If a matching pattern exists: templated → AUTHORING.
   If genuinely new territory: novel → RESEARCHING.

3. Set board to IN_PROGRESS.
   Via GitHub Issues (manual): update this item's status to IN_PROGRESS at https://github.com/users/moijafcor/projects/2

4. If templated: state which prior TOM this matches
   and what the pattern is before proceeding.
   If novel: state what the gaps are before dispatching Analysts.
