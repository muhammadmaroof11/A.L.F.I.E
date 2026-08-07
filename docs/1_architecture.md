# System Architecture

This document breaks down the mechanical structure of A.L.F.I.E. 

## The Triad Model

A.L.F.I.E. operates across three sovereign stacks:

1. **The Telephony Engine (LiveKit)**
   - Acts as the SIP gateway and WebRTC bridge. 
   - We do not use Twilio's proprietary webhooks for call audio. We map Twilio DIDs to our LiveKit SIP Ingress. LiveKit handles all real-time media streaming, maintaining sub-millisecond latencies critical for natural voice AI.
2. **The Intelligence Core (FastAPI / ARQ / Redis)**
   - The orchestration layer. It receives the SIP payload, connects to Deepgram (STT), pipes transcripts to OpenRouter (LLM), and streams text to Fish Audio (TTS). 
   - Background tasks (billing sweeps) run on ARQ workers backed by Redis.
3. **The Control Planes (Vue 3)**
   - **Super Admin (`super_admin_ui`):** Absolute control over the platform, tenants, personas, global configs, and call log auditing.
   - **Client Admin (`client_admin_ui`):** Isolated workspace for tenants to manage their multi-agent roster, view Chart.js analytics, and top-up credits via Stripe.

## Latency Waterfall

Our primary technical directive is maintaining conversational latency under 800ms.
1. **STT (Deepgram Nova 2):** Streams continuously. Finalizes transcript within ~150-200ms of utterance end.
2. **LLM (OpenRouter):** We use `stream=True`. TTFT (Time To First Token) is heavily monitored. We use Llama 3.3 70B for standard routing, falling back to Llama 3.1 8B for extreme speed if the system load spikes.
3. **TTS (Fish Audio):** We pipe the LLM stream directly into Fish Audio. Audio chunks begin playing before the LLM has finished generating the full sentence.
4. **Context Compression:** We use LLMLingua-2 to dynamically compress the conversation history before sending it to the LLM. This prevents token explosion on 20+ minute calls, keeping the KV cache small and inference lightning fast.

## Database Schema (PostgreSQL)

Strict relational integrity defines the state.
- `alfie_tenants`: The highest level abstraction. Holds billing, custom pricing limits, and subscription endpoints.
- `alfie_tenant_agents`: The individual agents a tenant deploys (e.g., Sales, Support). Maps to physical `alfie_phone_numbers`.
- `alfie_call_recordings`: Logs every interaction. Joined with `alfie_tenant_agents` for the Client Admin analytics dashboard.
- `alfie_credit_transactions`: The immutable ledger for Stripe top-ups and daily/monthly overage sweeps.
