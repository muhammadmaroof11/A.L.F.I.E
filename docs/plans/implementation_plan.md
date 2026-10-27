# A.L.F.I.E — Implementation Plan (Modular Architecture)

**Version**: 3.0 | **Date**: 2026-08-04 | **Status**: Approved

---

## Architecture: Modular Multi-Niche Platform

The codebase is organized into **platform core** (niche-agnostic) and **niche modules** (pluggable per vertical). See [data_model.md](data_model.md) for the full schema.

---

## Phase 1: Project Skeleton & Configuration

| File | Purpose |
|:-----|:--------|
| `.gitignore` | VCS exclusions |
| `.env` | Credential store (git-ignored) |
| `requirements.txt` | Pinned Python dependencies |
| `config.py` | Pydantic-based environment validation |

---

## Phase 2: Database Layer — Core + Niche Modules

| File | Purpose |
|:-----|:--------|
| `database.py` | Async MongoDB client (Motor), connection pooling, tenant-scoped query helpers |
| `models/core.py` | Pydantic models: `Tenant`, `AgentConfig`, `ToolRegistryEntry`, `Call`, `Transcript`, `Lead`, `Notification`, `AnalyticsEvent` |
| `models/real_estate.py` | Pydantic models: `Property`, `Neighborhood`, `REBooking` |
| `models/car_rental.py` | Pydantic models: `Vehicle`, `RentalLocation`, `CRReservation`, `InsurancePlan` |
| `seed_data.py` | Seed tenant configs, tool registries, sample properties, vehicles |

**Key patterns**:
- Single `AsyncIOMotorClient` in worker prewarm
- All queries scoped by `tenant_id` via helper: `db.scoped(collection, tenant_id)`
- All write operations as background tasks (non-blocking to voice pipeline)
- Compound indexes starting with `tenant_id` on every collection

---

## Phase 3: System Prompts — Per-Niche, Trilingual

| File | Purpose |
|:-----|:--------|
| `prompts/base.py` | Shared prompt fragments (language rules, formatting prohibitions, number rules) |
| `prompts/real_estate.py` | Real estate system prompt (property search, scheduling, mortgage) |
| `prompts/car_rental.py` | Car rental system prompt (reservations, insurance, fleet) |

**Runtime**: Prompt is loaded from `agent_configs.system_prompt` per tenant, not hardcoded.

**Shared prompt rules** (all niches):
- No markdown, bullets, asterisks, emojis
- Spoken numbers: "thirty five million rupees" not "35,000,000 PKR"
- Max 2 sentences per response turn
- Mirror caller's language (English/Urdu/Arabic)
- Cultural greetings for each language

---

## Phase 4: Tool Definitions — Registry + Implementations

| File | Purpose |
|:-----|:--------|
| `tools/registry.py` | `ToolRegistry` class — loads enabled tools from MongoDB per tenant |
| `tools/core.py` | Shared tools: `capture_lead`, `schedule_callback`, `transfer_to_human` |
| `tools/real_estate.py` | 8 tools: `search_properties`, `get_property_details`, `compare_properties`, `get_neighborhood_info`, `check_viewing_availability`, `book_viewing`, `calculate_mortgage`, `get_market_trends` |
| `tools/car_rental.py` | 12 tools: `search_vehicles`, `get_vehicle_details`, `check_availability`, `get_rental_quote`, `create_reservation`, `modify_reservation`, `cancel_reservation`, `get_insurance_plans`, `get_locations`, `check_driver_requirements`, `report_issue`, `extend_rental` |

**Tool registry flow**:
```python
# At call start:
registry = ToolRegistry(db, tenant_id)
active_tools = await registry.load_enabled_tools()
agent = Agent(instructions=config.system_prompt, tools=active_tools)
```

**Adding tools for a new niche**:
1. Create `tools/new_niche.py` with `@function_tool` definitions
2. Register in `TOOL_IMPLEMENTATIONS` map
3. Insert tool definitions into `tool_registry` collection for the tenant
4. No changes to `agent.py` or any core code

---

## Phase 5: Pipeline Orchestration

| File | Purpose |
|:-----|:--------|
| `agent.py` | AgentServer entrypoint — tenant identification, config loading, session wiring |

**Session lifecycle**:
1. `prewarm` → init MongoDB client, store in `proc.userdata`
2. Incoming call → SIP dispatch identifies `tenant_id` from room metadata
3. Load `agent_configs` from MongoDB for this tenant
4. Load `tool_registry` — get enabled tools
5. Construct pipeline from tenant config (STT, LLM, TTS, VAD)
6. `AgentSession.start()` with tenant-specific agent
7. `generate_reply()` — tenant-specific greeting
8. On disconnect → update call record, log metrics, webhook if needed

**Multi-tenant pipeline construction**:
```python
# Each tenant can have different providers/models
stt = build_stt(config.stt_config)      # Deepgram, or future alternative
llm = build_llm(config.llm_config)      # OpenRouter, OpenAI, or future
tts = build_tts(config.voice_config)    # Fish Audio, or future alternative
vad = build_vad(config.vad_config)      # Silero (always local)
```

---

## Phase 6: Telemetry & Notifications

| File | Purpose |
|:-----|:--------|
| `telemetry.py` | Event-based pipeline metrics, context window management |
| `notifications.py` | Webhook delivery with retry logic, tenant-scoped |

**Metrics captured**: STT latency, LLM TTFT, TTS TTFA, token usage, call duration, tool execution times
**Notification delivery**: POST with 3 retries, exponential backoff, logged to `notifications` collection

---

## Phase 7: Deployment — Docker

| File | Purpose |
|:-----|:--------|
| `Dockerfile` | Python 3.11 slim agent image |
| `docker-compose.yml` | `alfie-agent` + `alfie-mongodb` containers |
| `setup_sip.py` | LiveKit SIP dispatch rule setup (per tenant) |
| `README.md` | Documentation & quickstart |

---

## Updated Directory Structure

```
e:\Me\A.L.F.I.E\
├── agent.py                  # AgentServer entrypoint
├── config.py                 # Pydantic environment validation
├── database.py               # Async MongoDB client + tenant-scoped helpers
├── telemetry.py              # Pipeline metrics
├── notifications.py          # Webhook delivery + retries
├── setup_sip.py              # LiveKit SIP dispatch setup
├── seed_data.py              # Sample data seeder
│
├── models/                   # Pydantic document schemas
│   ├── __init__.py
│   ├── core.py               # Tenant, Call, Transcript, Lead, etc.
│   ├── real_estate.py        # Property, Neighborhood, REBooking
│   └── car_rental.py         # Vehicle, Location, Reservation, Insurance
│
├── prompts/                  # System prompts (loaded per tenant)
│   ├── __init__.py
│   ├── base.py               # Shared prompt fragments
│   ├── real_estate.py        # RE-specific instructions
│   └── car_rental.py         # CR-specific instructions
│
├── tools/                    # @function_tool definitions
│   ├── __init__.py
│   ├── registry.py           # Dynamic tool loading from MongoDB
│   ├── core.py               # Shared: capture_lead, transfer_to_human
│   ├── real_estate.py        # 8 RE tools
│   └── car_rental.py         # 12 CR tools
│
├── plans/                    # Architecture & planning docs
│   ├── architecture.md
│   ├── implementation_plan.md
│   ├── data_model.md
│   └── risks_and_costs.md
│
├── docs/                     # Technical reference
│   ├── tech_stack.md
│   ├── api_reference.md
│   └── prompt_engineering.md
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── .gitignore
├── PENDING_FROM_USER.md
└── README.md
```

---

## Verification Plan

### Automated
```bash
docker compose up --build -d
docker exec alfie-mongodb mongosh --eval "db.runCommand({ping:1})"
docker exec alfie-agent python seed_data.py
docker logs alfie-agent --tail 50
```

### Manual — Real Estate Tenant
| Test | Expected |
|:-----|:---------|
| Dial phone number | Agent greets in English (per tenant config) |
| Speak Urdu | Agent responds in Urdu |
| "3 bedroom in DHA" | Queries `properties`, returns top 3 |
| "Compare first two" | Side-by-side comparison |
| "Tell me about the neighborhood" | School ratings, safety, amenities |
| "Book viewing tomorrow 2PM" | Creates booking, sends webhook |
| "What would mortgage look like?" | Calculates monthly payment |

### Manual — Car Rental Tenant
| Test | Expected |
|:-----|:---------|
| "I need a car for Friday to Monday" | Searches `vehicles`, returns available |
| "What's the total with insurance?" | Itemized quote with extras |
| "Book it" | Creates reservation, sends webhook |
| "Can I extend until Wednesday?" | Extends rental, recalculates cost |
| "I had a flat tire" | Logs issue, escalates if urgent |
