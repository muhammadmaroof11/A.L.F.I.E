# A.L.F.I.E — System Architecture

**Version**: 3.0 | **Date**: 2026-08-04

---

## 1. System Overview

A.L.F.I.E (Autonomous LiveKit Framework for Intelligent Engagement) is a **multi-tenant, multi-niche** voice AI telephony platform. Each client (tenant) gets a fully configured, niche-specific voice agent — with its own phone number, system prompt, voice personality, and tool set — running on a shared platform core.

**Core Engine**: LiveKit Agents Python SDK (≥1.6)
**Languages**: English, Urdu, Arabic (per-tenant configurable)
**Active Niches**: Real Estate, Car Rental
**Architecture**: Modular — new verticals plug in without touching core code

### Key Architectural Principles

| Principle | How It's Applied |
|:----------|:-----------------|
| **Tenant isolation** | Every document carries `tenant_id`; queries are always scoped |
| **Niche modularity** | Tools, prompts, and data collections are organized per-vertical |
| **Dynamic tool loading** | Agent constructs its tool set at call start from `tool_registry` |
| **Provider flexibility** | STT, LLM, TTS providers configurable per-tenant in `agent_configs` |
| **Zero-downtime niche addition** | New vertical = new collections + tool implementations + registry entries |

---

## 2. High-Level Architecture

```mermaid
graph TB
    subgraph "PSTN / Telephony"
        Phone["📞 Caller (PSTN)"]
    end

    subgraph "LiveKit Cloud (Free Tier)"
        NativeNum["Native US Phone Number"]
        Gateway["SIP Gateway"]
        Dispatch["SIP Dispatch Rule"]
        Room["LiveKit Room (alfie-call-{uuid})"]
    end

    subgraph "Docker: A.L.F.I.E Stack"
        subgraph "agent-worker container"
            Server["AgentServer"]
            Session["AgentSession"]
            
            subgraph "Voice Pipeline"
                VAD["Silero VAD (local ONNX)"]
                STT["Deepgram Nova-3 STT (multilingual)"]
                LLM["LLM via OpenRouter"]
                TTS["Fish Audio TTS (s2.1-pro)"]
            end
            
            subgraph "Agent Logic"
                Agent["Agent (instructions + tools)"]
                LangDetect["Language Detector"]
                ToolSet["Real Estate Tools"]
                CtxMgr["Chat Context Manager"]
            end
            
            Telemetry["Telemetry & Metrics"]
            DBClient["Motor (async MongoDB client)"]
        end

        subgraph "mongodb container"
            MongoDB[("MongoDB 7.0")]
            Collections["Collections:\n• calls\n• transcripts\n• properties\n• bookings\n• leads"]
        end
    end

    subgraph "External APIs"
        DeepgramAPI["Deepgram API"]
        OpenRouterAPI["OpenRouter API"]
        FishAudioAPI["Fish Audio API"]
    end

    subgraph "Admin Notification"
        Webhook["Webhook Endpoint"]
        AdminApp["Admin App / Mobile Notification"]
    end

    Phone -->|"Dial number"| NativeNum
    NativeNum --> Gateway
    Gateway --> Dispatch
    Dispatch -->|"Create room + dispatch agent"| Room
    Room <-->|"WebRTC Audio"| Session

    Session --> VAD
    VAD --> STT
    STT --> LangDetect
    LangDetect --> LLM
    LLM --> TTS
    TTS --> Session
    
    LLM <-->|"Tool calls"| ToolSet
    ToolSet <-->|"CRUD"| DBClient
    DBClient <--> MongoDB
    
    STT <-->|"WebSocket"| DeepgramAPI
    LLM <-->|"HTTPS"| OpenRouterAPI
    TTS <-->|"WebSocket"| FishAudioAPI
    
    ToolSet -->|"POST /notify"| Webhook
    Webhook --> AdminApp
```

---

## 3. Voice Pipeline — Per-Turn Data Flow

```
Caller Audio → [Silero VAD] → Speech Segment
                                    ↓
                            [Deepgram Nova-3]
                          (language="multi")
                                    ↓
                        Transcript + Language Code
                                    ↓
                     [Language-Aware Prompt Selection]
                                    ↓
                        [OpenRouter LLM (Llama 3.3)]
                      system prompt + chat history
                                    ↓
                          ┌─────────┴─────────┐
                          │                   │
                    Direct Response      Tool Call
                          │            (@function_tool)
                          │                   │
                          │           Execute + DB ops
                          │                   │
                          └─────────┬─────────┘
                                    ↓
                        [Fish Audio TTS (s2.1-pro)]
                        (auto language detection)
                                    ↓
                          Audio Frames → Caller
```

---

## 4. Call Lifecycle

```mermaid
sequenceDiagram
    participant Caller as 📞 Caller
    participant LK as LiveKit Cloud
    participant Agent as A.L.F.I.E
    participant STT as Deepgram
    participant LLM as OpenRouter
    participant TTS as Fish Audio
    participant DB as MongoDB

    Caller->>LK: Dial native phone number
    LK->>LK: SIP Dispatch → create Room
    LK->>Agent: JobContext dispatched
    Agent->>LK: ctx.connect()
    Agent->>DB: Create call record (status: active)
    Agent->>TTS: generate_reply("Greet caller")
    TTS-->>Caller: "Hello! How can I help you today?"

    loop Conversation Turn
        Caller->>Agent: Speech audio
        Agent->>Agent: VAD → end of turn
        Agent->>STT: Audio segment
        STT-->>Agent: Transcript + detected language
        Agent->>Agent: Switch prompt language if needed
        Agent->>LLM: [system prompt + history + transcript]

        alt Tool Call: search_properties
            LLM-->>Agent: search_properties(bedrooms=3, city="Islamabad")
            Agent->>DB: Query properties collection
            DB-->>Agent: Matching listings
            Agent->>LLM: Tool result with property details
            LLM-->>Agent: "I found two properties that match..."
        else Tool Call: book_viewing
            LLM-->>Agent: book_viewing(property_id, date, time)
            Agent->>DB: Insert booking record
            Agent->>Agent: POST webhook → admin notification
            LLM-->>Agent: "Your viewing is booked for..."
        end

        Agent->>TTS: Response text
        TTS-->>Caller: Synthesized speech
        Agent->>DB: Append turn to transcript
    end

    Caller->>LK: Hang up
    LK->>Agent: Room disconnected
    Agent->>DB: Update call record (status: completed, duration)
```

---

## 5. Interruption (Barge-In) Flow

```mermaid
sequenceDiagram
    participant Caller as 📞 Caller
    participant VAD as Silero VAD
    participant Session as AgentSession
    participant TTS as TTS Playback

    Note over TTS: Agent speaking: "The property at Bahria Town has—"
    Caller->>VAD: [Interruption detected]
    VAD->>Session: UserStartedSpeaking
    Session->>TTS: ⚡ FLUSH audio buffer
    TTS-->>TTS: Stop immediately
    Note over Session: Switches to listening
    Caller->>Session: "What about DHA instead?"
    VAD->>Session: UserStoppedSpeaking (600ms silence)
    Session->>Session: New turn → STT → LLM → TTS
```

---

## 6. Language Detection & Switching

```mermaid
flowchart LR
    Audio["Caller Audio"] --> STT["Deepgram Nova-3\n(language=multi)"]
    STT --> Detect{"Detected\nLanguage?"}
    
    Detect -->|"en"| EN["English System Prompt\n+ English TTS voice"]
    Detect -->|"ur"| UR["Urdu System Prompt\n+ Urdu TTS voice"]
    Detect -->|"ar"| AR["Arabic System Prompt\n+ Arabic TTS voice"]
    
    EN --> LLM["LLM (responds in detected language)"]
    UR --> LLM
    AR --> LLM
    LLM --> TTS["Fish Audio s2.1-pro\n(auto language detection)"]
```

**Strategy**:
- Deepgram Nova-3 with `language="multi"` auto-detects per utterance
- System prompt instructs LLM to mirror the caller's language
- Fish Audio s2.1-pro has built-in auto-detection (83 languages)
- No manual language switching required

---

## 7. Booking & Admin Notification Flow

```mermaid
sequenceDiagram
    participant Agent as A.L.F.I.E
    participant DB as MongoDB
    participant Hook as Webhook
    participant Admin as Admin App

    Agent->>DB: Query available time slots
    DB-->>Agent: Available: Tomorrow 2PM, 4PM
    Agent-->>Agent: Tell caller available slots

    Note over Agent: Caller chooses 2PM

    Agent->>DB: Insert booking (property_id, date, 2PM)
    Agent->>DB: Upsert lead (name, phone, email, interests)
    Agent->>DB: Update call transcript
    Agent->>Hook: POST /api/notifications/new-booking
    Hook->>Admin: Push notification
    Admin-->>Admin: "New viewing booked: 3BR in DHA Phase 5, Tomorrow 2:00 PM"
    Agent-->>Agent: Confirm to caller
```

---

## 8. Docker Deployment Topology

```mermaid
graph LR
    subgraph "Docker Host"
        subgraph "alfie-agent"
            PY["Python 3.11"]
            AG["agent.py"]
            MO["Motor Client"]
        end
        
        subgraph "alfie-mongodb"
            DB[("MongoDB 7.0")]
            VOL["mongo_data volume"]
        end
        
        MO -->|"mongodb://mongodb:27017"| DB
        DB --> VOL
    end
    
    AG <-->|"wss://"| LK["LiveKit Cloud"]
    AG <-->|"wss://"| DG["Deepgram API"]
    AG <-->|"https://"| OR["OpenRouter API"]
    AG <-->|"wss://"| FA["Fish Audio API"]
    AG -->|"POST"| WH["Admin Webhook"]
```

---

## 9. Technology Stack

| Layer | Provider | Model / Config | Protocol |
|:------|:---------|:---------------|:---------|
| **Transport** | LiveKit Cloud | Native phone + WebRTC | WebRTC / SIP |
| **VAD** | Silero | ONNX local model | Local inference |
| **STT** | Deepgram | Nova-3 (multi-language) | WebSocket |
| **LLM** | OpenRouter | llama-3.3-70b-instruct:free | HTTPS |
| **TTS** | Fish Audio | s2.1-pro (auto-detect) | WebSocket |
| **Database** | MongoDB | 7.0 (Docker) | TCP |
| **Deployment** | Docker Compose | Multi-container | — |
