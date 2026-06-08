# AGENTS.md
# Template — copy to your project root as AGENTS.md and fill in the # REPLACE markers.

## Harnessable protocol

This project uses Harnessable: operational governance for autonomous
agents. Full documentation: docs/harness/vendor/harnessable/references/

Before non-trivial work:

1. Identify active role: Architect, Engineer, Coder, SRE, QA, Security,
   Reviewer, Inspector, Analyst, Orchestrator, Narrator, or Emergency Responder.
2. Do not combine Coder and QA, or SRE and QA, in the same pass.
   Security must not be the Coder, SRE, or QA for the same mandate.
3. For implementation work, require a Design Implementation Plan before
   editing code or touching live systems.
4. Record deviations, blockers, and verification evidence.
5. Do not claim completion without running the stated checks.

## Project Tracker

# REPLACE: declare your board tool and integration method.
# Examples:
#   tool: GitHub Projects
#   project_url: https://github.com/orgs/{org}/projects/{n}
#   item_fetch: gh issue view {id}
#   status_update: gh project item-edit ...
#
#   tool: Linear
#   project_url: https://linear.app/{org}/project/{slug}
#   item_fetch: ...

## Knowledge Graph

Framework graph: docs/harness/vendor/harnessable/KNOWLEDGE_GRAPH.yaml
Project graph:   docs/knowledge-graph.yaml (if present)

Load both at session start. Resolve all domain terms against the
project graph before acting. File ONTOLOGY_GAP for any concept
encountered that is not declared in the graph.

## Risk Profile

# REPLACE: declare your project's risk tolerance and safety constraints.
# risk_level: high | medium | low
# safety_constraints:
#   - [constraint description]

## Locale and Voice

# REPLACE: declare language, tone, and audience for this project.
# locale: en-US
# voice: professional | casual | technical
# audience: [primary audience description]

## Blocked

# List actions the agent must never take on this project.
# The bouncer.py hook enforces this list.
- Do not force-push
- Do not delete branches
- Do not run destructive database commands (DROP, TRUNCATE, WHERE-less DELETE)
- Do not read or expose secrets unless explicitly required
- Do not send external communications without human approval

## Completion Gate

# Commands that must pass before the agent reports work as complete.
# REPLACE: add project-specific verification commands.
# - make test
# - make lint
# - python3 -m pytest

## MCP Servers

# REPLACE: declare MCP servers available to agents in this project.
# Remove this section if no MCP servers are configured.
#
# Example:
# server_name:
#   url: {server URL or socket path}
#   purpose: {what this server provides}

## Communication Channels

# Declare the communication destinations the Narrator produces for.
# The Narrator reads this section before writing anything.
# REPLACE: adapt to your project's actual channels or remove section.

# docs_site:    {URL}  ({format: MDX | Markdown | HTML})
# api_docs:     {URL}  ({format: OpenAPI changelog | Markdown})
# landing_page: {URL}  ({sections: hero | features | pricing | cta})
# blog:         {URL}  ({format: MDX | long-form Markdown})
# email:        ({audiences: tenant | prospect | partner})
# social:       ({platforms: LinkedIn | X | newsletter})
# press:        ({format: press release})
# partner:      ({format: talking points | sales enablement})
# executive:    ({format: impact summary})
