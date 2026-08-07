# A.L.F.I.E. — Sovereign AI Telephony Engine

> **Notice:** This is not a toy chatbot. A.L.F.I.E. is a weaponized, multi-tenant voice AI infrastructure designed to handle concurrent SIP trunking, dynamic agent routing, and sub-millisecond audio streaming across high-stakes verticals like Real Estate and Car Rentals.

---

## ⚡ The Core Architecture

A.L.F.I.E. bypasses traditional high-latency telephony APIs by maintaining native WebRTC and SIP bridges via **LiveKit**. 

### The Triad Pipeline
- **STT (Ear):** Deepgram Nova 2 Streaming (WebSocket). Lowest latency possible.
- **LLM (Brain):** OpenRouter Gateway. We dynamically route to Llama 3.3 70B, GPT-4o, or Claude 3.5 Sonnet depending on the configured Persona. We use **LLMLingua-2** for aggressive context compression during long-running calls to prevent token-bloat memory exhaustion.
- **TTS (Voice):** Fish Audio Engine. Real-time synthesized responses via their streaming API, fully integrated with their Discover registry for instant Voice ID cloning.

---

## 🏗️ The Infrastructure

The platform is split into three sovereign domains:

### 1. The Core Engine (FastAPI + PostgreSQL + ARQ)
The central nervous system. Written in Python/FastAPI, it handles WebRTC signaling, WebSocket telemetry, and REST endpoints.
- **Background Workers (`worker.py`):** Powered by Redis and ARQ. Handles the `arq.cron` monthly subscription sweeper, slicing base prices, calculating overages, and resetting included minute balances at midnight.
- **Database (`telemetry.py`):** PostgreSQL 15. Strict relational integrity across `alfie_tenants`, `alfie_personas`, `alfie_tenant_agents`, and `alfie_credit_transactions`.

### 2. The Command Center (Super Admin UI — Vue 3)
The omniscient dashboard for the platform owner (Port `5173`).
- **Tenant Provisioning:** Spin up new isolated workspaces, inject API keys, and set hard credit limits.
- **Billing Overrides:** Bypass standard pricing tiers. Hardcode custom monthly prices, custom included minutes, and custom per-minute overage rates on a per-tenant basis.
- **Persona Engineering:** Edit system prompts, define Webhook toolsets, and assign Fish Audio Voice IDs.
- **Call Auditing:** Real-time WebSocket dual-channel transcript inspector and 4-step latency waterfall graphs for absolute QA.

### 3. The Client Portal (Client Admin UI — Vue 3)
The isolated workspace for your tenants (Port `5174`).
- **Multi-Agent Roster:** Tenants don't just get one agent. They can configure Sales, Support, and Reporting agents, each mapped to a distinct Twilio DID.
- **LiveKit SIP Handoffs:** The system allows agents to dynamically transfer active calls to other agents/departments *internally* using native LiveKit `transfer_sip_participant` headers. No PSTN hairpinning. No Twilio transfer fees.
- **Per-Agent Analytics:** Dashboard powered by Chart.js. See exactly which agent handled how many calls, minutes consumed, and credits burned.
- **Self-Serve Top-ups:** Integrated Stripe Checkout workflows for voucher top-ups when their included minutes run dry.

---

## 🚀 Ignition Sequence

You need Docker, Python 3.11, and valid API keys. Stop running raw scripts and containerize.

```bash
# 1. Clone & Env
cp .env.example .env
# Populate LIVEKIT, OPENROUTER, DEEPGRAM, FISH_AUDIO, TWILIO, and STRIPE keys in .env.

# 2. Spin up the persistence layer
docker-compose up -d postgres redis n8n

# 3. Boot the API and Worker
uvicorn api:app --host 0.0.0.0 --port 8000
arq worker.WorkerSettings

# 4. Spin up the Frontends
cd super_admin_ui && npm run dev
cd ../client_admin_ui && npm run dev
```

> [!CAUTION]
> **Strict Prerequisite:** A.L.F.I.E requires a `.env` file populated with your Stripe, Twilio, LiveKit, and LLM provider keys. The backend will halt if it detects missing foundational secrets. See `requirements_from_user.md` for exact instructions.

---

## 🧠 Tool Registry & Event Webhooks

A.L.F.I.E. agents aren't blind. They execute tools. 
The Super Admin UI allows you to register **Custom HTTP Webhooks**. If an agent determines they need to book an appointment, they invoke the webhook. We pipe this into our integrated **n8n** instance (`http://n8n:5678/webhook/alfie-events`) or a Twenty CRM instance to execute real-world mutations based on the conversation intent.
