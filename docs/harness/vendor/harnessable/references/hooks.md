# Hooks Reference

Hooks are the operational implementation of the Enforcement Layer. They turn
the advisory policies in AGENTS.md into deterministic controls that run
regardless of what the model decides.

This document maps Harnessable framework concepts to Claude Code lifecycle
events and to the hook scripts in `hooks/`.

---

## The Protocol

When a hook fires, the agent pauses and feeds a JSON payload to the hook
script via stdin. The script responds with an exit code:

| Exit code | Meaning |
| --- | --- |
| `0` | Allow — execution proceeds |
| `2` | Block — tool call is cancelled; stderr is fed back to the agent as the reason |
| Any other | Treated as an error; behaviour depends on Claude Code version |

The agent reads the stderr message on exit 2 and understands why it was
blocked. It can then try a different approach. This is the core of the
"deterministic bouncer" pattern.

---

## The Dispatcher

`hooks/run.py` is the single entry point wired in `.claude/settings.json`.
It discovers every `*.py` file in the given event subdirectory, sorted
alphabetically, and runs each one in order, passing the original stdin
payload to each script individually.

```text
Claude Code fires event
        │
        ▼
  hooks/run.py <event_subdir>
        │
        ├─► pre_tool_use/bouncer.py        ← stdin JSON
        ├─► pre_tool_use/secrets_guard.py  ← stdin JSON
        └─► pre_tool_use/…                 ← any new scripts, alphabetical
```

**To add a new check:** drop a `.py` file into the relevant subdirectory.
No changes to `settings.json` are required.

**Execution model:** `run.py` stops at the first script that exits 2 and
forwards its stderr. Remaining scripts in that event's directory are not run.
Scripts that want fail-open behaviour (e.g. loggers) should handle their own
errors and always exit 0.

**Each script is independently runnable and testable:**

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"},"cwd":"/tmp"}' \
  | python3 hooks/pre_tool_use/bouncer.py
```

**When testing through the dispatcher, use `printf` with a standalone pipeline — not a compound script:**

```bash
printf '{"tool_name":"Bash","tool_input":{"command":"git push origin main --force"}}' \
  | python3 hooks/run.py pre_tool_use
```

Guards that inspect command content (bouncer, git_guard, database_guard) scan the
outer shell command string. If a test payload is embedded inside a compound script
that itself contains a blocked pattern, the guard blocks the test invocation — not
the JSON payload being tested. Use `printf '…' | python3 hooks/run.py` as a
standalone pipeline.

---

## Lifecycle Events

### PreToolUse

Fires after the model decides to act but before anything executes. This is
where blocking happens.

**Harnessable concepts served:** Blocked actions, Ask-First enforcement,
SecretsGuard.

**Scripts in `hooks/pre_tool_use/`:**

| Script | Purpose |
| --- | --- |
| `bouncer.py` | Reads `## Blocked` from AGENTS.md and blocks matching Bash commands |
| `secrets_guard.py` | Hardcoded patterns that block secret file reads and credential exfiltration |

**Payload fields used:**

```json
{
  "session_id": "…",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf /tmp/build" }
}
```

---

### PostToolUse

Fires immediately after a tool finishes executing (whether it succeeded or
failed). This is where audit logging happens.

**Harnessable concepts served:** Audit trail, TIR evidence, observability.

**Scripts in `hooks/post_tool_use/`:**

| Script | Purpose |
| --- | --- |
| `audit_logger.py` | Appends a structured JSON entry to `.harnessable/audit.log` |

**Payload fields used:**

```json
{
  "session_id": "…",
  "cwd": "/path/to/project",
  "hook_event_name": "PostToolUse",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" },
  "tool_response": { "output": "…", "exit_code": 0 }
}
```

---

### Stop

Fires when the agent finishes a turn. If the hook exits 2, the agent is
forced to continue working until the gate passes.

**Harnessable concepts served:** Pre-Completion Hook Runner (from
`agents/coder.md`), completion verification gates.

**Scripts in `hooks/stop/`:**

| Script | Purpose |
| --- | --- |
| `completion_gate.py` | Runs every command in AGENTS.md `## Completion Gate`; blocks completion if any fail |

**Payload fields used:**

```json
{
  "session_id": "…",
  "cwd": "/path/to/project",
  "hook_event_name": "Stop"
}
```

---

## Event-to-Layer Mapping

```text
AGENTS.md ## Blocked  ──────────────► PreToolUse  ► bouncer.py
AGENTS.md ## Ask First (future)  ───► PreToolUse  ► (add a new script)
Credential files & exfil patterns ──► PreToolUse  ► secrets_guard.py
Tool invocations (all tools) ───────► PostToolUse ► audit_logger.py
AGENTS.md ## Completion Gate ───────► Stop        ► completion_gate.py
```

---

## Installation

### 1. Copy the hooks directory

Place `hooks/` somewhere the agent can reach it. A common location:

```text
your-project/
└── docs/
    └── harness/
        └── hooks/         ← copy here
```

### 2. Wire hooks in `.claude/settings.json`

Copy `hooks/claude_code_settings_template.json` to `.claude/settings.json` in your
project root. The template wires all three events through the dispatcher:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 docs/harness/hooks/run.py pre_tool_use" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "python3 docs/harness/hooks/run.py post_tool_use" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "python3 docs/harness/hooks/run.py stop" }
        ]
      }
    ]
  }
}
```

Adjust the base path if you placed `hooks/` elsewhere.

### 3. Configure AGENTS.md

The hooks are AGENTS.md-driven. Two sections control their behaviour:

#### `## Blocked`

The bouncer reads this section and blocks any Bash command that contains a
listed pattern. Write patterns as command fragments, not prose:

```markdown
## Blocked

- `rm -rf`
- `DROP TABLE`
- `git push --force`
- `git push -f`
- `truncate -s 0`
```

Patterns are matched as case-insensitive substrings of the command string.
If a pattern is written in prose ("Force push to main"), it will not match
the actual command (`git push --force`). Write the literal fragment.

Backtick-quoted items in the list (`` `rm -rf` ``) use the backtick contents
as the pattern; unquoted items use the full line text.

#### `## Completion Gate`

The `completion_gate.py` hook reads this section and runs each listed command
before the agent can finish a turn. If any command exits non-zero, the agent
is forced to keep working.

Each command is domain-specific — write whatever verification makes sense for
your context:

Software project:

```markdown
## Completion Gate

- npx eslint src/
- npx tsc --noEmit
- npx jest --passWithNoTests
```

Executive assistant:

```markdown
## Completion Gate

- python3 scripts/verify_recipients.py
- python3 scripts/check_calendar_conflicts.py
```

Legal review agent:

```markdown
## Completion Gate

- python3 scripts/check_citations.py
- python3 scripts/flag_unresolved_references.py
```

If this section is absent from AGENTS.md, the completion gate is a no-op.

### 4. Audit log

The audit logger writes to `.harnessable/audit.log` at the project root
(one JSON object per line). Add it to `.gitignore` to exclude from version
control, or track it for compliance:

```text
# .gitignore
.harnessable/audit.log
```

---

## Extending the Hooks

## Pre-built Guards

The following scripts ship in `hooks/pre_tool_use/` and can be activated by
simply placing them in the directory. Each is independently auditable,
independently testable, and covers a distinct risk domain.

### `bouncer.py` — Policy enforcement (AGENTS.md-driven)

Reads the `## Blocked` list from AGENTS.md and blocks any Bash command
containing a listed pattern. This is the configurable policy layer: teams
write their rules once in AGENTS.md and the bouncer enforces them.

### `secrets_guard.py` — Credential protection (hardcoded floor)

Blocks commands that read or transmit sensitive files (`.env`, `.pem`, `.key`,
`credentials.json`) or match credential exfiltration patterns (`printenv`,
`echo $SECRET`, `curl --header Authorization`). Runs regardless of AGENTS.md.

### `database_guard.py` — Data destruction prevention

Blocks destructive SQL regardless of how it reaches the shell:

| Blocked | Why |
| --- | --- |
| `DROP TABLE`, `DROP DATABASE`, `DROP SCHEMA` | Irreversible schema destruction |
| `TRUNCATE` | Removes all rows, often outside transaction scope |
| `DELETE FROM x` without `WHERE` | Deletes every row in the table |
| `UPDATE x SET` without `WHERE` | Overwrites every row in the table |

The WHERE-clause check is the key insight: `DELETE FROM orders` is
catastrophic; `DELETE FROM orders WHERE id = 42` is routine. A simple
substring match cannot distinguish them — this guard does.

### `git_guard.py` — History and branch protection

Blocks git operations that destroy shared history or work with no recovery path:

| Blocked | Why |
| --- | --- |
| `git push --force` / `-f` | Rewrites shared remote history; destroys others' commits |
| `git push origin :<ref>` | Deletes a remote branch or tag |
| `git reset --hard` | Permanently discards all uncommitted changes |
| `git branch -D` | Force-deletes a branch even with unmerged commits |
| `git clean -f` | Permanently deletes all untracked files |
| `git rebase` onto shared branches | Rewrites already-published commits |
| `git tag -d` | Deletes a tag without removing the remote counterpart |

Each block message names the safe alternative (e.g. `--force-with-lease`,
`git branch -d`, `git stash`, `git clean -n`) so the agent can immediately
propose a corrected approach.

### `communication_guard.py` — Unauthorized external communications

Prevents agents from sending messages on behalf of a human without approval.
Directly relevant to executive assistant, chief-of-staff, legal, and
customer-facing agents where an unsanctioned message carries reputational
or legal risk.

| Blocked | Platforms covered |
| --- | --- |
| CLI email tools | `sendmail`, `mailx`, `mutt`, `msmtp`, `swaks` |
| SMTP in scripts | `smtplib.SMTP`, direct SMTP connections |
| Email delivery APIs | SendGrid, Mailgun, Postmark, AWS SES |
| Chat | Slack `chat.post`, `chat.update`, `chat.delete` |
| Microsoft 365 | Graph API `sendMail`, `events` (calendar writes) |
| Google Workspace | Gmail `messages.send`, Calendar event writes |
| SMS / voice | Twilio, MessageBird, Vonage, Bandwidth |
| Generic outbound POST | curl/wget POSTs with message-shaped payloads |

The agent is instructed to draft the message and present it for human
review — not to simply fail. The block message explains exactly why.

---

## Extending the Hooks

Because `run.py` discovers scripts dynamically, extending any event means
writing a new script and placing it in the relevant directory.

### Add a PreToolUse check

Create `hooks/pre_tool_use/my_check.py`. It must:

1. Read the JSON payload from stdin
2. Exit 0 to allow or exit 2 to block (with a reason on stderr)

```python
#!/usr/bin/env python3
import json, sys

hook_data = json.load(sys.stdin)
command = hook_data.get('tool_input', {}).get('command', '')

if 'something_forbidden' in command:
    sys.stderr.write("[MyCheck] Blocked: reason.\n")
    sys.exit(2)

sys.exit(0)
```

Alphabetical order determines execution sequence. Prefix with a number
(`10_my_check.py`) to control position relative to existing scripts.

### Add a PostToolUse logger

Create `hooks/post_tool_use/my_logger.py`. Loggers should always exit 0
even on internal failure — a logging error must never block the agent.

### Routing Ask-First actions for human approval

Add `hooks/pre_tool_use/ask_first.py`. Parse `## Ask First` from AGENTS.md.
Instead of blocking outright, write the pending action to
`.harnessable/approvals/` and exit 2 with a message like:
"Awaiting human approval — check .harnessable/approvals/pending.json".
A separate process monitors the queue and resumes the session when approved.

### Add a PostToolUseFailure hook

Add `PostToolUseFailure` to `settings.json` pointing to a new
`hooks/post_tool_use_failure/` directory. The payload is identical to
PostToolUse. Use it to page on-call or open a ticket on tool failures.

---

## Design Decisions

**One dispatcher, not one entry per script in settings.json.**
Adding a check requires dropping a file, not editing settings. This follows
the Unix convention of directories as extension points.

**Alphabetical execution order.**
Deterministic and obvious. Use numeric prefixes (`10_`, `20_`) when order
matters between scripts in the same directory.

**Dispatcher stops on first exit 2.**
An enforcement failure is a hard stop. There is no value in running further
checks once a block is issued — the agent will not proceed anyway.

**Hooks fail open on internal error.**
If a script crashes (bad JSON, missing import), it exits 0 and execution
continues. The agent should not be blocked by a defective hook. Log the
exception to stderr for visibility.

**The audit logger never blocks.**
A logging failure must never interrupt the agent. The logger always exits 0.

**Bouncer and SecretsGuard are separate scripts.**
The bouncer is policy-driven (AGENTS.md). The SecretsGuard is a hardcoded
floor that applies regardless of policy. Keeping them separate makes each
independently auditable and testable.

**Completion gate is opt-in.**
No `## Completion Gate` section means no gate. Teams adopt it incrementally
rather than being forced into a configuration they haven't designed.
