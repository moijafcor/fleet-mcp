# AGENTS.md

## Project Identity
Domain: developer-tooling
Team: small-team
Timezone: America/Toronto

## Project Tracker
Tool: GitHub Issues
Integration: manual
Task URL pattern: https://github.com/users/moijafcor/projects/2?pane=issue&itemId={id}

## Locale
Language: en-CA
Date format: ISO 8601

## Voice
Style: engineering
Formality: high
Verbosity: standard

## Risk Profile
Default posture: pragmatic
Escalation: file a BLOCKER field discovery and stop when: a fleet/ YAML edit would
remove a Landmine entry (landmines must be explicitly approved for removal), or when
a change to src/models/ would break the YAML schema contract with downstream consumers.

## Knowledge Graph
Framework graph: docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml
Project graph:   docs/knowledge-graph.yaml

## Allowed
- Read any file in the repository
- Write and edit source files, tests, and fleet/ YAML data
- Run pytest suites
- Run linters (ruff) and type checkers (mypy)
- Run git status, git diff, git log, git add, git commit

## Ask First
- Any change to docs/knowledge-graph.yaml (schema changes affect the static layer contract)
- Any change to .claude/settings.json or .claude/settings.local.json
- Any push to the remote

## Blocked
- `git push --force`
- `git reset --hard`
- `git clean -f`
- `rm -rf`

## Completion Gate
- python3 -m pytest tests/ -x -q --tb=short
