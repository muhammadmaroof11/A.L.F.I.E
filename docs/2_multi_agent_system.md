# Multi-Agent Routing & SIP Dynamics

A.L.F.I.E. is not a single-bot system. A single tenant can deploy an entire virtual workforce. 

## The Multi-Agent Roster
Instead of mapping one phone number to a generic "Tenant AI", we map Twilio DIDs to specific `agent_id`s within a tenant workspace. 
- **Sales Agent (Agent A):** Aggressive prompt, high energy Fish Audio Voice ID.
- **Support Agent (Agent B):** Empathetic prompt, calm Voice ID.
- **Billing Agent (Agent C):** Highly analytical prompt, no-nonsense Voice ID.

## Internal SIP Transfers (The Handoff)

We do not use Twilio to transfer calls between agents. Routing a call back out through Twilio and back in costs double the PSTN rates.

Instead, we use native **LiveKit SIP Handoffs**:
1. When Agent A connects to a caller, the backend injects the roster of all other agents belonging to the same tenant into Agent A's system prompt context.
2. If the caller says "I need to talk to support", the LLM triggers the `transfer_to_department` tool.
3. The tool executes a native LiveKit `transfer_sip_participant` command, issuing a SIP REFER header.
4. The call is instantly bridged to Agent B without ever leaving our WebRTC infrastructure.

## Contextual Persistence
During a SIP handoff, the conversation history is passed through Redis using the caller's unique SIP Call ID. When Agent B picks up the line, they instantly know who they are talking to and what Agent A already discussed, preventing the user from repeating themselves.
