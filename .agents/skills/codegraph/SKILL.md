---
name: codegraph
description: Fast pre-indexed code knowledge graph for semantic code exploration, symbol tracing, call graph navigation, and blast radius analysis. Use when analyzing codebase structure, locating symbol definitions, tracing dependencies, or understanding component flows.
---

# CodeGraph — Semantic Code Intelligence

CodeGraph provides pre-indexed, structural code intelligence across the codebase with sub-millisecond AST-parsed lookups for surgical context and minimal token usage.

## Primary Usage

### 1. MCP Tool (`codegraph_explore`)
When the MCP tool is available, use `codegraph_explore` for any structural or navigation query instead of raw `grep`/`find` or manual file reading loops:
- Accepts natural language questions or symbol/file names (e.g. `"How does the authentication flow in api.py work?"`, `"get_db_session"`, `"super_admin_ui"`).
- Returns exact line-numbered source code snippets, caller/callee trees (including dynamic dispatch and callbacks), and dependent symbols.

### 2. CLI Command (`codegraph explore`)
In shell or subagent environments where MCP tools are deferred:
```bash
codegraph explore "<symbol or question>"
```

### 3. Key CLI Commands
- `codegraph init`: Initialize/rebuild `.codegraph/` index in current workspace.
- `codegraph status`: Display local graph index statistics.
- `codegraph install`: Configure CodeGraph MCP server across all installed AI coding agents.
- `codegraph upgrade`: Check and update CodeGraph CLI to latest release.

## Rules of Engagement
- **Reach for CodeGraph First**: On indexed repositories (containing `.codegraph/`), query CodeGraph before initiating manual multi-file reads or `grep` sweeps.
- **Trust Index Results**: CodeGraph results are generated from AST parses. Do not waste tokens re-verifying returned source with `grep`.
- **Staleness Handling**: Pay attention to staleness warnings (`⚠️ Some files referenced below were edited...`). Read only those specific pending files if indicated.
