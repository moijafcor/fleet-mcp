AI coding agents are stateless and repo-scoped. Your fleet isn't. `fleet-mcp` is an opinionated MCP server that maintains a living Knowledge Graph of your multi-app SaaS architecture — modelling the relationships between services, the contracts at their boundaries, the shared concerns that cross them, and the things that silently break other apps when touched naively. Wire it once; every agent session across every codebase in your fleet inherits full situational awareness.

## Wiring to Claude Desktop

### stdio (local, recommended for Phase 1)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or equivalent:

```json
{
  "mcpServers": {
    "fleet": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/absolute/path/to/fleet-mcp"
    }
  }
}
```

Restart Claude Desktop after editing. The five `fleet_*` tools will be
available in every session.

### HTTP (optional, for team sharing)

```bash
mcp run src/server.py --transport streamable-http --port 8096
```

Point Claude Desktop at `http://localhost:8096/mcp`.

## Development Workflow

Changes to this project follow the [Harnessable](docs/harness/QUICKSTART.md) agent development pipeline:
`/engineer` → `/coder` → `/qa`. See [`docs/harness/QUICKSTART.md`](docs/harness/QUICKSTART.md) for the full quickstart.
