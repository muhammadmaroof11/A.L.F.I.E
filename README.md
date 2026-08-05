# A.L.F.I.E Voice AI

A multi-tenant, multilingual voice AI agent tailored for Real Estate and Car Rental niches.
Powered by LiveKit, Deepgram, OpenRouter, Fish Audio, and MongoDB.

## Security Architecture

This platform implements a **Deanchor Ascended Security Architecture**:
1. **Docker Secrets:** API keys are injected via `/run/secrets/` avoiding `.env` leakage in images or logs.
2. **MongoDB 8.0:** Pinned database versions without zlib compression vulnerabilities.
3. **Tenant-Scoped DB Drivers:** All database queries are automatically scoped by `tenant_id` at the lowest driver level to prevent data contamination between clients.

## Local Setup

### 1. Initialize Secrets

Do not use `.env` files. Instead, create your secrets locally in the `secrets/` directory. These will be securely mounted into Docker.

```bash
mkdir -p secrets
echo -n "your_livekit_key" > secrets/livekit_api_key
echo -n "your_livekit_secret" > secrets/livekit_api_secret
echo -n "your_deepgram_key" > secrets/deepgram_api_key
echo -n "your_openrouter_key" > secrets/openrouter_api_key
echo -n "your_fish_audio_key" > secrets/fish_audio_api_key
```

### 2. Boot the Infrastructure

```bash
docker-compose up -d alfie-mongodb
```

### 3. Seed the Database

Before starting the agent, seed the database with the initial tenant configurations.

```bash
python seed_data.py
```

### 4. Start the Agent

```bash
docker-compose up -d alfie-agent
```

### 5. Setup Telephony (SIP Trunk)

Run the SIP script to programmatically configure your LiveKit Cloud project to accept SIP calls and route them to A.L.F.I.E.

```bash
python setup_sip.py
```
