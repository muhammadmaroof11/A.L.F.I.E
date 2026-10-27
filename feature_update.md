# A.L.F.I.E. — Feature Roadmap & Unimplemented Proposals Ledger
**Automated Listening & Fluency Intelligence Engine**  
**Document Status:** Production Backlog & Engineering Roadmap  
**Scope:** Core Telephony, Distributed Architecture, CRM Integrations, Billing, FDA SaMD / HIPAA Safeguards, and Testing

---

## Executive Overview
This document tracks all finalized architectural specifications, domain capabilities, regulatory controls, and product features identified and approved during project proposals, business plans, and system engineering audits that are scheduled for implementation in upcoming release cycles.

---

## 1. Telephony, Voice Mesh & Real-Time Media

### 1.1 Live PSTN Phone Number Auto-Provisioning (Twilio / Telnyx)
- **Status:** Finalized in Proposal / Pending Production API Wiring
- **Specification:**
  - Automated search, reservation, and purchase of local and toll-free Direct Inward Dialing (DID) numbers across US, UK, and GCC jurisdictions via Telnyx and Twilio REST APIs.
  - Automated submission and tracking of regional regulatory bundles (e.g., local address requirements, identity verification for international numbers).
  - Automatic E.164 normalization, carrier SIP trunk origination binding, and LiveKit dispatch rule configuration upon purchase.

### 1.2 Native WebRTC Supervisor Live Audio Stream
- **Status:** Finalized in Inbound Enterprise Plan / UI Integration Pending
- **Specification:**
  - Replace the HTML5 `<audio>` placeholder stub in `client_admin_ui/src/composables/useLiveCallAudio.js` with full `livekit-client` `Room` media subscription.
  - Establish bidirectional WebRTC audio tracks so supervisors can listen in real-time to active calls and stream microphone audio during 1-Click Human Takeover.
  - Add audio ducking: smoothly mute or attenuate AI agent voice audio when supervisor takeover is engaged.

### 1.3 Multimodal Multi-Language Voice Pipelines
- **Status:** Finalized in Proposal / Architecture Defined
- **Specification:**
  - Expand speech pipeline beyond English to support Spanish (US market) and Bilingual English/Arabic (GCC / Gulf markets: UAE, Saudi Arabia, Qatar).
  - Implement real-time automatic speech language identification (LID) within Deepgram / Whisper streaming layers to dynamically adapt prompt context and TTS voice models.
  - Regional accent calibration and localized colloquial phrase dictionaries for medical and legal verticals.

### 1.4 Self-Hosted / Clustered LiveKit Media Server Ingress
- **Status:** Finalized in Architecture Plan / Docker Deployment Pending
- **Specification:**
  - Add self-hosted LiveKit SFU (Selective Forwarding Unit) container configuration to root `docker-compose.yml` to remove external cloud SFU dependency for on-premise or sovereign enterprise deployments.
  - Configure Redis-backed LiveKit distributed room routing and turn/stun server allocation for multi-node clusters.

---

## 2. Distributed Core, Concurrency & High Availability

### 2.1 Redis Pub/Sub WebSocket Architecture for Live Telemetry
- **Status:** Finalized in System Design Audit / Pending Refactor
- **Specification:**
  - Refactor `ConnectionManager` in `backend/api.py` from a single-process in-memory connection list to a Redis Pub/Sub subscription model (`telemetry:events` and `telemetry:live:{tenant_id}`).
  - Enable seamless horizontal scaling across multiple Uvicorn worker containers behind Caddy / Nginx reverse proxies without dropped telemetry frames or split-brain socket states.

### 2.2 Atomic Multi-Step Financial & Billing Transactions
- **Status:** Finalized in Engineering Audit / Implementation Pending
- **Specification:**
  - Enforce strict PostgreSQL transactional boundaries (`async with conn.transaction()`) across `backend/routes/billing_routes.py`, `backend/routes/super_admin_routes.py`, and `backend/worker.py`.
  - Atomically bind tenant credit deductions, rate-card overage computations, and ledger transaction insertions to eliminate race conditions under concurrent call volume.

### 2.3 In-Flight LLM Gateway Fallback Retry
- **Status:** Finalized in Architecture Audit / Implementation Pending
- **Specification:**
  - Update `CachedOpenAILLM` in `backend/pipeline/audio_engine.py` to implement instant, in-flight retry logic against direct OpenRouter or Groq endpoints upon receiving HTTP 5xx or connection timeouts from the local LiteLLM proxy container during an active conversation turn.

### 2.4 Structured Warning Logging for Background Tasks
- **Status:** Finalized in Reliability Audit / Implementation Pending
- **Specification:**
  - Audit and replace bare `except Exception: pass` blocks in `backend/pipeline/context_factory.py`, `backend/cache/prompt_cache.py`, and `backend/telemetry.py` with structured JSON warning logs containing contextual error tags and telemetry counters.

---

## 3. Billing, Payments & Client Self-Service

### 3.1 Production Stripe Payment Gateway Integration
- **Status:** Test Mode Configured / Production Gateway Pending
- **Specification:**
  - Complete live Stripe webhook event processing (`invoice.payment_succeeded`, `customer.subscription.deleted`, `payment_intent.failed`) in `backend/routes/billing_routes.py`.
  - Integrate Stripe Customer Portal redirect for self-serve payment method updates, invoice history downloads, and tier modifications.
  - Automated PDF receipt generation and email dispatch for recurring subscription renewals.

### 3.2 Usage Quotas & Automated Top-Up Rules
- **Status:** Finalized in Business Specification / Implementation Pending
- **Specification:**
  - Automatic low-balance SMS and email warning triggers when a tenant's credit balance drops below 15% of their monthly allocation.
  - Client-configurable auto-recharge settings (e.g., automatically purchase 500 minutes when balance drops below 50 minutes).
  - Rate card customizer supporting per-second vs. per-minute rounding rules per tenant.

---

## 4. CRM, Calendar & Omnichannel Integrations

### 4.1 Production CRM Bidirectional Sync Adapters
- **Status:** Schema Defined / API Client Wiring Pending
- **Specification:**
  - Complete live OAuth2 token lifecycle management and automatic token refresh for HubSpot, Salesforce, GoHighLevel, and Twenty CRM.
  - Bidirectional field synchronization: push qualified lead slots (budget, timeline, case details) from call sessions into CRM custom objects; pull existing contact history during inbound caller identification.

### 4.2 Live Calendar Availability & Booking (Cal.com / Google / Outlook)
- **Status:** Core Tool Structure Built / Live OAuth Flow Pending
- **Specification:**
  - Direct integration with Cal.com, Google Calendar API, and Microsoft 365 Outlook Calendar for real-time slot checking, double-booking prevention, and instant booking confirmation.
  - Automated calendar invite (.ics) dispatch to caller's email and SMS confirmation with reschedule link.

### 4.3 Post-Call Multi-Channel Automations
- **Status:** Finalized in GTM Plan / Integration Pending
- **Specification:**
  - Outbound WhatsApp Business API adapter for instant post-call summary, brochure PDF link, or digital retainer delivery.
  - Configurable SMS follow-up templates triggered by pathway terminal nodes or QA conversion tags.

---

## 5. Healthcare, FDA SaMD & Security Compliance

### 5.1 Deterministic Emergency Triage Circuit Breaker (IEC 62304 Class C)
- **Status:** Identified in FDA Audit / Safety Engineering Pending
- **Specification:**
  - Implement a programmatic, non-overridable emergency keyword parser (`EmergencyTriageEngine`) running prior to and alongside LLM turns.
  - Intercept acute clinical red flags ("chest pain", "shortness of breath", "uncontrolled bleeding", "stroke symptoms", "loss of consciousness").
  - Immediately bypass LLM generation, deliver a deterministic emergency directive ("Please hang up and dial 911 immediately"), and trigger emergency SIP transfer or SMS alert to clinic staff.

### 5.2 Zero-PHI Application Logging & Field-Level Encryption (HIPAA)
- **Status:** Identified in Regulatory Audit / Security Hardening Pending
- **Specification:**
  - Implement a PII/PHI redaction filter in `backend/logging_config.py` ensuring patient names, phone numbers, and dates of birth are anonymized before output to stdout and Loki ingestion.
  - Implement Application-Level Field Encryption (AES-256 GCM) for sensitive clinical columns in PostgreSQL (`patient_name`, `patient_phone`, `patient_dob`, `reason_for_visit`).
  - Enforce AWS KMS server-side encryption (`x-amz-server-side-encryption: aws:kms`) for all call recordings stored in the S3/R2 audio vault.
  - Enable authentication and TLS on Grafana Loki observability endpoints.

### 5.3 Cryptographic 21 CFR Part 11 Append-Only Audit Ledger
- **Status:** Identified in FDA Audit / Compliance Engineering Pending
- **Specification:**
  - Create a tamper-evident audit ledger table `alfie_audit_ledger` in PostgreSQL with row-level immutability triggers.
  - Compute a cryptographic SHA-256 Merkle chain linking each clinical or administrative event to the previous record hash:
    $$\text{Hash}_n = \text{SHA256}(\text{Hash}_{n-1} \parallel \text{Timestamp} \parallel \text{ActorID} \parallel \text{Action} \parallel \text{PayloadHash})$$

### 5.4 AI Model Governance & Versioning Ledger
- **Status:** Identified in FDA Audit / Traceability Pending
- **Specification:**
  - Implement an immutable prompt versioning table (`alfie_prompt_versions`) storing prompt text, semantic version, and SHA-256 digest.
  - Log complete reproducibility metadata with every call session in `alfie_telemetry`: prompt version hash, exact LLM snapshot checkpoint ID, temperature, top-p, random seed, and retrieved knowledge context IDs.

---

## 6. Testing, CI/CD & Deployment

### 6.1 End-to-End Synthetic Voice Call Test Suite
- **Status:** Unit Tests Active (303 Tests) / E2E Audio Pipeline Pending
- **Specification:**
  - Build an automated integration test harness using LiveKit's test mode that simulates incoming audio streams, asserts on VAD triggering, STT transcript generation, LLM turn processing, tool execution, and TTS chunk delivery.

### 6.2 GitHub Actions CI/CD Pipeline
- **Status:** Local Configuration Active / Cloud CI Matrix Pending
- **Specification:**
  - Automated pull request workflow executing `pytest`, linting (`ruff`, `eslint`), security secret scanning (`trufflehog`), and multi-arch Docker image builds (`linux/amd64`, `linux/arm64`).

### 6.3 Kubernetes Production Orchestration Manifests
- **Status:** Docker Compose Production Ready / K8s Manifests Pending
- **Specification:**
  - Production Helm charts, Kubernetes Deployments, Services, Horizontal Pod Autoscalers (HPA), and ingress controller configurations for enterprise high-availability deployments.
