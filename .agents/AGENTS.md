# Workspace Rules & Governance — A.L.F.I.E

This file specifies project-level rules that MUST be strictly followed by all AI agents working in this codebase.

---

## Rule 1: Continuous STATE.md Synchronization & Ledger Maintenance
- **State File Location:** `e:\Me\A.L.F.I.E\STATE.md`
- **Mandatory Action:** Whenever ANY architectural change, database schema update, API endpoint modification, or UI feature is added or edited in any component (`super_admin_ui`, `client_admin_ui`, `api.py`, `telemetry.py`, `agent.py`, `docker-compose.yml`, or `scripts/`), the agent MUST immediately update `STATE.md`.
- **Sync Tracking Requirement:** `STATE.md` must maintain the **Component State Matrix** and **Synchronization Ledger**, clearly demarcating which components are fully synced vs pending synchronization across the rest of the platform.

---

## Rule 2: Zero Secret Exposure & Security Hygiene
- **Strict Prohibition:** Never commit, print, log, or hardcode API keys, secrets, JWT signing secrets, or database passwords directly into any source code file, markdown file, or git history.
- **Secret Resolution:** All sensitive credentials MUST be loaded dynamically via environment variables (`.env`) or mounted Docker Secrets (`/run/secrets/` in production containers, or local `secrets/` directory in dev).
- **Inspection Rule:** Before finalizing any code changes or documentation updates, verify that no raw secrets or credentials are hardcoded into source files.

---

## Rule 3: Codebase Knowledge & Semantic Graph (CodeGraph)
- **CodeGraph Integration:** Use `codegraph_explore` (MCP tool) or `codegraph explore` (CLI) for any structural codebase analysis, call graph tracing, symbol lookups, or file-by-file exploration before resorting to raw `grep`/`find` or reading files directly.
- **Direct Answers:** `codegraph_explore` returns exact line-numbered source code, call dependencies, dynamic dispatch links, and blast-radius summaries in one call. Use it directly to answer code structure and flow questions.
- **Index Staleness:** If a response contains a staleness warning ("⚠️ Some files referenced below were edited..."), read those specific pending files directly. If `.codegraph/` is present at the repo root, CodeGraph is active and authoritative for indexed files.

---

## Rule 4: Fail-Fast & Transparent Reporting
- **Rule File:** `.agents/rules/fail-fast-inform.md`
- **Mandatory Action:** On the first failure of any tool, command, or approach, immediately inform the user with the exact error and alternatives. Never attempt silent workaround chains, run dozens of blind scripts, or fabricate unverified results.

---

## Rule 5: Prompt Enhancement, Skill Routing & Workflow Orchestration
- **Rule File:** `.agents/rules/prompt-orchestration.md`
- **Mandatory Action:** Automatically decompose every user prompt into its target stack layer, auto-activate matching skills (`interface-design`, `no-slop-ui`, `motion-framer`, `chrome-devtools`, `codegraph`, `deanchor`), dispatch relevant MCP tools (`context7`, `chrome-devtools-mcp`, `github`, `git`, `figma`), and follow the 5-phase execution lifecycle (Enhance → Explore → Execute → Verify → Sync STATE.md).
