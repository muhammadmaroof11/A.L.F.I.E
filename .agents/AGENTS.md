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

## Rule 4: Cross-Device Agent Sync (`.sync/` Folder)
- **Sync Folder Location:** `.sync/` in the project root (committed to Git).
- **Mandatory First Action:** At the start of ANY new session, the agent MUST read `.sync/HANDOFF.md` to understand what the previous agent (on any device) was doing, what's in progress, and what's next.
- **Mandatory Last Action:** Before the user switches devices or ends a significant work session, update `.sync/HANDOFF.md` with current progress, blockers, and next steps.
- **Task Tracking:** `.sync/TASKS.md` is the single source of truth for project progress. Update it as tasks are completed.
- **Decision Log:** `.sync/DECISIONS.md` contains all resolved decisions. Never re-ask a question that's already answered there. Add new decisions as they are made.
- **Device Routing:** Read `.sync/DEVICES.md` to understand hardware capabilities. Route GPU-heavy tasks (Blender, model generation) to the Office Desktop.
