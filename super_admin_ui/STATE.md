# Super Admin UI — Component State & Sync Ledger

> **Location**: `super_admin_ui/STATE.md`  
> **Last Updated**: 2026-08-06  
> **Scope**: Super Admin Vue 3 Frontend (`super_admin_ui`, Port 5173)

---

## 1. Views & Component Inventory

| View / Component | Path | Description & Features |
| :--- | :--- | :--- |
| **Dashboard** | `src/views/Dashboard.vue` | KPI stats cards, call volume breakdown graph, active tenant counts fetched dynamically. |
| **Tenants & Provisioning** | `src/views/Tenants.vue` | Tenant list table, status toggles, "+ New Tenant" modal with API key popup, **⚙️ Per-Tenant Agent Customization Modal**. |
| **Niches & Personas** | `src/views/Personas.vue` | Vertical agent persona templates CRUD, system prompt editor, **Fish Audio Discover voice selector**. |
| **Call Logs & Auto-QA** | `src/views/CallLogs.vue` | Completed calls table, quality score, sentiment tags, **4-Step Latency Waterfall Breakdown graph**, dual-channel transcript inspector. |
| **Tool Registry** | `src/views/ToolRegistry.vue` | Native built-in toolsets (`real_estate`, `car_rental`, `core`), **Custom HTTP Webhook tool creator**. |
| **Phone Numbers Router** | `src/views/PhoneNumbers.vue` | Maps inbound DID phone numbers directly to client tenants and persona templates. |
| **Agent Config** | `src/views/AgentConfig.vue` | Global default engine configuration (OpenRouter human-like models, Deepgram STT, Fish Audio TTS). |
| **WebRTC Simulator** | `src/components/SimulatorModal.vue` | In-browser WebRTC mic test playground with waveform animation & live transcript debug drawer. |

---

## 2. API Contracts & Endpoint Integration State

- **`GET /api/super/tenants`**: ✅ Connected (Fetches tenants list & status)
- **`POST /api/super/provision`**: ✅ Connected (Provisions tenant & displays raw API Key once)
- **`PATCH /api/super/tenants/{id}`**: ✅ Connected (Toggles active/suspended status)
- **`GET/PUT /api/super/tenants/{id}/config`**: ✅ Connected (Saves per-tenant system prompt, LLM model, temperature, voice ID, speaking rate, greeting)
- **`GET/POST/PUT/DELETE /api/super/personas`**: ✅ Connected (Manages niche persona templates)
- **`GET /api/super/fish-audio/voices`**: ✅ Connected (Browses live Fish Audio voice discovery options)
- **`POST /api/super/livekit/token`**: ✅ Connected (Generates WebRTC test room token for simulator)
- **`GET /api/super/calls`**: ✅ Connected (Fetches call recordings & latency metrics)
- **`GET/POST/DELETE /api/super/tools`**: ✅ Connected (Manages HTTP webhook tools)
- **`GET/POST/DELETE /api/super/phone-numbers`**: ✅ Connected (Maps DIDs to tenants)
- **`GET/POST /api/super/config/global_agent_config`**: ✅ Connected (Persists global engine defaults)

---

## 3. Synchronization Status & External Dependencies

- **Local State**: All Super Admin UI components are fully implemented and verified via Vite build (`npm run build`).
- **External Sync Status**:
  - Backend API (`api.py` / `telemetry.py`): **Synced**
  - Client Admin UI (`client_admin_ui`): **Unsynced / Pending User Approval** (Client Admin UI has not yet been updated with per-tenant agent customization views).
  - Agent Engine (`agent.py`): **Unsynced / Pending User Approval** (Agent worker needs to be updated to load `tenant_config` overrides upon call entrypoint).

> ⚠️ **Rule Note**: Changes to Super Admin UI are isolated to this component. Do NOT update other components until explicitly requested by the user.
