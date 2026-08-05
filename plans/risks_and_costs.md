# A.L.F.I.E — Risk Matrix & Cost Estimation

**Date**: 2026-08-04

---

## Risk Matrix

| # | Risk | Impact | Probability | Mitigation |
|:--|:-----|:-------|:------------|:-----------|
| 1 | OpenRouter free-tier rate limit (20 req/min) | Calls fail on rapid exchanges | Medium | Exponential backoff + filler phrases; upgrade to paid if needed |
| 2 | Urdu STT accuracy for Roman Urdu / code-switching | Misrecognition | Medium | Use Deepgram `keyterm` for domain vocab; test with real callers |
| 3 | Fish Audio Urdu TTS quality | Unnatural prosody | Low | Test multiple stock voices; fall back to English if quality insufficient |
| 4 | MongoDB write latency blocking voice pipeline | Delayed TTS playback | Low | All DB writes as background tasks via `asyncio.create_task()` |
| 5 | LiveKit free tier exhaustion (50 min/mo) | No more inbound calls | High (during dev) | Monitor usage; upgrade to Ship plan ($50/mo) when ready |
| 6 | Admin webhook endpoint not running | Notifications lost silently | Medium | Log webhook failures; implement retry queue in `database.py` |
| 7 | LLM context window overflow on long calls | TTFT inflation, degraded responses | Medium | Sliding window pruning; summarize older turns |
| 8 | SIP Dispatch Rule misconfiguration | Calls connect but agent never joins | Low | Verify `agent_name` matches; test with LiveKit CLI |

---

## Cost Estimation

### Development / Prototype Phase (100 calls × 3 min average)

| Service | Unit Cost | Estimated Usage | Monthly Cost |
|:--------|:----------|:----------------|:-------------|
| LiveKit Cloud (Build plan) | Free (50 min/mo) | 300 min (exceeds free) | $0 (first 16 calls free) |
| Deepgram Nova-3 | $0.0043/min | 300 min | ~$1.29 |
| OpenRouter (free models) | $0.00 | 1000 req/day limit | $0.00 |
| Fish Audio s2.1-pro | ~$0.01/1K chars | ~150K chars | ~$1.50 |
| MongoDB (Docker self-hosted) | $0.00 | — | $0.00 |
| **Total** | | | **~$2.79** |

### Scaling Milestones

| Milestone | Action | Added Cost |
|:----------|:-------|:-----------|
| 16+ calls/mo | Upgrade LiveKit to Ship plan | +$50/mo |
| 50+ req/min LLM | Switch OpenRouter to paid tier | ~$0.50/M tokens |
| 1000+ calls/mo | Consider Deepgram Enterprise | Custom pricing |
| Production launch | MongoDB Atlas (M10+) | ~$57/mo |
