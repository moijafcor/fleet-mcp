# Skills Reference

CC skills are Claude Code custom commands that encapsulate harnessable role
invocations. Each skill is a Markdown file in `.claude/commands/` that loads
the correct agent protocol, resolves the mandate source, and handles board
status transitions — automatically, at session start, with a single command.

This document covers installation, the two customisation points every adopter
must update, the three-case `$ARGUMENTS` resolution pattern, the runtime
matrix, and how to extend skills for new roles.

---

## Why Skills Over Manual Context Loading

The manual approach to starting an agent session requires the operator to
remember which files to load, in what order, and how to pass the mandate
source. Each of those steps is a prompt that can be omitted or misstated.

A CC skill encodes the complete session bootstrap:

- Declares the role and its constraints
- Loads the agent protocol file and the reference library
- Resolves `$ARGUMENTS` via three-case detection
- Handles board status transitions conditionally on the resolved case
- Reads project governance from `AGENTS.md` rather than repeating it inline

The result is that `$ARGUMENTS` is the only variable the operator needs to
supply. The skill handles everything else deterministically.

Skills are the preferred invocation method for Claude Code. For Codex and
runtime-agnostic invocations, see the Runtime Matrix below.

---

## Installation

Copy the skill templates from the framework into your project's Claude Code
commands directory:

```bash
mkdir -p .claude/commands
cp docs/harness/templates/skills/*.md .claude/commands/
```

Then open each file and update the two marked placeholders (see Customisation
Points below). After customising, invoke any role with:

```bash
/project:engineer "docs/mandates/my-feature.md"
/project:engineer 190778951
/project:coder "docs/mandates/auth/login_implementation_plan.md"
/project:qa 190778951
/project:sre "docs/mandates/ops/deploy-vhost.md"
/project:security "docs/mandates/auth/login_implementation_plan.md"
/project:architect "Add rate limiting to the public API"
/project:emergency "login service is returning 500s on all POST requests"
```

---

## Customisation Points

Every skill file contains two `# REPLACE` comments. Both must be updated
before the skills are usable.

### 1. Project tracker URL pattern and fetch command (Case A)

```markdown
# REPLACE: project tracker URL pattern and fetch command
```

This comment appears in the Case A block of each skill. Replace it with the
URL pattern your board uses and the command to fetch a board item. The agent
uses this to detect whether `$ARGUMENTS` is a board item and to fetch it.

**GitHub Projects example:**

```markdown
**Case A — Board task URL or item ID**
Matches `github.com/orgs/YOUR_ORG/projects` or a bare numeric itemId.
Fetch the full item from `YOUR_ORG/projects/N` via `gh api graphql`.
Read every field, comment, and linked item.
Board status updates apply (see Entry Checklist and Handoff).
```

**Linear example:**

```markdown
**Case A — Linear issue URL or issue ID**
Matches `linear.app/YOUR_TEAM` or a bare issue ID (e.g. `ENG-123`).
Fetch the full issue via the Linear API.
Read title, description, comments, and linked items.
Board status updates apply (see Entry Checklist and Handoff).
```

Replace the detection pattern, fetch command, and any board mutation
calls throughout the file (Entry Checklist and Handoff sections) to
match your tracker's API.

### 2. Framework base path (if not docs/harness/)

```markdown
# REPLACE: framework base path (if not docs/harness/)
```

This comment appears above the reference library load list in each skill.
If you installed the framework directory somewhere other than `docs/harness/`,
update every path in the list below the comment.

**Default (no change needed if you used the standard install path):**

```markdown
- `docs/harness/agents/engineer.md`
- `docs/harness/templates/dip.md`
- `docs/harness/vendor/harnessable/references/state-machine.md`
```

**Custom base path example (if installed at `harness/`):**

```markdown
- `harness/agents/engineer.md`
- `harness/templates/dip.md`
- `harness/vendor/harnessable/references/state-machine.md`
```

---

## The Three-Case $ARGUMENTS Resolution Pattern

Every skill resolves `$ARGUMENTS` via the same three-case pattern. The agent
detects which case applies and loads the mandate accordingly.

### Case A — Board task URL or item ID

Triggered when `$ARGUMENTS` matches the board URL pattern you configured, or
is a bare item ID (numeric or otherwise, depending on your tracker).

The agent fetches the full item from the tracker API, reads all fields and
comments, and applies board status updates at each stage (Entry Checklist,
Handoff, Exit Gate).

**Examples:**

```text
/project:engineer 190778951
/project:coder https://github.com/orgs/YOUR_ORG/projects/1/items/45
```

### Case B — Local file path

Triggered when `$ARGUMENTS` starts with `docs/`, `./`, or `/`, or ends in
`.md`. The agent reads the file directly.

No board item exists. Board status mutations are skipped; intended operations
are recorded in the DIP `## Tracker Ops Log` as `Pending — no board item`.

**Examples:**

```text
/project:engineer "docs/mandates/my-feature.md"
/project:coder "docs/mandates/auth/login_implementation_plan.md"
```

### Case C — Inline description

Triggered when `$ARGUMENTS` matches neither Case A nor Case B. The argument
text is treated as the mandate description itself.

For the Engineer: the inline text becomes the DMT and the agent authors a DIP
from it. For other roles: use sparingly — a meaningful DIP or board item is
always preferable to an inline description at the Coder, QA, or Security stages.

**Example:**

```text
/project:architect "Add rate limiting to the public API — 100 req/min per token"
```

---

## Runtime Matrix

| Runtime | Invocation method |
| --- | --- |
| Claude Code | `/project:{role}` — skills in `.claude/commands/` |
| Codex | `codex/examples/` — role prompt templates |
| Either (no skills) | Load context manually at session start (see README Step 3) |

**Claude Code** uses CC skills as the primary invocation path. Skills load all
required context automatically. Install once; invoke with a single command.

**Codex** discovers `AGENTS.md` automatically at session start for persistent
repository instructions. For role-specific invocations, use the prompt
templates in `codex/examples/` or invoke via `AGENTS/skills/harnessable/SKILL.md`.

**Runtime-agnostic manual loading** is always available as a fallback. Load
context manually at session start as described in README Step 3. This is the
required path for runtimes that do not support CC skills or Codex conventions.

---

## Extending for New Roles

To add a skill for a new role:

1. Create the role protocol file at `framework/agents/{role}.md` (following
   the existing agent file conventions).
2. Create `framework/templates/skills/{role}.md` following this pattern:

   ```markdown
   You are acting as the {Role} agent. [One-sentence role definition.]

   The {input} is: $ARGUMENTS

   ---

   ## Resolving $ARGUMENTS

   **Case A — Board task URL or item ID**
   # REPLACE: project tracker URL pattern and fetch command
   [Detection and fetch instructions.]

   **Case B — Local file path**
   [Read and proceed instructions.]

   **Case C — Inline description**
   [Inline handling instructions if applicable.]

   ---

   ## Protocol

   Follow the {Role} agent protocol at `docs/harness/agents/{role}.md` exactly.

   Load project governance from `AGENTS.md`.

   Load the harnessable reference library:
   # REPLACE: framework base path (if not docs/harness/)
   - `docs/harness/agents/{role}.md`
   - [additional reference files]

   ---

   ## Entry Checklist
   [Role-specific entry checks.]

   ## [Role-specific protocol sections]

   ## Exit Gate
   [Role-specific exit conditions and board transitions.]
   ```

3. Document the new role in `framework/vendor/harnessable/KNOWLEDGE_GRAPH.yaml`
   under the `harnessable` namespace.
4. Ship the new skill file alongside the other skill templates so adopters
   get it via the standard `cp` install.

The two `# REPLACE` comments are the only project-specific content in a skill
file. Everything else reads from the protocol file and `AGENTS.md` at runtime.
